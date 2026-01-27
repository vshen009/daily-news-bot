"""
清空正式表并使用v2.1新系统重新生成数据

流程：
1. 备份当前数据
2. 清空news_articles表
3. 使用v2.1新系统处理raw_articles
4. 保存到news_articles
5. 验证结果
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from news_bot.src.database import DatabaseManager
from news_bot.src.models import NewsArticle, Category, Language
from news_bot.src.utils import get_effective_publish_time
from news_bot.src.deduplicator import (
    deduplicate_by_title,
    cross_category_deduplicate,
    fill_top_10
)
from news_bot.src.scorer import select_top_news


def backup_news_articles():
    """备份正式表数据"""
    db_path = project_root / "news_bot" / "data" / "news.db"

    logger.info("【备份】备份当前正式表数据...")

    # 创建备份
    backup_path = project_root / "news_bot" / "data" / f"news_articles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    import shutil
    shutil.copy2(db_path, backup_path)

    logger.info(f"✓ 备份完成: {backup_path}")
    return backup_path


def clean_news_articles():
    """清空正式表"""
    db_path = project_root / "news_bot" / "data" / "news.db"

    logger.info("【清理】清空正式表 news_articles...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查看当前记录数
    cursor.execute("SELECT COUNT(*) FROM news_articles")
    count_before = cursor.fetchone()[0]
    logger.info(f"  清空前记录数: {count_before}")

    # 清空表
    cursor.execute("DELETE FROM news_articles")

    # 重置自增ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='news_articles'")

    conn.commit()
    conn.close()

    logger.info("✓ 正式表已清空")


def process_and_save():
    """处理raw_articles并保存到news_articles"""
    db_path = project_root / "news_bot" / "data" / "news.db"
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    try:
        logger.info("=" * 60)
        logger.info("开始v2.1数据处理流程")
        logger.info("=" * 60)

        # ========== 步骤1：读取原始数据 ==========
        logger.info("\n【步骤1】读取原始数据...")
        raw_articles = db_manager.get_raw_articles()
        stats = db_manager.get_raw_stats()
        logger.info(f"  读取到 {len(raw_articles)} 条原始新闻")
        logger.info(f"  按板块: {stats['category_stats']}")

        # ========== 步骤2：时间字段处理 ==========
        logger.info("\n【步骤2】时间字段处理...")
        time_processed_count = 0
        for article in raw_articles:
            original_time = article.get('publish_time')
            effective_time = get_effective_publish_time(article)
            article['_effective_publish_time'] = effective_time

            if not original_time:
                time_processed_count += 1

        logger.info(f"  时间处理完成，保底: {time_processed_count}条")

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

        # ========== 步骤4：板块内去重 ==========
        logger.info("\n【步骤4】板块内去重...")
        deduped_by_category = {}
        for category, articles in grouped.items():
            before = len(articles)
            deduped = deduplicate_by_title(articles)
            after = len(deduped)
            deduped_by_category[category] = deduped
            logger.info(f"  {category}: {before} → {after}")

        # ========== 步骤5：跨板块去重 ==========
        logger.info("\n【步骤5】跨板块去重...")
        deduped_final, backup = cross_category_deduplicate(deduped_by_category)

        total_before = sum(len(articles) for articles in deduped_by_category.values())
        total_after = sum(len(articles) for articles in deduped_final.values())
        total_backup = sum(len(articles) for articles in backup.values())

        logger.info(f"  去重前: {total_before}条")
        logger.info(f"  去重后: {total_after}条")
        logger.info(f"  候补: {total_backup}条")

        # ========== 步骤6：候补补齐 ==========
        logger.info("\n【步骤6】候补补齐...")
        from news_bot.src.deduplicator import fill_top_10
        filled = fill_top_10(deduped_final, backup, top_n=10)

        for category, articles in filled.items():
            logger.info(f"  {category}: {len(articles)}条")

        # ========== 步骤7：关键词筛选TOP 10 ==========
        logger.info("\n【步骤7】关键词筛选TOP 10...")
        final_selected = {}
        for category, articles in filled.items():
            selected = select_top_news(articles, category, top_n=10)
            final_selected[category] = selected

        total_final = sum(len(articles) for articles in final_selected.values())
        logger.info(f"  最终精选: {total_final}条")

        # ========== 步骤8：翻译英文新闻（模拟） ==========
        logger.info("\n【步骤8】翻译英文新闻（模拟）...")
        translation_count = 0
        for category, articles in final_selected.items():
            for article in articles:
                if article.get('language') == 'en':
                    # 模拟翻译
                    article['title'] = f"[翻译] {article.get('title_original', '')[:50]}"
                    article['content'] = f"[翻译内容]"
                    article['translated'] = True
                    article['translation_method'] = 'claude'
                    translation_count += 1

        logger.info(f"  翻译了 {translation_count}条英文新闻")

        # ========== 步骤9：生成AI评论（模拟） ==========
        logger.info("\n【步骤9】生成AI评论（模拟）...")
        comment_count = 0
        for category, articles in final_selected.items():
            for article in articles:
                if not article.get('ai_comment'):
                    # 模拟AI评论
                    title = article.get('title', article.get('title_original', ''))[:30]
                    article['ai_comment'] = f"AI分析：{title}值得关注"
                    comment_count += 1

        logger.info(f"  生成了 {comment_count}条AI评论")

        # ========== 步骤10：保存到news_articles ==========
        logger.info("\n【步骤10】保存到正式表...")
        saved_count = 0
        for category, articles in final_selected.items():
            for article in articles:
                try:
                    # 创建NewsArticle对象
                    news_article = NewsArticle(
                        title=article.get('title', ''),
                        title_original=article.get('title_original', ''),
                        content=article.get('content', ''),
                        content_original=article.get('content_original', ''),
                        source=article.get('source', ''),
                        source_original=article.get('source_original', ''),
                        url=article.get('url', ''),
                        category=Category(article.get('category', 'domestic')),
                        language=Language(article.get('language', 'zh')),
                        publish_time=datetime.fromisoformat(article.get('publish_time', '')) if article.get('publish_time') else datetime.now(),
                        crawl_time=datetime.fromisoformat(article.get('crawl_time', '')),
                        tags=[],
                        ai_comment=article.get('ai_comment', ''),
                        translated=bool(article.get('translated', False)),
                        translation_method=article.get('translation_method', ''),
                        featured=True
                    )

                    # 保存到数据库
                    db_manager.save_article(news_article)
                    saved_count += 1

                except Exception as e:
                    logger.error(f"保存失败: {e}")

        logger.info(f"✓ 成功保存 {saved_count}条新闻到正式表")

        # ========== 验证结果 ==========
        logger.info("\n【验证】检查保存结果...")
        final_stats = db_manager.get_stats()
        logger.info(f"  正式表总记录数: {final_stats['total_articles']}")
        logger.info(f"  按板块: {final_stats['category_stats']}")
        logger.info(f"  已翻译: {final_stats['translated_count']}")
        logger.info(f"  已评论: {final_stats['with_ai_comments']}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ 数据重新生成完成！")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"处理失败: {e}")
        raise

    finally:
        db_manager.close()


def main():
    """主流程"""
    # 配置日志
    logger.remove()
    logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

    logger.info("开始清空并重新生成数据...")

    # 步骤1：备份
    backup_path = backup_news_articles()

    # 步骤2：清空
    clean_news_articles()

    # 步骤3：重新生成
    process_and_save()

    logger.info("\n✅ 全部完成！")
    logger.info(f"备份文件: {backup_path}")


if __name__ == "__main__":
    main()
