"""
主处理脚本（v2.1）

阶段2：从raw_articles读取并处理数据，生成最终HTML

流程：
1. 从raw_articles读取所有数据
2. 时间字段处理（使用保底逻辑）
3. 按板块分组
4. 板块内去重
5. 跨板块去重
6. 候补补齐到10条
7. 关键词筛选TOP 10
8. 翻译英文新闻（使用事务）
9. 生成AI评论（使用事务）
10. 保存到news_articles
11. 生成HTML
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from news_bot.src.database import DatabaseManager
from news_bot.src.utils import get_effective_publish_time
from news_bot.src.deduplicator import (
    deduplicate_by_title,
    cross_category_deduplicate,
    fill_top_10
)
from news_bot.src.scorer import select_top_news


def process_raw_articles():
    """
    主处理流程：从raw_articles处理到最终HTML
    """
    logger.info("=" * 60)
    logger.info("开始数据处理流程（v2.1）")
    logger.info("=" * 60)

    # 初始化数据库
    db_path = project_root / "news_bot" / "data" / "news.db"
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    try:
        # ========== 步骤1：读取原始数据 ==========
        logger.info("\n【步骤1】读取原始数据...")
        raw_articles = db_manager.get_raw_articles()
        stats = db_manager.get_raw_stats()
        logger.info(f"  读取到 {len(raw_articles)} 条原始新闻")
        logger.info(f"  按板块分布: {stats['category_stats']}")
        logger.info(f"  按语言分布: {stats['language_stats']}")

        # ========== 步骤2：时间字段处理 ==========
        logger.info("\n【步骤2】时间字段处理（保底逻辑）...")
        time_processed_count = 0
        for article in raw_articles:
            original_time = article.get('publish_time')
            effective_time = get_effective_publish_time(article)
            article['_effective_publish_time'] = effective_time

            # 统计保底次数
            if not original_time:
                time_processed_count += 1

        logger.info(f"  时间处理完成，保底次数: {time_processed_count}")

        # ========== 步骤3：按板块分组 ==========
        logger.info("\n【步骤3】按板块分组...")
        grouped = {
            'domestic': [],
            'asia_pacific': [],
            'us_europe': []
        }

        for article in raw_articles:
            category = article.get('category', '')
            if category in grouped:
                grouped[category].append(article)

        logger.info(f"  分组结果:")
        for category, articles in grouped.items():
            logger.info(f"    {category}: {len(articles)}条")

        # ========== 步骤4：板块内去重 ==========
        logger.info("\n【步骤4】板块内去重...")
        deduped_by_category = {}
        for category, articles in grouped.items():
            before_count = len(articles)
            deduped = deduplicate_by_title(articles)
            after_count = len(deduped)
            deduped_by_category[category] = deduped
            logger.info(f"  {category}: {before_count} → {after_count} (删除{before_count - after_count}条)")

        # ========== 步骤5：跨板块去重 ==========
        logger.info("\n【步骤5】跨板块去重（全局）...")
        deduped_final, backup = cross_category_deduplicate(deduped_by_category)

        total_before = sum(len(articles) for articles in deduped_by_category.values())
        total_after = sum(len(articles) for articles in deduped_final.values())
        total_backup = sum(len(articles) for articles in backup.values())

        logger.info(f"  去重前总计: {total_before}条")
        logger.info(f"  去重后总计: {total_after}条")
        logger.info(f"  候补新闻: {total_backup}条")

        # ========== 步骤6：候补补齐 ==========
        logger.info("\n【步骤6】候补补齐（确保每个板块10条）...")
        filled = fill_top_10(deduped_final, backup, top_n=10)

        for category, articles in filled.items():
            count = len(articles)
            logger.info(f"  {category}: {count}条 {'✓' if count == 10 else '(不足10条)'}")

        # ========== 步骤7：关键词筛选TOP 10 ==========
        logger.info("\n【步骤7】关键词筛选TOP 10...")
        final_selected = {}
        for category, articles in filled.items():
            selected = select_top_news(articles, category, top_n=10)
            final_selected[category] = selected

        total_final = sum(len(articles) for articles in final_selected.values())
        logger.info(f"  最终精选: {total_final}条")

        # ========== 步骤8：翻译英文新闻（模拟） ==========
        logger.info("\n【步骤8】翻译英文新闻...")
        translation_count = 0
        for category, articles in final_selected.items():
            for article in articles:
                if article.get('language') == 'en' and not article.get('translated'):
                    # 这里应该调用真实的翻译API
                    # 为了测试，我们使用模拟数据
                    logger.info(f"  模拟翻译: {article.get('title_original', '')[:50]}")
                    translation_count += 1

        logger.info(f"  需要翻译: {translation_count}条")

        # ========== 步骤9：生成AI评论（模拟） ==========
        logger.info("\n【步骤9】生成AI评论...")
        comment_count = 0
        for category, articles in final_selected.items():
            for article in articles:
                if not article.get('ai_comment'):
                    # 这里应该调用真实的AI评论API
                    logger.info(f"  模拟生成评论: {article.get('title', article.get('title_original', ''))[:50]}")
                    comment_count += 1

        logger.info(f"  需要生成评论: {comment_count}条")

        # ========== 步骤10：保存到news_articles ==========
        logger.info("\n【步骤10】保存到正式表...")
        # 这里应该调用db_manager.save_article()
        # 为了测试，我们只做统计
        logger.info(f"  将保存 {total_final} 条新闻到 news_articles")

        # ========== 步骤11：生成HTML ==========
        logger.info("\n【步骤11】生成HTML...")
        # 这里应该调用html_generator
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        output_path = project_root / "public" / f"{today}.html"
        logger.info(f"  HTML将保存到: {output_path}")

        # ========== 总结 ==========
        logger.info("\n" + "=" * 60)
        logger.info("数据处理流程完成！")
        logger.info("=" * 60)
        logger.info(f"  原始数据: {len(raw_articles)}条")
        logger.info(f"  板块内去重: {total_before}条")
        logger.info(f"  跨板块去重: {total_after}条")
        logger.info(f"  候补补齐: {total_final}条")
        logger.info(f"  需要翻译: {translation_count}条")
        logger.info(f"  需要评论: {comment_count}条")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"处理流程出错: {e}")
        raise

    finally:
        db_manager.close()


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
    logger.add("logs/process_raw_{time:YYYY-MM-DD}.log", rotation="1 day")

    # 运行主流程
    process_raw_articles()
