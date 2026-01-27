"""
查看数据库信息
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from news_bot.src.database import DatabaseManager


def show_database_info():
    """显示数据库信息"""
    db_path = Path("data/news.db")
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    try:
        print("=" * 60)
        print("数据库信息")
        print("=" * 60)

        # 数据库文件大小
        file_size = db_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        print(f"数据库文件大小: {file_size:,} bytes ({size_mb:.2f} MB)")

        print("\n" + "-" * 60)

        # raw_articles统计
        print("\n【原始数据表 raw_articles】")
        raw_stats = db_manager.get_raw_stats()
        print(f"总记录数: {raw_stats['total_articles']}")
        print(f"\n按板块分布:")
        for category, count in raw_stats['category_stats'].items():
            print(f"  - {category}: {count}条")
        print(f"\n按来源分布:")
        for source, count in list(raw_stats['source_stats'].items())[:10]:
            print(f"  - {source}: {count}条")
        print(f"\n按语言分布:")
        for lang, count in raw_stats['language_stats'].items():
            print(f"  - {lang}: {count}条")

        print("\n" + "-" * 60)

        # news_articles统计
        print("\n【正式数据表 news_articles】")
        news_stats = db_manager.get_stats()
        print(f"总记录数: {news_stats['total_articles']}")
        print(f"\n按板块分布:")
        for category, count in news_stats['category_stats'].items():
            print(f"  - {category}: {count}条")
        print(f"\n已翻译: {news_stats['translated_count']}条")
        print(f"已生成AI评论: {news_stats['with_ai_comments']}条")

        print("\n" + "-" * 60)

        # 显示前10条新闻（最新）
        print("\n【最新的10条新闻】")
        articles = db_manager.get_all_articles(limit=10)

        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article.title}")
            print(f"   来源: {article.source}")
            print(f"   板块: {article.category.value}")
            print(f"   语言: {article.language.value}")
            print(f"   发布时间: {article.publish_time}")
            print(f"   翻译: {'✅' if article.translated else '❌'}")
            print(f"   AI评论: {'✅' if article.ai_comment else '❌'}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db_manager.close()


if __name__ == "__main__":
    show_database_info()
