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


def select_top_news(articles: list, top_n: int = 15) -> list:
    """
    筛选重要新闻（跨板块总共TOP N）

    评分规则：
    1. 新新闻优先（没有数据库ID）
    2. 发布时间越新越好
    3. 有AI评论优先
    4. 板块平衡（尽量覆盖3个板块）

    Args:
        articles: 所有新闻列表
        top_n: 筛选数量，默认15条

    Returns:
        筛选后的新闻列表
    """
    from src.models import Category

    # 为每条新闻计算得分
    scored_articles = []
    for article in articles:
        score = 0

        # 新新闻优先（+50分）
        if article.id is None:
            score += 50

        # 有AI评论优先（+20分）
        if article.ai_comment:
            score += 20

        # 发布时间（越新越好，最多+30分）
        # 计算新闻年龄（小时）
        from datetime import datetime, timedelta
        age_hours = (datetime.now() - article.publish_time).total_seconds() / 3600
        if age_hours < 6:
            score += 30
        elif age_hours < 12:
            score += 20
        elif age_hours < 24:
            score += 10
        elif age_hours < 48:
            score += 5

        # 已翻译优先（+10分）
        if article.translated:
            score += 10

        scored_articles.append((score, article))

    # 按得分倒序排序
    scored_articles.sort(key=lambda x: x[0], reverse=True)

    # 取前N条
    top_articles = [article for score, article in scored_articles[:top_n]]

    # 确保板块平衡（如果可能）
    # 统计各板块数量
    from collections import Counter
    category_count = Counter(a.category for a in top_articles)

    # 如果某个板块没有新闻，尝试替换低分新闻
    for category in [Category.DOMESTIC, Category.ASIA_PACIFIC, Category.US_EUROPE]:
        if category_count.get(category, 0) == 0:
            # 从剩余新闻中查找该板块的新闻
            for score, article in scored_articles[top_n:]:
                if article.category == category:
                    # 找到最低分且不是该板块的新闻进行替换
                    for i, existing in enumerate(top_articles):
                        if existing.category != category:
                            # 替换
                            top_articles[i] = article
                            category_count[existing.category] -= 1
                            category_count[category] = category_count.get(category, 0) + 1
                            break
                    break

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

        # 7. 筛选TOP 15新闻（用于HTML显示）
        logger.info("\n步骤7: 筛选TOP 15新闻（用于HTML显示）")
        all_articles = translated_new + cached_articles
        top_15_news = select_top_news(all_articles, top_n=15)
        logger.info(f"✓ 从 {len(all_articles)} 条新闻中筛选出 TOP {len(top_15_news)} 条")

        # 统计板块分布
        from src.models import Category
        category_dist = {}
        for article in top_15_news:
            cat = article.category.value
            category_dist[cat] = category_dist.get(cat, 0) + 1
        logger.info(f"  板块分布: {category_dist}")

        # 8. 生成HTML（只显示TOP 15）
        logger.info("\n步骤8: 生成HTML（TOP 15）")
        generator = HTMLGenerator()
        output_path = generator.generate(top_15_news)
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
