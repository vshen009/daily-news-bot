"""简单迁移执行脚本"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# 数据库路径
DB_PATH = Path("news_bot/data/news.db")

def migrate():
    """执行迁移"""
    print("=" * 60)
    print("开始数据库迁移")
    print("=" * 60)

    # 1. 备份
    backup_path = DB_PATH.parent / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_news.db"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✓ 备份完成: {backup_path}")

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. 检查当前表结构
    print("\n步骤1: 检查当前表结构")
    cursor.execute("PRAGMA table_info(news_articles)")
    columns = {row[1] for row in cursor.fetchall()}
    print(f"现有列: {columns}")

    # 检查是否需要迁移
    if 'language' in columns and 'title_original' in columns:
        print("✓ 数据库已经是新结构，无需迁移")
        conn.close()
        return True

    # 3. 读取现有数据
    print("\n步骤2: 读取现有数据")
    cursor.execute("SELECT * FROM news_articles")
    old_data = cursor.fetchall()
    print(f"✓ 已读取 {len(old_data)} 条记录")

    # 4. 重命名旧表
    print("\n步骤3: 重命名旧表")
    cursor.execute("ALTER TABLE news_articles RENAME TO news_articles_v1")
    print("✓ 旧表已重命名")

    # 5. 创建新表
    print("\n步骤4: 创建新表")
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
    print("✓ 新表创建成功")

    # 6. 创建索引
    print("\n步骤5: 创建索引")
    cursor.execute("CREATE INDEX idx_publish_time ON news_articles(publish_time DESC)")
    cursor.execute("CREATE INDEX idx_category ON news_articles(category)")
    cursor.execute("CREATE INDEX idx_title_original ON news_articles(title_original)")
    print("✓ 索引创建成功")

    # 7. 迁移数据
    print("\n步骤6: 迁移数据")
    migrated_count = 0

    for row in old_data:
        try:
            # v1结构: id, title, content, source, category, publish_date, created_at
            title = row[1]
            content = row[2]
            source = row[3]
            category = row[4]
            publish_date = row[5]
            created_at = row[6]

            # 插入新表
            cursor.execute("""
                INSERT INTO news_articles (
                    title, content, source, category,
                    language, publish_time, crawl_time,
                    translated, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, content, source, category, 'zh',
                  publish_date, created_at, 0, created_at))

            migrated_count += 1

        except Exception as e:
            print(f"警告: 迁移记录失败 - {e}")
            continue

    print(f"✓ 成功迁移 {migrated_count} 条记录")

    # 8. 验证
    print("\n步骤7: 验证结果")
    cursor.execute("SELECT COUNT(*) FROM news_articles")
    new_total = cursor.fetchone()[0]
    print(f"新表记录数: {new_total}")

    # 9. 删除旧表
    print("\n步骤8: 删除旧表")
    cursor.execute("DROP TABLE news_articles_v1")
    print("✓ 旧表已删除")

    # 提交
    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("✓ 数据库迁移完成！")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        if DB_PATH.exists():
            migrate()
        else:
            print("数据库文件不存在")
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
