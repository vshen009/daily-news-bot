"""
显示数据库中所有新闻
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from news_bot.src.database import DatabaseManager


def show_all_articles():
    """显示所有新闻"""
    db_path = Path("data/news.db")
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    try:
        print("=" * 80)
        print("数据库中所有新闻")
        print("=" * 80)

        # 获取所有文章
        articles = db_manager.get_all_articles()

        print(f"\n总记录数: {len(articles)}条")
        print("\n" + "-" * 80)

        # 按板块分组显示
        by_category = {
            'domestic': [],
            'asia_pacific': [],
            'us_europe': []
        }

        for article in articles:
            category = article.category.value
            if category in by_category:
                by_category[category].append(article)

        # 显示每个板块的新闻
        for category in ['domestic', 'asia_pacific', 'us_europe']:
            articles_in_category = by_category[category]
            print(f"\n{'=' * 80}")
            print(f"板块: {category.upper()} ({len(articles_in_category)}条)")
            print('=' * 80)

            for i, article in enumerate(articles_in_category, 1):
                print(f"\n{i}. 【{article.source}】{article.title}")
                print(f"   原文: {article.title_original or '无'}")
                print(f"   发布时间: {article.publish_time}")
                print(f"   语言: {article.language.value}")
                print(f"   翻译: {'✅ 是' if article.translated else '❌ 否'}")
                print(f"   AI评论: {'✅ 有' if article.ai_comment else '❌ 无'}")
                if article.ai_comment:
                    print(f"   评论内容: {article.ai_comment}")

        print("\n" + "=" * 80)
        print(f"总计: {len(articles)}条新闻")
        print("=" * 80)

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db_manager.close()


if __name__ == "__main__":
    show_all_articles()
