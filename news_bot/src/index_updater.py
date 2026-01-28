"""
自动更新首页index.html

功能：
1. 扫描public/目录下的所有HTML文件
2. 过滤出过去30天的新闻
3. 按日期倒序排列
4. 自动生成新闻卡片列表
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import sys

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import Config


class IndexUpdater:
    """首页更新器"""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.public_dir = project_root / "public"
        self.index_file = project_root / "public" / "index.html"

    def get_news_files(self, days: int = 30) -> list:
        """
        获取过去N天的新闻文件

        Args:
            days: 保留的天数，默认30天

        Returns:
            list: 新闻文件信息列表，按日期倒序
        """
        news_files = []

        # 检查public目录是否存在
        if not self.public_dir.exists():
            logger.warning(f"public目录不存在: {self.public_dir}")
            return news_files

        # 扫描所有HTML文件
        for file_path in self.public_dir.glob("*.html"):
            # 提取日期（文件名格式：YYYY-MM-DD.html）
            match = re.match(r'(\d{4}-\d{2}-\d{2})\.html', file_path.name)
            if not match:
                continue

            date_str = match.group(1)
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                # 检查是否在指定天数内（使用北京时间）
                cutoff_date = Config.get_beijing_time() - timedelta(days=days)
                if file_date >= cutoff_date:
                    # 读取标题
                    title = self._extract_title(file_path)

                    # 提取新闻数量
                    article_count = self._extract_article_count(file_path)

                    news_files.append({
                        'date': date_str,
                        'file_date': file_date,
                        'url': file_path.name,  # 相对于public/index.html的路径
                        'title': title,
                        'article_count': article_count
                    })

            except ValueError as e:
                logger.warning(f"日期解析失败: {file_path.name}, {e}")
                continue

        # 按日期倒序排列
        news_files.sort(key=lambda x: x['file_date'], reverse=True)

        return news_files

    def _extract_title(self, file_path: Path) -> str:
        """从HTML文件中提取标题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 尝试提取<h1>或<h2>标签内容
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
                if h1_match:
                    title = h1_match.group(1).strip()
                    # 移除HTML标签
                    title = re.sub(r'<[^>]+>', '', title)
                    if len(title) > 10:
                        return title[:100]  # 限制长度

                # 提取<title>标签
                title_match = re.search(r'<title>(.*?)</title>', content)
                if title_match:
                    title = title_match.group(1).strip()
                    if len(title) > 10:
                        return title[:100]

        except Exception as e:
            logger.warning(f"读取标题失败: {file_path.name}, {e}")

        # 默认标题
        return f"财经日报 - {file_path.stem}"

    def _extract_article_count(self, file_path: Path) -> int:
        """从HTML文件中提取新闻数量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 统计 <article class="news-card ..."> 的数量
                article_count = len(re.findall(r'<article[^>]*class="[^"]*news-card', content))

                if article_count > 0:
                    return article_count

        except Exception as e:
            logger.warning(f"读取新闻数量失败: {file_path.name}, {e}")

        # 如果无法提取，返回0
        return 0

    def update_index(self, days: int = 30) -> bool:
        """
        更新index.html

        Args:
            days: 保留的天数，默认30天

        Returns:
            bool: 是否成功更新
        """
        try:
            logger.info(f"开始更新首页（保留过去{days}天）")

            # 获取新闻文件列表
            news_files = self.get_news_files(days)

            if not news_files:
                logger.warning("没有找到符合条件的新闻文件")
                return False

            logger.info(f"找到{len(news_files)}个新闻文件")

            # 生成JavaScript数组
            news_list_js = self._generate_news_list_js(news_files)

            # 读取index.html模板
            if not self.index_file.exists():
                logger.error(f"index.html不存在: {self.index_file}")
                return False

            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换newsList数组
            pattern = r'const newsList = \[.*?\];'
            replacement = f'const newsList = [\n{news_list_js}\n        ];'

            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

            # 写回文件
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            logger.info(f"✓ 首页更新成功，包含{len(news_files)}天新闻")
            return True

        except Exception as e:
            logger.error(f"更新首页失败: {e}")
            return False

    def _generate_news_list_js(self, news_files: list) -> str:
        """生成JavaScript数组的字符串"""
        lines = []

        for news in news_files:
            date = news['date']
            url = news['url']
            title = news['title'].replace("'", "\\'").replace('"', '\\"')
            article_count = news.get('article_count', 0)

            lines.append(f"            {{")
            lines.append(f"                date: '{date}',")
            lines.append(f"                url: '{url}',")
            lines.append(f"                title: '{title}',")
            lines.append(f"                articleCount: {article_count}")
            lines.append(f"            }},")

        # 移除最后一个逗号
        if lines:
            lines[-1] = lines[-1].rstrip(',')

        return '\n'.join(lines)


def update_index_html(days: int = 30) -> bool:
    """
    更新index.html的便捷函数

    Args:
        days: 保留的天数，默认30天

    Returns:
        bool: 是否成功更新
    """
    updater = IndexUpdater()
    return updater.update_index(days)


if __name__ == "__main__":
    # 测试代码
    import sys
    from loguru import logger

    logger.remove()
    logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

    # 更新首页，保留30天
    success = update_index_html(days=30)

    if success:
        logger.info("✅ 首页更新完成")
    else:
        logger.error("❌ 首页更新失败")
        sys.exit(1)
