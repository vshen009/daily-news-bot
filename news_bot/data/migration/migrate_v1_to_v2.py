"""数据迁移脚本：从v1表结构升级到v2表结构

v1表结构：
- id, title, content, source, category, publish_date, created_at

v2表结构：
- id, title, title_original, content, content_original, source, source_original,
  url, category, language, publish_time, crawl_time, tags, ai_comment,
  translated, translation_method, featured, created_at, updated_at
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from loguru import logger


def migrate_v1_to_v2(db_path: Path, backup: bool = True) -> bool:
    """
    执行数据库迁移

    Args:
        db_path: 数据库文件路径
        backup: 是否备份原数据库

    Returns:
        bool: 迁移成功返回True，失败返回False
    """
    logger.info("=" * 60)
    logger.info("开始数据库迁移: v1 → v2")
    logger.info("=" * 60)

    try:
        # 1. 备份原数据库
        if backup:
            backup_path = db_path.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_news.db"
            shutil.copy2(db_path, backup_path)
            logger.info(f"✓ 备份完成: {backup_path}")

        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 2. 检查当前表结构
        logger.info("步骤1: 检查当前表结构")
        cursor.execute("PRAGMA table_info(news_articles)")
        columns = {row[1] for row in cursor.fetchall()}

        # 检查是否已经是v2结构
        if 'language' in columns and 'title_original' in columns:
            logger.info("✓ 数据库已经是v2结构，无需迁移")
            conn.close()
            return True

        # 检查是否是v1结构
        if 'publish_date' in columns and 'publish_time' not in columns:
            logger.info("检测到v1表结构，准备升级")

            # 3. 读取现有数据
            logger.info("步骤2: 读取现有数据")
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total = cursor.fetchone()[0]
            logger.info(f"现有记录数: {total}")

            cursor.execute("SELECT * FROM news_articles")
            old_data = cursor.fetchall()
            logger.info(f"✓ 已读取 {len(old_data)} 条记录")

            # 4. 重命名旧表
            logger.info("步骤3: 重命名旧表")
            cursor.execute("ALTER TABLE news_articles RENAME TO news_articles_v1")
            logger.info("✓ 旧表已重命名为 news_articles_v1")

            # 5. 创建新表
            logger.info("步骤4: 创建新表结构")
            cursor.execute("""
                CREATE TABLE news_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    title_original TEXT,
                    content TEXT,
                    content_original TEXT,
                    source TEXT NOT NULL,
                    source_original TEXT,
                    url TEXT,
                    category TEXT NOT NULL,
                    language TEXT NOT NULL DEFAULT 'zh',
                    publish_time TIMESTAMP NOT NULL,
                    crawl_time TIMESTAMP NOT NULL,
                    tags TEXT,
                    ai_comment TEXT,
                    translated BOOLEAN DEFAULT 0,
                    translation_method TEXT,
                    featured BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT unique_title UNIQUE (title, title_original)
                )
            """)
            logger.info("✓ 新表创建成功")

            # 6. 创建索引
            logger.info("步骤5: 创建索引")
            cursor.execute("""
                CREATE INDEX idx_publish_time ON news_articles(publish_time DESC)
            """)
            cursor.execute("""
                CREATE INDEX idx_category ON news_articles(category)
            """)
            cursor.execute("""
                CREATE INDEX idx_title_original ON news_articles(title_original)
            """)
            logger.info("✓ 索引创建成功")

            # 7. 迁移数据
            logger.info("步骤6: 迁移数据")
            migrated_count = 0

            for row in old_data:
                try:
                    # v1数据结构：id, title, content, source, category, publish_date, created_at
                    old_id = row[0]
                    title = row[1]
                    content = row[2]
                    source = row[3]
                    category = row[4]
                    publish_date = row[5]
                    created_at = row[6]

                    # 转换为新表结构
                    # publish_date 是字符串格式，需要转换为 ISO 格式
                    # 如果已经是ISO格式则直接使用，否则尝试解析
                    try:
                        # 尝试解析 publish_date
                        if isinstance(publish_date, str):
                            # 假设是 ISO 格式或可解析格式
                            publish_time = publish_date
                        else:
                            publish_time = datetime.now().isoformat()
                    except:
                        publish_time = datetime.now().isoformat()

                    # crawl_time 使用 created_at
                    crawl_time = created_at if created_at else datetime.now().isoformat()

                    # 插入新表
                    cursor.execute("""
                        INSERT INTO news_articles (
                            title, content, source, category,
                            language, publish_time, crawl_time,
                            translated, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        title, content, source, category,
                        'zh', publish_time, crawl_time,
                        0, created_at
                    ))

                    migrated_count += 1

                except Exception as e:
                    logger.warning(f"迁移记录失败 (ID={old_id}): {e}")
                    continue

            logger.info(f"✓ 成功迁移 {migrated_count} 条记录")

            # 8. 验证迁移结果
            logger.info("步骤7: 验证迁移结果")
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            new_total = cursor.fetchone()[0]

            if new_total == total:
                logger.info(f"✓ 验证通过: 迁移前后记录数一致 ({new_total} 条)")
            else:
                logger.warning(f"⚠ 警告: 迁移前后记录数不一致 (原:{total}, 新:{new_total})")

            # 9. 删除旧表（可选）
            logger.info("步骤8: 清理旧表")
            response = input("是否删除旧表 news_articles_v1? (y/n): ")
            if response.lower() == 'y':
                cursor.execute("DROP TABLE news_articles_v1")
                logger.info("✓ 旧表已删除")
            else:
                logger.info("保留旧表 news_articles_v1")

            # 提交事务
            conn.commit()
            conn.close()

            logger.info("\n" + "=" * 60)
            logger.info("✓ 数据库迁移完成！")
            logger.info("=" * 60)
            return True

        else:
            logger.warning("未知的表结构，跳过迁移")
            conn.close()
            return False

    except Exception as e:
        logger.error(f"✗ 迁移失败: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    import sys

    # 添加项目路径
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    src_dir = project_root / "news_bot" / "src"

    sys.path.insert(0, str(src_dir))

    from config import Config

    # 配置日志
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    # 执行迁移
    db_path = Config.DATABASE_PATH

    print(f"数据库路径: {db_path}")
    print(f"数据库存在: {db_path.exists()}")
    print()

    if db_path.exists():
        success = migrate_v1_to_v2(db_path, backup=True)

        if success:
            print("\n✓ 迁移成功！")
        else:
            print("\n✗ 迁移失败！")
    else:
        print("数据库文件不存在，无需迁移")
