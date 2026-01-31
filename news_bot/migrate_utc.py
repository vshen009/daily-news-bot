"""
数据库时间字段迁移脚本

将现有数据库中的 crawl_time, created_at, updated_at 从本地时间转换为 UTC 时间

注意：
1. 假设现有数据的 crawl_time, created_at, updated_at 是北京时间（UTC+8）
2. publish_time 已经是 UTC，不需要转换
3. 转换公式：UTC = 北京时间 - 8小时
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import Config
from src.database import DatabaseManager


def migrate_news_articles_to_utc(db_manager: DatabaseManager, dry_run: bool = True):
    """
    将 news_articles 表的时间字段转换为 UTC

    Args:
        db_manager: 数据库管理器
        dry_run: 是否为预演模式（True不实际修改数据库）
    """
    logger.info("=" * 60)
    logger.info(f"{'[预演模式]' if dry_run else '[实际执行]'} 迁移 news_articles 表")
    logger.info("=" * 60)

    with db_manager:
        # 查询所有需要转换的记录
        query = """
            SELECT id, title, crawl_time, created_at, updated_at
            FROM news_articles
        """
        results = db_manager.cursor.execute(query).fetchall()

        total = len(results)
        logger.info(f"找到 {total} 条记录需要检查")

        if dry_run:
            logger.info("\n预演模式：显示前5条记录的转换效果\n")

        converted_count = 0

        for idx, row in enumerate(results):
            record_id = row['id']
            title = row['title'][:50] if row['title'] else ''
            crawl_time_str = row['crawl_time']
            created_at_str = row['created_at']
            updated_at_str = row['updated_at']

            # 解析时间
            try:
                crawl_time = datetime.fromisoformat(crawl_time_str) if crawl_time_str else None
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else None
                updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else None

                # 转换为 UTC（减去8小时）
                crawl_time_utc = crawl_time - timedelta(hours=8) if crawl_time else None
                created_at_utc = created_at - timedelta(hours=8) if created_at else None
                updated_at_utc = updated_at - timedelta(hours=8) if updated_at else None

                # 预演模式：显示转换效果
                if dry_run and idx < 5:
                    logger.info(f"ID: {record_id}")
                    logger.info(f"  标题: {title}")
                    logger.info(f"  crawl_time:    {crawl_time_str} → {crawl_time_utc.isoformat() if crawl_time_utc else None}")
                    logger.info(f"  created_at:    {created_at_str} → {created_at_utc.isoformat() if created_at_utc else None}")
                    logger.info(f"  updated_at:    {updated_at_str} → {updated_at_utc.isoformat() if updated_at_utc else None}")
                    logger.info("")

                # 实际执行：更新数据库
                if not dry_run:
                    update_query = """
                        UPDATE news_articles
                        SET crawl_time = ?, created_at = ?, updated_at = ?
                        WHERE id = ?
                    """
                    db_manager.cursor.execute(update_query, (
                        crawl_time_utc.isoformat() if crawl_time_utc else None,
                        created_at_utc.isoformat() if created_at_utc else None,
                        updated_at_utc.isoformat() if updated_at_utc else None,
                        record_id
                    ))
                    converted_count += 1

                    if (idx + 1) % 100 == 0:
                        logger.info(f"已处理 {idx + 1}/{total} 条记录")

            except Exception as e:
                logger.error(f"处理记录 ID={record_id} 时出错: {e}")
                continue

        if not dry_run:
            logger.info(f"\n✓ 成功转换 {converted_count}/{total} 条记录")


def migrate_raw_articles_to_utc(db_manager: DatabaseManager, dry_run: bool = True):
    """
    将 raw_articles 表的时间字段转换为 UTC

    Args:
        db_manager: 数据库管理器
        dry_run: 是否为预演模式
    """
    logger.info("=" * 60)
    logger.info(f"{'[预演模式]' if dry_run else '[实际执行]'} 迁移 raw_articles 表")
    logger.info("=" * 60)

    with db_manager:
        # 查询所有需要转换的记录
        query = """
            SELECT id, title, crawl_time, created_at
            FROM raw_articles
        """
        results = db_manager.cursor.execute(query).fetchall()

        total = len(results)
        logger.info(f"找到 {total} 条记录需要检查")

        if dry_run:
            logger.info("\n预演模式：显示前5条记录的转换效果\n")

        converted_count = 0

        for idx, row in enumerate(results):
            record_id = row['id']
            title = (row['title'] or '')[:50]
            crawl_time_str = row['crawl_time']
            created_at_str = row['created_at']

            # 解析时间
            try:
                crawl_time = datetime.fromisoformat(crawl_time_str) if crawl_time_str else None
                created_at = datetime.fromisoformat(created_at_str) if created_at_str else None

                # 转换为 UTC（减去8小时）
                crawl_time_utc = crawl_time - timedelta(hours=8) if crawl_time else None
                created_at_utc = created_at - timedelta(hours=8) if created_at else None

                # 预演模式：显示转换效果
                if dry_run and idx < 5:
                    logger.info(f"ID: {record_id}")
                    logger.info(f"  标题: {title}")
                    logger.info(f"  crawl_time:    {crawl_time_str} → {crawl_time_utc.isoformat() if crawl_time_utc else None}")
                    logger.info(f"  created_at:    {created_at_str} → {created_at_utc.isoformat() if created_at_utc else None}")
                    logger.info("")

                # 实际执行：更新数据库
                if not dry_run:
                    update_query = """
                        UPDATE raw_articles
                        SET crawl_time = ?, created_at = ?
                        WHERE id = ?
                    """
                    db_manager.cursor.execute(update_query, (
                        crawl_time_utc.isoformat() if crawl_time_utc else None,
                        created_at_utc.isoformat() if created_at_utc else None,
                        record_id
                    ))
                    converted_count += 1

                    if (idx + 1) % 100 == 0:
                        logger.info(f"已处理 {idx + 1}/{total} 条记录")

            except Exception as e:
                logger.error(f"处理记录 ID={record_id} 时出错: {e}")
                continue

        if not dry_run:
            logger.info(f"\n✓ 成功转换 {converted_count}/{total} 条记录")


def main():
    """主函数"""
    logger.info("开始数据库时区迁移...")
    logger.info("假设：现有数据使用北京时间（UTC+8）")
    logger.info("目标：统一转换为 UTC 时间\n")

    # 初始化数据库
    db_path = Config.DATABASE_DIR / "news.db"
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    try:
        # 第一步：预演模式（不修改数据库）
        logger.info("\n" + "=" * 60)
        logger.info("第一步：预演模式（不修改数据库）")
        logger.info("=" * 60 + "\n")

        migrate_news_articles_to_utc(db_manager, dry_run=True)
        print()
        migrate_raw_articles_to_utc(db_manager, dry_run=True)

        # 询问用户是否继续
        logger.info("\n" + "=" * 60)
        response = input("\n是否执行实际迁移？这将修改数据库！(yes/no): ").strip().lower()

        if response == 'yes':
            # 第二步：实际执行
            logger.info("\n" + "=" * 60)
            logger.info("第二步：实际执行迁移")
            logger.info("=" * 60 + "\n")

            migrate_news_articles_to_utc(db_manager, dry_run=False)
            print()
            migrate_raw_articles_to_utc(db_manager, dry_run=False)

            logger.info("\n" + "=" * 60)
            logger.info("✓ 迁移完成！")
            logger.info("=" * 60)
        else:
            logger.info("\n已取消迁移。")

    finally:
        db_manager.close()


if __name__ == "__main__":
    main()
