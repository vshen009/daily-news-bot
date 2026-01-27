"""新闻抓取器"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger

from .models import NewsArticle, NewsSource
from .config import Config
from .utils import parse_timestamp, normalize_to_utc


class NewsScraper:
    """新闻抓取器"""

    def __init__(self, source: NewsSource):
        self.source = source

    def fetch(self) -> List[NewsArticle]:
        """抓取新闻"""
        logger.info(f"开始抓取: {self.source.name}")

        articles = []

        # 优先使用RSS
        if self.source.rss:
            articles = self._fetch_from_rss()
        else:
            articles = self._fetch_from_html()

        logger.info(f"从 {self.source.name} 抓取到 {len(articles)} 条新闻")

        return articles

    def _fetch_from_rss(self) -> List[NewsArticle]:
        """从RSS抓取"""
        articles = []

        try:
            # 获取RSS Feed
            feed = feedparser.parse(self.source.rss)

            for entry in feed.entries[:20]:  # 限制最多20条
                try:
                    # 提取信息
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')
                    summary = entry.get('summary', entry.get('description', ''))

                    # 清理HTML标签
                    summary = self._clean_html(summary)

                    # 提取发布时间（使用v2.1时间处理工具）
                    crawl_time = datetime.now()

                    # 优先使用published_parsed，否则使用published原始字符串
                    published = entry.get('published_parsed')
                    if published:
                        publish_time = datetime(*published[:6])
                        # 统一转换为UTC（v2.1新增）
                        publish_time = normalize_to_utc(publish_time)
                    else:
                        # 尝试解析原始时间字符串（v2.1新增）
                        published_raw = entry.get('published', '')
                        if published_raw:
                            try:
                                publish_time = parse_timestamp(published_raw)
                                publish_time = normalize_to_utc(publish_time)
                            except Exception as e:
                                logger.debug(f"时间解析失败，使用crawl_time: {e}")
                                publish_time = crawl_time
                        else:
                            # 保底：使用crawl_time（v2.1新增）
                            publish_time = crawl_time

                    # 检查时效性
                    if self._is_too_old(publish_time):
                        continue

                    # 创建文章对象
                    # 对于英文新闻：title留空，title_original保存原文
                    # 对于中文新闻：title直接使用，title_original为None
                    article = NewsArticle(
                        title=title if self.source.language == "zh" else "",
                        title_original=title if self.source.language == "en" else None,
                        content=self._truncate_content(summary) if self.source.language == "zh" else "",
                        content_original=summary if self.source.language == "en" else None,
                        source=self.source.name,
                        source_original=self.source.english_name,
                        url=url,
                        category=self.source.category,
                        language=self.source.language,
                        publish_time=publish_time,
                        crawl_time=crawl_time,  # 使用统一定义的crawl_time
                        translated=False
                    )

                    articles.append(article)

                except Exception as e:
                    logger.warning(f"解析RSS条目失败: {e}")
                    continue

        except Exception as e:
            logger.error(f"RSS抓取失败 {self.source.name}: {e}")

        return articles

    def _fetch_from_html(self) -> List[NewsArticle]:
        """从HTML抓取（备用方案）"""
        articles = []

        try:
            headers = {'User-Agent': Config.USER_AGENT}
            response = requests.get(
                self.source.url,
                headers=headers,
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # 这里需要根据不同网站的HTML结构来解析
            # 暂时跳过，后续可以扩展
            logger.warning(f"HTML抓取暂未实现: {self.source.name}")

        except Exception as e:
            logger.error(f"HTML抓取失败 {self.source.name}: {e}")

        return articles

    def _clean_html(self, html: str) -> str:
        """清理HTML标签"""
        if not html:
            return ""

        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        # 移除多余空白
        text = ' '.join(text.split())

        return text

    def _truncate_content(self, content: str, max_length: int = 300) -> str:
        """截断内容到指定长度"""
        if len(content) <= max_length:
            return content

        # 在截断点附近找到句号
        truncated = content[:max_length]
        last_period = truncated.rfind('。')

        if last_period > max_length * 0.7:  # 如果句号位置合理
            return truncated[:last_period + 1]

        return truncated + "……"

    def _is_too_old(self, publish_time: datetime) -> bool:
        """检查新闻是否过期"""
        age = datetime.now() - publish_time
        return age > timedelta(hours=Config.MAX_AGE_HOURS)


def fetch_all_sources() -> List[NewsArticle]:
    """抓取所有新闻源"""
    Config.validate()
    sources = Config.load_sources()

    all_articles = []

    for source in sources:
        try:
            scraper = NewsScraper(source)
            articles = scraper.fetch()
            all_articles.extend(articles)
        except Exception as e:
            logger.error(f"抓取 {source.name} 失败: {e}")
            continue

    logger.info(f"总共抓取 {len(all_articles)} 条新闻")

    return all_articles
