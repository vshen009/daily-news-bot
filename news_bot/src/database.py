"""数据库管理模块"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger

from .models import NewsArticle, Category, Language
from .config import Config


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: Path):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        self.cursor = self.conn.cursor()
        logger.debug(f"数据库已连接: {self.db_path}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.debug("数据库连接已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.close()

    def init_database(self):
        """
        初始化数据库表结构

        如果表不存在则创建，已存在则检查并升级
        """
        with self:
            # 检查news_articles表是否存在
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='news_articles'
            """)
            table_exists = self.cursor.fetchone() is not None

            if not table_exists:
                # 创建新表
                self._create_tables()
                logger.info("✓ 数据库表创建成功")
            else:
                # 检查表结构是否需要升级
                self._upgrade_table_if_needed()
                logger.info("✓ 数据库表检查完成")

            # 创建原始抓取数据临时表（每次都确保存在）
            self._create_raw_articles_table()

    def _create_tables(self):
        """创建数据库表"""
        # 创建新闻文章表
        self.cursor.execute("""
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
                language TEXT NOT NULL,
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

        # 创建索引
        self.cursor.execute("""
            CREATE INDEX idx_publish_time ON news_articles(publish_time DESC)
        """)

        self.cursor.execute("""
            CREATE INDEX idx_category ON news_articles(category)
        """)

        self.cursor.execute("""
            CREATE INDEX idx_title_original ON news_articles(title_original)
        """)

        logger.debug("数据库表和索引已创建")

    def _upgrade_table_if_needed(self):
        """
        检查并升级表结构

        添加缺失的列（如果需要）
        """
        # 获取表结构
        self.cursor.execute("PRAGMA table_info(news_articles)")
        columns = {row['name'] for row in self.cursor.fetchall()}

        # 检查并添加缺失的列
        required_columns = {
            'title_original', 'source_original', 'content_original',
            'url', 'language', 'tags', 'ai_comment',
            'translated', 'translation_method', 'featured'
        }

        missing_columns = required_columns - columns

        if missing_columns:
            logger.info(f"检测到缺失列，准备升级: {missing_columns}")

            # 添加缺失的列（如果不存在）
            if 'title_original' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN title_original TEXT")
            if 'source_original' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN source_original TEXT")
            if 'content_original' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN content_original TEXT")
            if 'url' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN url TEXT")
            if 'language' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN language TEXT NOT NULL DEFAULT 'zh'")
            if 'tags' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN tags TEXT")
            if 'ai_comment' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN ai_comment TEXT")
            if 'translated' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN translated BOOLEAN DEFAULT 0")
            if 'translation_method' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN translation_method TEXT")
            if 'featured' not in columns:
                self.cursor.execute("ALTER TABLE news_articles ADD COLUMN featured BOOLEAN DEFAULT 0")

            # 检查并创建唯一索引
            self.cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='index' AND name='idx_title_original'
            """)
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    CREATE INDEX idx_title_original ON news_articles(title_original)
                """)

            logger.info("✓ 数据库表升级完成")

    def article_exists(self, title: str, title_original: Optional[str] = None) -> bool:
        """
        检查新闻是否已存在

        Args:
            title: 新闻标题（中文）
            title_original: 原始标题（英文）

        Returns:
            bool: 如果新闻已存在返回True，否则返回False
        """
        with self:
            if title_original:
                # 英文新闻：通过原始标题去重
                query = "SELECT id FROM news_articles WHERE title_original = ?"
                params = [title_original]
            else:
                # 中文新闻：通过中文标题去重
                query = "SELECT id FROM news_articles WHERE title = ? AND title_original IS NULL"
                params = [title]

            result = self.cursor.execute(query, params).fetchone()
            return result is not None

    def get_article_by_title(self, title: str, title_original: Optional[str] = None) -> Optional[NewsArticle]:
        """
        根据标题获取新闻文章

        Args:
            title: 新闻标题（中文）
            title_original: 原始标题（英文）

        Returns:
            NewsArticle: 新闻文章对象，如果不存在返回None
        """
        with self:
            if title_original:
                # 英文新闻：通过原始标题查询
                query = """
                    SELECT * FROM news_articles
                    WHERE title_original = ?
                """
                params = [title_original]
            else:
                # 中文新闻：通过中文标题查询
                query = """
                    SELECT * FROM news_articles
                    WHERE title = ? AND title_original IS NULL
                """
                params = [title]

            result = self.cursor.execute(query, params).fetchone()

            if result:
                return self._row_to_article(result)
            return None

    def save_article(self, article: NewsArticle) -> int:
        """
        保存新闻文章到数据库

        Args:
            article: 新闻文章对象

        Returns:
            int: 插入记录的ID
        """
        with self:
            # 将tags列表转为JSON字符串
            tags_json = str(article.tags) if article.tags else None

            query = """
                INSERT INTO news_articles (
                    title, title_original, content, content_original,
                    source, source_original, url, category, language,
                    publish_time, crawl_time, tags, ai_comment,
                    translated, translation_method, featured
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                article.title,
                article.title_original,
                article.content,
                article.content_original,
                article.source,
                article.source_original,
                article.url,
                article.category.value,
                article.language.value,
                article.publish_time.isoformat(),
                article.crawl_time.isoformat(),
                tags_json,
                article.ai_comment,
                int(article.translated),
                article.translation_method,
                int(article.featured)
            )

            self.cursor.execute(query, params)
            article_id = self.cursor.lastrowid

            logger.debug(f"文章已保存到数据库: ID={article_id}, title={article.title_original or article.title}")
            return article_id

    def update_ai_comment(self, article_id: int, comment: str) -> bool:
        """
        更新新闻的AI评论

        Args:
            article_id: 文章ID
            comment: AI评论内容

        Returns:
            bool: 更新成功返回True，失败返回False
        """
        with self:
            query = """
                UPDATE news_articles
                SET ai_comment = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """

            self.cursor.execute(query, (comment, article_id))
            success = self.cursor.rowcount > 0

            if success:
                logger.debug(f"AI评论已更新: ID={article_id}")
            else:
                logger.warning(f"更新AI评论失败: ID={article_id}")

            return success

    def get_all_articles(self, limit: Optional[int] = None) -> List[NewsArticle]:
        """
        获取所有新闻文章

        Args:
            limit: 限制返回数量，None表示不限制

        Returns:
            List[NewsArticle]: 新闻文章列表
        """
        with self:
            query = """
                SELECT * FROM news_articles
                ORDER BY publish_time DESC
            """

            if limit:
                query += f" LIMIT {limit}"

            results = self.cursor.execute(query).fetchall()

            articles = []
            for row in results:
                articles.append(self._row_to_article(row))

            return articles

    def get_articles_by_days(self, days: int = 7) -> List[NewsArticle]:
        """
        获取最近N天的所有新闻文章（已翻译、有AI评论）

        Args:
            days: 天数，默认7天

        Returns:
            List[NewsArticle]: 新闻文章列表
        """
        with self:
            # 计算时间范围（使用北京时间）
            cutoff_time = Config.get_beijing_time() - timedelta(days=days)

            query = """
                SELECT * FROM news_articles
                WHERE publish_time >= ?
                AND translated = 1
                AND ai_comment IS NOT NULL
                ORDER BY publish_time DESC
            """

            results = self.cursor.execute(query, (cutoff_time,)).fetchall()

            articles = []
            for row in results:
                articles.append(self._row_to_article(row))

            logger.info(f"从数据库读取最近 {days} 天的新闻: {len(articles)} 条")
            return articles

    def get_stats(self) -> dict:
        """
        获取数据库统计信息

        Returns:
            dict: 统计信息
        """
        with self:
            # 总文章数
            total = self.cursor.execute(
                "SELECT COUNT(*) FROM news_articles"
            ).fetchone()[0]

            # 按板块统计
            category_stats = self.cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM news_articles
                GROUP BY category
            """).fetchall()

            # 按语言统计
            language_stats = self.cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM news_articles
                GROUP BY language
            """).fetchall()

            # 已翻译数量
            translated = self.cursor.execute(
                "SELECT COUNT(*) FROM news_articles WHERE translated = 1"
            ).fetchone()[0]

            # 已生成AI评论数量
            with_comments = self.cursor.execute(
                "SELECT COUNT(*) FROM news_articles WHERE ai_comment IS NOT NULL"
            ).fetchone()[0]

            return {
                'total_articles': total,
                'category_stats': {row[0]: row[1] for row in category_stats},
                'language_stats': {row[0]: row[1] for row in language_stats},
                'translated_count': translated,
                'with_ai_comments': with_comments
            }

    def _row_to_article(self, row: sqlite3.Row) -> NewsArticle:
        """
        将数据库行转换为NewsArticle对象

        Args:
            row: 数据库行（sqlite3.Row对象）

        Returns:
            NewsArticle: 新闻文章对象
        """
        # 解析tags（从JSON字符串转为列表）
        import json
        tags = []
        if row['tags']:
            try:
                tags = json.loads(row['tags'])
            except:
                tags = []

        # 创建NewsArticle对象
        article = NewsArticle(
            id=row['id'],
            title=row['title'],
            title_original=row['title_original'],
            content=row['content'],
            content_original=row['content_original'],
            source=row['source'],
            source_original=row['source_original'],
            url=row['url'],
            category=Category(row['category']),
            language=Language(row['language']),
            publish_time=datetime.fromisoformat(row['publish_time']),
            crawl_time=datetime.fromisoformat(row['crawl_time']),
            tags=tags,
            ai_comment=row['ai_comment'],
            translated=bool(row['translated']),
            translation_method=row['translation_method'] or '',
            featured=bool(row['featured'])
        )

        return article

    # ========== 原始抓取数据临时表相关方法 ==========

    def _create_raw_articles_table(self):
        """
        创建原始抓取数据临时表

        该表用于存储抓取的原始数据，不进行去重和翻译
        """
        # 检查表是否已存在
        self.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='raw_articles'
        """)
        table_exists = self.cursor.fetchone() is not None

        if table_exists:
            logger.debug("原始数据临时表已存在")
            return

        # 创建临时表
        self.cursor.execute("""
            CREATE TABLE raw_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                title_original TEXT,
                content TEXT,
                content_original TEXT,
                source TEXT NOT NULL,
                source_original TEXT,
                url TEXT,
                category TEXT NOT NULL,
                language TEXT NOT NULL,
                publish_time TIMESTAMP,
                crawl_time TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        self.cursor.execute("""
            CREATE INDEX idx_raw_category ON raw_articles(category)
        """)

        self.cursor.execute("""
            CREATE INDEX idx_raw_source ON raw_articles(source)
        """)

        self.cursor.execute("""
            CREATE INDEX idx_raw_crawl_time ON raw_articles(crawl_time DESC)
        """)

        logger.info("✓ 原始数据临时表创建成功")

    def save_raw_article(self, article: NewsArticle) -> int:
        """
        保存新闻文章到原始数据临时表

        Args:
            article: 新闻文章对象

        Returns:
            int: 插入记录的ID
        """
        with self:
            query = """
                INSERT INTO raw_articles (
                    title, title_original, content, content_original,
                    source, source_original, url, category, language,
                    publish_time, crawl_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                article.title,
                article.title_original,
                article.content,
                article.content_original,
                article.source,
                article.source_original,
                article.url,
                article.category.value,
                article.language.value,
                article.publish_time.isoformat() if article.publish_time else None,
                article.crawl_time.isoformat()
            )

            self.cursor.execute(query, params)
            article_id = self.cursor.lastrowid

            logger.debug(f"原始文章已保存: ID={article_id}, source={article.source}, title={article.title_original or article.title[:50]}")
            return article_id

    def get_raw_articles(self, category: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
        """
        从临时表获取原始抓取数据

        Args:
            category: 板块筛选，None表示所有板块
            limit: 限制返回数量，None表示不限制

        Returns:
            List[dict]: 原始文章列表（字典格式）
        """
        with self:
            query = "SELECT * FROM raw_articles WHERE 1=1"
            params = []

            if category:
                query += " AND category = ?"
                params.append(category)

            query += " ORDER BY crawl_time DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            results = self.cursor.execute(query, params).fetchall()

            # 转为字典列表
            articles = []
            for row in results:
                articles.append(dict(row))

            return articles

    def get_raw_articles_count(self) -> int:
        """
        获取临时表中的记录数量

        Returns:
            int: 记录数量
        """
        with self:
            count = self.cursor.execute(
                "SELECT COUNT(*) FROM raw_articles"
            ).fetchone()[0]
            return count

    def clear_raw_articles(self):
        """
        清空原始数据临时表

        用于在处理完成后清空临时表
        """
        with self:
            self.cursor.execute("DELETE FROM raw_articles")
            deleted_count = self.cursor.rowcount
            logger.info(f"✓ 已清空临时表，删除了 {deleted_count} 条记录")

    def get_raw_stats(self) -> dict:
        """
        获取临时表的统计信息

        Returns:
            dict: 统计信息
        """
        with self:
            # 总记录数
            total = self.cursor.execute(
                "SELECT COUNT(*) FROM raw_articles"
            ).fetchone()[0]

            # 按板块统计
            category_stats = self.cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM raw_articles
                GROUP BY category
            """).fetchall()

            # 按来源统计
            source_stats = self.cursor.execute("""
                SELECT source, COUNT(*) as count
                FROM raw_articles
                GROUP BY source
            """).fetchall()

            # 按语言统计
            language_stats = self.cursor.execute("""
                SELECT language, COUNT(*) as count
                FROM raw_articles
                GROUP BY language
            """).fetchall()

            return {
                'total_articles': total,
                'category_stats': {row[0]: row[1] for row in category_stats},
                'source_stats': {row[0]: row[1] for row in source_stats},
                'language_stats': {row[0]: row[1] for row in language_stats}
            }

    # ========== 事务优化相关方法（v2.1新增）==========

    def begin_immediate_transaction(self):
        """
        开始IMMEDIATE事务（v2.1新增）

        IMMEDIATE事务会立即获取数据库写锁，防止并发冲突

        Returns:
            bool: 是否成功开始事务
        """
        try:
            self.cursor.execute("BEGIN IMMEDIATE")
            logger.debug("已开始IMMEDIATE事务")
            return True
        except Exception as e:
            logger.error(f"开始IMMEDIATE事务失败: {e}")
            return False

    def set_translating_lock(self, article_id: int) -> bool:
        """
        设置翻译锁（v2.1新增）

        使用原子操作设置translating锁，防止并发翻译

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功获取锁（True=获取成功，False=已被锁定）
        """
        query = """
            UPDATE raw_articles
            SET translating = 1,
                translation_locked_at = CURRENT_TIMESTAMP
            WHERE id = ? AND translating = 0
        """
        self.cursor.execute(query, (article_id,))
        success = self.cursor.rowcount > 0

        if success:
            logger.debug(f"成功获取翻译锁: article_id={article_id}")
        else:
            logger.debug(f"翻译锁已被占用: article_id={article_id}")

        return success

    def release_translating_lock(self, article_id: int) -> bool:
        """
        释放翻译锁（v2.1新增）

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功释放锁
        """
        query = "UPDATE raw_articles SET translating = 0 WHERE id = ?"
        self.cursor.execute(query, (article_id,))
        success = self.cursor.rowcount > 0

        if success:
            logger.debug(f"已释放翻译锁: article_id={article_id}")
        else:
            logger.warning(f"释放翻译锁失败: article_id={article_id}")

        return success

    def set_comment_generating_lock(self, article_id: int) -> bool:
        """
        设置AI评论生成锁（v2.1新增）

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功获取锁
        """
        query = """
            UPDATE raw_articles
            SET comment_generating = 1,
                comment_generating_locked_at = CURRENT_TIMESTAMP
            WHERE id = ? AND comment_generating = 0
        """
        self.cursor.execute(query, (article_id,))
        success = self.cursor.rowcount > 0

        if success:
            logger.debug(f"成功获取评论生成锁: article_id={article_id}")
        else:
            logger.debug(f"评论生成锁已被占用: article_id={article_id}")

        return success

    def release_comment_generating_lock(self, article_id: int) -> bool:
        """
        释放AI评论生成锁（v2.1新增）

        Args:
            article_id: 文章ID

        Returns:
            bool: 是否成功释放锁
        """
        query = "UPDATE raw_articles SET comment_generating = 0 WHERE id = ?"
        self.cursor.execute(query, (article_id,))
        success = self.cursor.rowcount > 0

        if success:
            logger.debug(f"已释放评论生成锁: article_id={article_id}")
        else:
            logger.warning(f"释放评论生成锁失败: article_id={article_id}")

        return success

    def save_translation_with_lock(
        self,
        article_id: int,
        translated_title: str,
        translated_content: str
    ) -> bool:
        """
        使用事务锁保存翻译结果（v2.1新增）

        完整的原子操作流程：
        1. 开始IMMEDIATE事务
        2. 尝试获取翻译锁
        3. 保存翻译结果
        4. 释放锁
        5. 提交事务

        Args:
            article_id: 文章ID
            translated_title: 翻译后的标题
            translated_content: 翻译后的内容

        Returns:
            bool: 是否成功保存
        """
        # 开始事务
        if not self.begin_immediate_transaction():
            return False

        try:
            # 获取锁
            if not self.set_translating_lock(article_id):
                self.conn.rollback()
                logger.info(f"翻译锁已被占用，跳过: article_id={article_id}")
                return False

            # 保存翻译
            query = """
                UPDATE raw_articles
                SET title = ?,
                    content = ?,
                    translated = 1,
                    translating = 0,
                    translation_method = 'claude',
                    translated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.cursor.execute(query, (translated_title, translated_content, article_id))
            success = self.cursor.rowcount > 0

            # 提交事务
            self.conn.commit()

            if success:
                logger.info(f"✓ 翻译已保存: article_id={article_id}")
            else:
                logger.warning(f"保存翻译失败: article_id={article_id}")

            return success

        except Exception as e:
            self.conn.rollback()
            logger.error(f"保存翻译时发生错误: {e}")
            return False

    def save_ai_comment_with_lock(
        self,
        article_id: int,
        ai_comment: str
    ) -> bool:
        """
        使用事务锁保存AI评论（v2.1新增）

        Args:
            article_id: 文章ID
            ai_comment: AI评论内容

        Returns:
            bool: 是否成功保存
        """
        # 开始事务
        if not self.begin_immediate_transaction():
            return False

        try:
            # 获取锁
            if not self.set_comment_generating_lock(article_id):
                self.conn.rollback()
                logger.info(f"评论生成锁已被占用，跳过: article_id={article_id}")
                return False

            # 保存评论
            query = """
                UPDATE raw_articles
                SET ai_comment = ?,
                    comment_generated = 1,
                    comment_generating = 0,
                    comment_method = 'claude',
                    comment_generated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            self.cursor.execute(query, (ai_comment, article_id))
            success = self.cursor.rowcount > 0

            # 提交事务
            self.conn.commit()

            if success:
                logger.info(f"✓ AI评论已保存: article_id={article_id}")
            else:
                logger.warning(f"保存AI评论失败: article_id={article_id}")

            return success

        except Exception as e:
            self.conn.rollback()
            logger.error(f"保存AI评论时发生错误: {e}")
            return False

    def get_locked_articles_count(self) -> dict:
        """
        获取锁定状态的统计（v2.1新增）

        Returns:
            dict: 锁定统计信息
        """
        with self:
            # 正在翻译的文章数
            translating = self.cursor.execute(
                "SELECT COUNT(*) FROM raw_articles WHERE translating = 1"
            ).fetchone()[0]

            # 正在生成评论的文章数
            comment_generating = self.cursor.execute(
                "SELECT COUNT(*) FROM raw_articles WHERE comment_generating = 1"
            ).fetchone()[0]

            return {
                'translating': translating,
                'comment_generating': comment_generating
            }
