"""配置管理"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
from typing import List

from .models import NewsSource

# 加载环境变量 - 明确指定.env文件路径
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


class Config:
    """全局配置"""

    # 项目路径
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / "config"
    OUTPUT_DIR = BASE_DIR.parent / "public"  # 输出到项目根目录的public（Vercel部署）
    LOGS_DIR = BASE_DIR / "logs"
    TEMPLATES_DIR = BASE_DIR / "templates"

    # 数据库配置
    DATABASE_DIR = BASE_DIR / "data"
    DATABASE_PATH = DATABASE_DIR / "news.db"

    # Claude API配置
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"  # 或 claude-3-5-haiku-20241022 (更便宜)

    # 翻译配置
    TRANSLATION_METHOD = "claude"  # claude / deepl / google
    MAX_CONTENT_LENGTH = 150      # 摘要最大长度

    # 抓取配置
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    REQUEST_TIMEOUT = 10          # 请求超时（秒）
    MAX_RETRIES = 3               # 最大重试次数

    # 新闻筛选
    TOP_NEWS_COUNT = 15           # 总共筛选TOP新闻数量
    MAX_AGE_HOURS = 48            # 新闻最大时效（小时）

    # 输出配置
    OUTPUT_FILENAME_FORMAT = "{date}.html"
    DATE_FORMAT = "%Y-%m-%d"

    @classmethod
    def load_sources(cls) -> List[NewsSource]:
        """加载新闻源配置"""
        config_file = cls.CONFIG_DIR / "sources.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        sources = []
        for item in data.get('sources', []):
            if item.get('enabled', False):
                source = NewsSource(**item)
                sources.append(source)

        return sources

    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """验证配置"""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("未设置 ANTHROPIC_API_KEY 环境变量")

        if errors:
            raise ValueError("配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors))
