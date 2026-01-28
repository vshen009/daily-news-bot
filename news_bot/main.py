"""主程序"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.database import DatabaseManager
from src.scraper import fetch_all_sources
from src.translator import translate_articles
from src.ai_comment import generate_comments
from src.html_generator import HTMLGenerator


def setup_logging():
    """配置日志"""
    Config.ensure_directories()
    logger.add(
        Config.LOGS_DIR / "news_bot_{time}.log",
        rotation="1 day",
        retention="7 days",
        level="INFO"
    )


def select_top_news(articles: list, top_n: int = 20) -> list:
    """
    筛选新闻（时间混合 + 源配额方案）

    新逻辑（方案 B）：
    1. 先从每个源取 2 条最新新闻（确保每个源都有展示）
    2. 从剩余新闻中按时间排序补充，直到凑够 20 条
    3. 最后全部按发布时间倒序排列

    旧逻辑（已屏蔽，保留代码）：
    - 评分规则：新新闻优先、有AI评论优先、发布时间越新越好

    Args:
        articles: 所有新闻列表
        top_n: 筛选数量，默认20条

    Returns:
        筛选后的新闻列表（按发布时间倒序）
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
    # 从剩余新闻中按时间排序，补充到 top_n 条
    remaining_articles.sort(key=lambda x: x.publish_time, reverse=True)

    # 合并配额文章和补充文章
    combined_articles = quota_articles + remaining_articles[:top_n - len(quota_articles)]

    # ========== 第三阶段：按时间倒序排列 ==========
    # 最终全部按发布时间倒序排列（确保时间连续性）
    combined_articles.sort(key=lambda x: x.publish_time, reverse=True)

    # 只取前 top_n 条
    top_articles = combined_articles[:top_n]

    logger.info(f"  源配额阶段: {len(quota_articles)} 条（每个源至少2条）")
    logger.info(f"  补充阶段: {len(remaining_articles[:top_n - len(quota_articles)])} 条")
    logger.info(f"  最终筛选: {len(top_articles)} 条")

    return top_articles


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='财经新闻抓取系统')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("新闻抓取系统启动")
    logger.info("=" * 60)

    try:
        # 1. 配置验证
        logger.info("步骤1: 配置验证")
        Config.validate()
        logger.info("✓ 配置验证通过")

        # 2. 初始化数据库
        logger.info("\n步骤2: 初始化数据库")
        db_manager = DatabaseManager(Config.DATABASE_PATH)
        db_manager.init_database()
        logger.info("✓ 数据库初始化完成")

        # 显示数据库统计
        stats = db_manager.get_stats()
        logger.info(f"数据库统计: 总记录 {stats['total_articles']} 条, "
                   f"已翻译 {stats['translated_count']} 条, "
                   f"有AI评论 {stats['with_ai_comments']} 条")

        # 3. 抓取新闻
        logger.info("\n步骤3: 抓取新闻")
        all_articles = fetch_all_sources()
        logger.info(f"✓ 抓取到 {len(all_articles)} 条新闻")

        if not all_articles:
            logger.warning("没有抓取到任何新闻！")
            return

        # 4. 去重检查：分离新新闻和缓存新闻
        logger.info("\n步骤4: 去重检查")
        new_articles = []
        cached_articles = []

        for article in all_articles:
            if db_manager.article_exists(article.title, article.title_original):
                # 新闻已存在，从数据库读取
                cached = db_manager.get_article_by_title(article.title, article.title_original)
                if cached:
                    cached_articles.append(cached)
                    logger.info(f"  缓存命中: {cached.title_original or cached.title}")
            else:
                # 新新闻，需要处理
                new_articles.append(article)
                logger.info(f"  新新闻: {article.title_original or article.title}")

        logger.info(f"✓ 去重完成: 新新闻 {len(new_articles)} 条, 缓存 {len(cached_articles)} 条")

        # 5. 翻译所有新新闻（保存到数据库）
        logger.info("\n步骤5: 翻译所有新新闻")
        translated_new = translate_articles(new_articles)
        logger.info(f"✓ 翻译完成（处理了 {len(new_articles)} 条新新闻）")

        # 6. 为所有新新闻生成AI评论（保存到数据库）
        logger.info("\n步骤6: 生成AI评论（所有新新闻）")
        saved_count = 0
        for article in translated_new:
            if not article.ai_comment:
                from src.ai_comment import generate_comment
                comment = generate_comment(article)
                article.ai_comment = comment

            # 保存到数据库（检查重复）
            try:
                db_manager.save_article(article)
                logger.debug(f"  已保存: {article.title_original or article.title}")
                saved_count += 1
            except Exception as e:
                if "UNIQUE constraint" in str(e):
                    logger.warning(f"  跳过重复新闻: {article.title_original or article.title}")
                else:
                    logger.error(f"  保存失败: {e}")
                    raise

        logger.info(f"✓ 已保存 {saved_count} 条新新闻到数据库")

        # 7. 筛选TOP 20新闻（用于HTML显示）
        logger.info("\n步骤7: 筛选TOP 20新闻（用于HTML显示）")
        all_articles = translated_new + cached_articles
        top_news = select_top_news(all_articles, top_n=Config.TOP_NEWS_COUNT)
        logger.info(f"✓ 从 {len(all_articles)} 条新闻中筛选出 TOP {len(top_news)} 条")

        # 8. 生成HTML（只显示TOP 20）
        logger.info("\n步骤8: 生成HTML（TOP 20）")
        generator = HTMLGenerator()
        output_path = generator.generate(top_news)
        logger.info(f"✓ HTML已生成: {output_path}")

        # 9. 更新首页（自动更新index.html）
        logger.info("\n步骤9: 更新首页")
        from src.index_updater import IndexUpdater
        updater = IndexUpdater(project_root=Config.BASE_DIR.parent)
        success = updater.update_index(days=30)
        if success:
            logger.info("✓ 首页已自动更新（保留30天）")
        else:
            logger.warning("⚠ 首页更新失败，但不影响新闻生成")

        logger.info("\n" + "=" * 60)
        logger.info("✓ 所有任务完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n✗ 执行失败: {e}")
        raise


if __name__ == "__main__":
    setup_logging()
    main()
