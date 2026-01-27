#!/usr/bin/env python3
"""简化版运行脚本 - 不使用loguru"""

import sys
import os
from pathlib import Path

# 设置临时目录
os.environ['TMPDIR'] = '/tmp'

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config
from src.scraper import fetch_all_sources
from src.translator import translate_articles
from src.ai_comment import generate_comments
from src.html_generator import HTMLGenerator
from src.models import Category


def main():
    """主函数"""
    print("=" * 60)
    print("新闻抓取系统启动")
    print("=" * 60)

    try:
        # 1. 验证配置
        print("\n步骤1: 配置验证")
        Config.validate()
        print("✓ 配置验证通过")

        # 2. 抓取新闻
        print("\n步骤2: 抓取新闻...")
        all_articles = fetch_all_sources()
        print(f"✓ 抓取到 {len(all_articles)} 条新闻")

        if not all_articles:
            print("警告：没有抓取到任何新闻")
            return

        # 3. 翻译
        print("\n步骤3: 翻译英文新闻...")
        translated_articles = translate_articles(all_articles)
        print("✓ 翻译完成")

        # 4. 筛选TOP新闻
        print("\n步骤4: 筛选重要新闻...")
        domestic = [a for a in translated_articles if a.category == Category.DOMESTIC]
        asia = [a for a in translated_articles if a.category == Category.ASIA_PACIFIC]
        useu = [a for a in translated_articles if a.category == Category.US_EUROPE]

        domestic.sort(key=lambda x: x.publish_time, reverse=True)
        asia.sort(key=lambda x: x.publish_time, reverse=True)
        useu.sort(key=lambda x: x.publish_time, reverse=True)

        top_news = []
        top_news.extend(domestic[:5])
        top_news.extend(asia[:5])
        top_news.extend(useu[:5])

        print(f"✓ 筛选出 {len(top_news)} 条重要新闻")

        # 5. 生成AI评论
        print("\n步骤5: 生成AI评论...")
        articles_with_comments = generate_comments(top_news)
        print("✓ AI评论生成完成")

        # 6. 生成HTML
        print("\n步骤6: 生成HTML...")
        generator = HTMLGenerator()
        output_path = generator.generate(articles_with_comments)
        print(f"✓ HTML已生成: {output_path}")

        print("\n" + "=" * 60)
        print("✓ 所有任务完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
