"""HTML生成器"""

from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from loguru import logger
import re

from .models import NewsArticle, Category
from .config import Config
from .database import utc_to_beijing


def simple_markdown(text):
    """
    简单的 Markdown 格式转换
    支持：**粗体** 和 *斜体*
    """
    if not text:
        return text

    # 转换 **粗体** 为 <strong>
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # 转换 *斜体* 为 <em>
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    return text


def format_beijing_time(utc_dt: datetime, format_str: str = "%Y-%m-%d %H:%M") -> str:
    """
    将UTC时间格式化为北京时间字符串

    Args:
        utc_dt: UTC时间对象
        format_str: 格式化字符串，默认 "YYYY-MM-DD HH:MM"

    Returns:
        str: 格式化后的北京时间字符串
    """
    if not utc_dt:
        return ""

    beijing_dt = utc_to_beijing(utc_dt)
    return beijing_dt.strftime(format_str)


def format_relative_time(utc_dt: datetime) -> str:
    """
    将UTC时间转换为相对时间描述（中文）

    Args:
        utc_dt: UTC时间对象

    Returns:
        str: 相对时间字符串，如 "2小时前"、"昨天"
    """
    if not utc_dt:
        return ""

    now = datetime.utcnow()
    delta = now - utc_dt
    beijing_dt = utc_to_beijing(utc_dt)

    # 小于1小时
    if delta.total_seconds() < 3600:
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes}分钟前" if minutes > 0 else "刚刚"

    # 小于24小时
    if delta.total_seconds() < 86400:
        hours = int(delta.total_seconds() / 3600)
        return f"{hours}小时前"

    # 小于48小时，显示"昨天"
    if delta.total_seconds() < 172800:
        return f"昨天 {beijing_dt.strftime('%H:%M')}"

    # 其他情况显示日期
    return beijing_dt.strftime("%m-%d %H:%M")


def format_beijing_iso(utc_dt: datetime) -> str:
    """
    将UTC时间转换为北京时间ISO格式字符串

    Args:
        utc_dt: UTC时间对象

    Returns:
        str: 北京时间的ISO格式字符串
    """
    if not utc_dt:
        return ""
    beijing_dt = utc_to_beijing(utc_dt)
    return beijing_dt.isoformat()


class HTMLGenerator:
    """HTML生成器"""

    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(Config.TEMPLATES_DIR),
            autoescape=True
        )
        # 添加自定义过滤器
        self.env.filters['zfill'] = lambda s, width: str(s).zfill(width)
        self.env.filters['simple_markdown'] = simple_markdown
        self.env.filters['beijing_time'] = format_beijing_time
        self.env.filters['beijing_iso'] = format_beijing_iso
        self.env.filters['relative_time'] = format_relative_time

    def generate(self, articles: List[NewsArticle], output_path: str = None, template_name: str = 'daily_news.html'):
        """生成HTML文件"""

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
