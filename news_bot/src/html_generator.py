"""HTML生成器"""

from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from pathlib import Path
from typing import List
from loguru import logger

from .models import NewsArticle, Category
from .config import Config


class HTMLGenerator:
    """HTML生成器"""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(Config.TEMPLATES_DIR),
            autoescape=True
        )
        # 添加自定义过滤器
        self.env.filters['zfill'] = lambda s, width: str(s).zfill(width)

    def generate(self, articles: List[NewsArticle], output_path: str = None, template_name: str = 'daily_news_modern.html'):
        """生成HTML文件"""

        # 为第一篇文章标记为featured
        if articles:
            articles[0].featured = True

        # 生成文件名（使用北京时间）
        date_str = Config.get_beijing_time().strftime(Config.DATE_FORMAT)
        filename = Config.OUTPUT_FILENAME_FORMAT.format(date=date_str)

        if not output_path:
            output_path = Config.OUTPUT_DIR / filename

        # 加载模板（使用现代化模板）
        template = self.env.get_template(template_name)

        # 渲染 - 使用单一articles列表
        html = template.render(
            date=date_str,
            articles=articles,
            total_articles=len(articles)
        )

        # 保存
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        logger.info(f"HTML已生成: {output_path}")
        logger.info(f"  总文章数: {len(articles)}")

        return output_path
