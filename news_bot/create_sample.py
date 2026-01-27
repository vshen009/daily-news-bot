#!/usr/bin/env python3
"""生成HTML样本文件"""

import sys
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models import NewsArticle, Category, Language
from jinja2 import Environment, FileSystemLoader

def main():
    """生成HTML样本"""
    print("开始生成HTML样本...")

    # 创建测试数据
    articles = [
        NewsArticle(
            title='央行降息0.25个百分点 释放流动性约1万亿元',
            content='中国人民银行宣布下调金融机构存款准备金率0.25个百分点，释放长期资金约1万亿元，旨在降低实体经济融资成本。',
            source='新华社',
            url='https://example.com/1',
            category=Category.DOMESTIC,
            language=Language.ZH,
            publish_time=datetime.now(),
            crawl_time=datetime.now(),
            ai_comment='降准释放流动性，有助于降低实体经济融资成本，对债市和股市形成双重利好。'
        ),
        NewsArticle(
            title='证监会优化公募基金监管',
            content='证监会发布优化公募基金监管新规，进一步放宽产品注册限制，推动行业高质量发展。',
            source='财新网',
            url='https://example.com/2',
            category=Category.DOMESTIC,
            language=Language.ZH,
            publish_time=datetime.now(),
            crawl_time=datetime.now(),
            ai_comment='监管松绑助力公募行业高质量发展，产品创新将迎来新机遇。'
        ),
        NewsArticle(
            title='美联储维持利率不变',
            title_original='Fed Holds Rates Steady',
            content='The Federal Reserve kept interest rates unchanged on Wednesday, signaling confidence in economic growth. The decision was widely expected by markets.',
            content_original='The Federal Reserve kept interest rates unchanged on Wednesday, signaling confidence in economic growth. The decision was widely expected by markets.',
            source='Bloomberg',
            source_original='Bloomberg',
            url='https://example.com/3',
            category=Category.US_EUROPE,
            language=Language.EN,
            publish_time=datetime.now(),
            crawl_time=datetime.now(),
            translated=True,
            ai_comment='按兵不动符合预期，但点阵图显示年内仍有降息空间，市场对软着陆预期增强。'
        )
    ]

    # 渲染HTML
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('daily_news.html')
    html = template.render(
        date=datetime.now().strftime('%Y-%m-%d'),
        domestic_news=articles[:2],
        asia_news=[],
        useu_news=articles[2:]
    )

    # 保存HTML
    output_path = Path('output/样本.html')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ 样本HTML已生成: {output_path}")
    print(f"\n查看方式: 用浏览器打开即可（支持PC、Mac、手机等各种设备）")

if __name__ == "__main__":
    main()
