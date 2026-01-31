#!/usr/bin/env python3
"""
端到端测试脚本

功能：
- 从每个新闻源只抓取1条最新数据
- 走完完整流程：抓取 -> 去重 -> 翻译 -> AI评论 -> 评分 -> 生成HTML -> 更新首页
- 用于测试系统完整性和API调用

用法：
    python3 test_e2e.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
from collections import defaultdict

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.database import DatabaseManager
from src.scraper import fetch_all_sources
from src.translator import translate_articles
from src.html_generator import HTMLGenerator
from src.index_updater import IndexUpdater


def select_top_news(articles: list, top_n: int = 20) -> list:
    """
    筛选新闻（按源分组轮询方案）

    新逻辑（方案 A）：
    1. 先从每个源取 2 条最新新闻（确保每个源都有展示）
    2. 从剩余新闻中按时间排序补充，直到凑够足够数量的候选
    3. 按源分组轮询排列（彭博社→Yahoo→MarketWatch→...循环）
    """
    from collections import defaultdict

    # ========== 第一阶段：源配额（每个源至少 2 条）==========
    # 按源分组
    source_articles = defaultdict(list)
    for article in articles:
        source_articles[article.source].append(article)

    # 为每个源选择 2 条最新新闻
    quota_articles = []
    remaining_articles = []

    for source, source_list in source_articles.items():
        # 按发布时间倒序排序
        source_list.sort(key=lambda x: x.publish_time, reverse=True)

        # 取前 2 条进入配额池
        quota_articles.extend(source_list[:2])

        # 剩余的进入候选池
        remaining_articles.extend(source_list[2:])

    # ========== 第二阶段：补充剩余配额 ==========
    # 从剩余新闻中按时间排序，补充到足够数量
    remaining_articles.sort(key=lambda x: x.publish_time, reverse=True)

    # 合并配额文章和补充文章
    combined_articles = quota_articles + remaining_articles[:top_n - len(quota_articles)]

    # ========== 第三阶段：按源分组轮询排列 ==========
    # 将文章按源重新分组（合并后）
    source_queues = defaultdict(list)
    for article in combined_articles:
        source_queues[article.source].append(article)

    # 获取所有源列表（按源优先级排序，这里按源名排序保证一致性）
    sources = sorted(source_queues.keys())

    # 轮询从每个源取文章
    top_articles = []
    round_num = 1

    while len(top_articles) < top_n:
        round_has_articles = False

        for source in sources:
            if len(source_queues[source]) > 0:
                # 每轮从每个源取1条（如果还有的话）
                article = source_queues[source].pop(0)
                top_articles.append(article)
                round_has_articles = True

                # 如果已经够了，退出
                if len(top_articles) >= top_n:
                    break

        # 如果某一轮没有任何文章了，退出循环
        if not round_has_articles:
            break

        round_num += 1

    return top_articles


def main():
    """端到端测试主流程"""

    logger.info("=" * 60)
    logger.info("端到端测试开始")
    logger.info("=" * 60)

    # ==================== 步骤1：配置验证 ====================
    logger.info("\n【步骤1】配置验证...")
    Config.validate()
    logger.info("  ✓ 配置验证通过")

    # ==================== 步骤2：初始化数据库 ====================
    logger.info("\n【步骤2】初始化数据库...")
    db_manager = DatabaseManager(Config.DATABASE_PATH)
    db_manager.init_database()
    logger.info("  ✓ 数据库初始化完成")

    stats = db_manager.get_stats()
    logger.info(f"  数据库统计: 总记录 {stats['total_articles']} 条")

    # ==================== 步骤3：抓取新闻（每个源只抓1条）====================
    logger.info("\n【步骤3】抓取新闻（测试模式：每个源只抓1条）...")
    all_articles = fetch_all_sources()

    # 限制每个源只保留最新的1条
    source_articles = defaultdict(list)
    for article in all_articles:
        source_articles[article.source].append(article)

    test_articles = []
    for source, articles in source_articles.items():
        # 按时间倒序，只取第一条
        articles.sort(key=lambda x: x.publish_time, reverse=True)
        test_articles.append(articles[0])
        logger.info(f"  {source}: 选取了1条 (发布时间: {articles[0].publish_time})")

    logger.info(f"  总计: 从{len(source_articles)}个源中选取了{len(test_articles)}条新闻")

    if not test_articles:
        logger.warning("  没有抓取到任何新闻！")
        return

    # ==================== 步骤4：去重检查 ====================
    logger.info("\n【步骤4】去重检查...")
    new_articles = []
    cached_articles = []

    for article in test_articles:
        if db_manager.article_exists(article.title, article.title_original):
            cached = db_manager.get_article_by_title(article.title, article.title_original)
            if cached:
                cached_articles.append(cached)
                logger.info(f"  ✓ 缓存命中: {cached.title_original or cached.title[:30]}...")
        else:
            new_articles.append(article)
            logger.info(f"  + 新新闻: {article.title_original or article.title[:30]}...")

    logger.info(f"  新文章: {len(new_articles)} 条")
    logger.info(f"  缓存文章: {len(cached_articles)} 条")

    if not new_articles:
        logger.warning("  没有新文章需要处理！使用缓存文章生成HTML...")
        all_articles = cached_articles
    else:
        # ==================== 步骤5：翻译 ====================
        logger.info("\n【步骤5】翻译所有新新闻...")
        translated_new = translate_articles(new_articles)
        logger.info(f"  ✓ 翻译完成（处理了 {len(new_articles)} 条新新闻）")

        # ==================== 步骤6：保存到数据库 ====================
        logger.info("\n【步骤6】保存新新闻到数据库...")
        saved_count = 0
        for article in translated_new:
            # 保存到数据库
            try:
                db_manager.save_article(article)
                logger.debug(f"  已保存: {article.title_original or article.title[:30]}...")
                saved_count += 1
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    logger.warning(f"  跳过重复: {article.title_original or article.title[:30]}...")
                else:
                    logger.error(f"  保存失败: {e}")

        logger.info(f"  ✓ 已保存 {saved_count} 条新新闻到数据库")
        all_articles = translated_new + cached_articles

    # ==================== 步骤7：筛选TOP新闻 ====================
    logger.info("\n【步骤7】筛选TOP 20新闻...")
    top_news = select_top_news(all_articles, top_n=Config.TOP_NEWS_COUNT)
    logger.info(f"  ✓ 从 {len(all_articles)} 条新闻中筛选出 TOP {len(top_news)} 条")

    for i, article in enumerate(top_news, 1):
        logger.info(f"  {i}. {article.title[:40]}...")

    # ==================== 步骤8：生成HTML ====================
    logger.info("\n【步骤8】生成HTML...")
    generator = HTMLGenerator()
    output_path = generator.generate(top_news)
    logger.success(f"  ✓ HTML已生成: {output_path}")

    # ==================== 步骤9：更新首页 ====================
    logger.info("\n【步骤9】更新首页...")
    updater = IndexUpdater(project_root=Config.BASE_DIR.parent)
    success = updater.update_index(days=30)
    if success:
        logger.success(f"  ✓ 首页已更新: {updater.index_file}")
    else:
        logger.warning("  ⚠ 首页更新失败")

    # ==================== 完成 ====================
    logger.info("\n" + "=" * 60)
    logger.success("端到端测试完成！")
    logger.info("=" * 60)
    logger.info(f"\n生成的文件:")
    logger.info(f"  - {output_path}")
    logger.info(f"  - {updater.index_file}")
    logger.info(f"\n在浏览器中打开查看效果：")
    logger.info(f"  file://{output_path.absolute()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n测试被用户中断")
    except Exception as e:
        logger.exception(f"\n测试失败: {e}")
        sys.exit(1)
