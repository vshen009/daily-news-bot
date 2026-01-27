"""数据模型定义"""

from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Category(str, Enum):
    """新闻板块"""
    GLOBAL = "global"               # 全球财经（统一分类）


class Language(str, Enum):
    """语言"""
    ZH = "zh"  # 中文
    EN = "en"  # 英文


class NewsArticle(BaseModel):
    """新闻文章数据模型"""

    # 数据库ID（用于判断是否已保存）
    id: Optional[int] = None

    # 基础信息
    title: str                       # 标题（中文）
    title_original: Optional[str] = None  # 原始标题（如果是英文）
    content: str                     # 摘要内容（中文）
    content_original: Optional[str] = None  # 原始内容（如果是英文）

    # 来源信息
    source: str                      # 媒体名称（中文）
    source_original: Optional[str] = None   # 原始媒体名称
    url: str                         # 文章链接
    category: Category               # 板块
    language: Language               # 语言

    # 时间信息
    publish_time: datetime           # 发布时间
    crawl_time: datetime             # 抓取时间

    # 标签
    tags: List[str] = []             # 标签

    # AI评论
    ai_comment: Optional[str] = None  # AI锐评

    # 翻译信息
    translated: bool = False         # 是否经过翻译
    translation_method: str = ""     # 翻译方式: "claude" / "deepl" / "google"

    # 显示标记
    featured: bool = False           # 是否为头条新闻

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NewsSource(BaseModel):
    """新闻源配置模型"""

    name: str                        # 中文名称
    english_name: str                # 英文名称
    url: str                         # 网站URL
    rss: Optional[str] = None        # RSS订阅地址
    language: Language               # 语言
    category: Category               # 板块
    priority: int = 5                # 优先级（1-10）
    enabled: bool = True             # 是否启用
    translate: bool = False          # 是否需要翻译
