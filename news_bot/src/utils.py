"""
时间处理工具函数

用于处理RSS源的时间字段，解决格式混乱和缺失问题。
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def get_effective_publish_time(article: dict) -> datetime:
    """
    获取有效的发布时间（v2.0新增）

    保底逻辑：
    1. 优先使用publish_time
    2. 如果publish_time为空或无效，使用crawl_time
    3. 记录日志便于后续分析

    Args:
        article: 新闻文章字典，包含publish_time和crawl_time

    Returns:
        datetime对象：有效的发布时间（UTC时区）
    """
    # 尝试解析publish_time
    publish_time = article.get('publish_time')

    if publish_time:
        try:
            # 解析时间戳
            parsed_time = parse_timestamp(publish_time)
            normalized = normalize_to_utc(parsed_time)
            logger.debug(f"使用publish_time: {normalized}")
            return normalized
        except Exception as e:
            logger.warning(f"publish_time解析失败: {publish_time}, 错误: {e}")

    # 保底：使用crawl_time
    crawl_time = article.get('crawl_time')
    if crawl_time:
        try:
            parsed_time = parse_timestamp(crawl_time)
            normalized = normalize_to_utc(parsed_time)
            title_preview = article.get('title', article.get('title_original', ''))[:50]
            logger.info(f"⚠️ publish_time缺失，使用crawl_time: {title_preview}")
            return normalized
        except Exception as e:
            logger.error(f"crawl_time解析失败: {crawl_time}, 错误: {e}")

    # 极端情况：两者都缺失
    title_preview = article.get('title', article.get('title_original', ''))[:50]
    logger.error(f"❌ 时间字段完全缺失: {title_preview}")
    return datetime.now(timezone.utc)


def parse_timestamp(time_str: str) -> datetime:
    """
    解析多种时间格式（v2.0新增）

    支持的格式：
    - RFC 3339: "2026-01-26T18:00:00Z"
    - ISO 8601: "2026-01-26T18:00:00+08:00"
    - 标准格式: "2026-01-26 18:00:00"
    - RSS格式: "Fri, 26 Jan 2026 18:00:00 +0000"

    Args:
        time_str: 时间字符串

    Returns:
        datetime对象

    Raises:
        ValueError: 如果无法解析时间格式
    """
    if not time_str or not isinstance(time_str, str):
        raise ValueError(f"无效的时间字符串: {time_str}")

    # 清理时间字符串
    time_str = time_str.strip()

    # 定义支持的时间格式
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",           # RFC 3339 (UTC)
        "%Y-%m-%dT%H:%M:%S.%fZ",         # RFC 3339 (带毫秒)
        "%Y-%m-%dT%H:%M:%S%z",          # ISO 8601 (时区)
        "%Y-%m-%dT%H:%M:%S.%f%z",        # ISO 8601 (带毫秒和时区)
        "%Y-%m-%dT%H:%M:%S",            # ISO 8601 (无时区)
        "%Y-%m-%dT%H:%M:%S.%f",          # ISO 8601 (带毫秒，无时区)
        "%Y-%m-%d %H:%M:%S",            # 标准格式
        "%Y-%m-%d %H:%M:%S.%f",          # 标准格式 (带毫秒)
        "%a, %d %b %Y %H:%M:%S %z",     # RSS格式 (RFC 2822)
        "%a, %d %b %Y %H:%M:%S %Z",     # RSS格式 (时区名称)
        "%d %b %Y %H:%M:%S %z",         # 简化的RSS格式
        "%d %b %Y %H:%M:%S %Z",         # 简化的RSS格式 (时区名称)
    ]

    # 尝试每种格式
    for fmt in formats:
        try:
            parsed = datetime.strptime(time_str, fmt)
            return parsed
        except ValueError:
            continue

    # 所有格式都失败
    raise ValueError(f"无法解析时间格式: {time_str}")


def normalize_to_utc(time_obj: datetime) -> datetime:
    """
    归一化到UTC时区（v2.0新增）

    为什么需要：
    - 不同RSS源使用不同时区
    - 需要统一到UTC进行比较

    Args:
        time_obj: datetime对象

    Returns:
        datetime对象（UTC时区，不带tzinfo以兼容现有代码）
    """
    if time_obj.tzinfo is None:
        # 无时区信息，假设为UTC
        return time_obj.replace(tzinfo=timezone.utc).replace(tzinfo=None)

    # 有时区信息，转换为UTC后去掉tzinfo
    return time_obj.astimezone(timezone.utc).replace(tzinfo=None)


def is_within_24_hours(article: dict, current_time: Optional[datetime] = None) -> bool:
    """
    检查新闻是否在24小时内

    Args:
        article: 新闻文章字典
        current_time: 当前时间（默认为现在）

    Returns:
        bool: 是否在24小时内
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    try:
        publish_time = get_effective_publish_time(article)
        time_diff = (current_time - publish_time).total_seconds()
        hours_diff = time_diff / 3600

        return -24 <= hours_diff <= 24  # 允许未来1小时的时间误差
    except Exception as e:
        logger.error(f"检查24小时失败: {e}")
        return False


def format_time_for_display(time_obj: datetime, timezone_str: str = 'Asia/Shanghai') -> str:
    """
    格式化时间用于显示

    Args:
        time_obj: UTC时间对象
        timezone_str: 目标时区（默认北京时间）

    Returns:
        str: 格式化的时间字符串
    """
    try:
        # 转换到目标时区
        import pytz
        target_tz = pytz.timezone(timezone_str)
        local_time = time_obj.astimezone(target_tz)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    except ImportError:
        # 如果没有pytz，直接返回UTC时间
        return time_obj.strftime("%Y-%m-%d %H:%M:%S UTC")


# 测试代码
if __name__ == "__main__":
    # 测试parse_timestamp
    test_times = [
        "2026-01-26T18:00:00Z",
        "2026-01-26T18:00:00+08:00",
        "2026-01-26 18:00:00",
        "Fri, 26 Jan 2026 18:00:00 +0000",
    ]

    print("测试时间解析:")
    for time_str in test_times:
        try:
            parsed = parse_timestamp(time_str)
            normalized = normalize_to_utc(parsed)
            print(f"  {time_str:45} → {normalized}")
        except Exception as e:
            print(f"  {time_str:45} → 错误: {e}")

    # 测试get_effective_publish_time
    print("\n测试保底逻辑:")
    test_articles = [
        {
            'title': '正常新闻',
            'publish_time': '2026-01-26T10:00:00Z',
            'crawl_time': '2026-01-26 18:00:00'
        },
        {
            'title': 'publish_time缺失',
            'publish_time': None,
            'crawl_time': '2026-01-26 18:00:00'
        },
        {
            'title': 'publish_time格式错误',
            'publish_time': 'Invalid Date',
            'crawl_time': '2026-01-26 18:00:00'
        },
    ]

    for article in test_articles:
        effective_time = get_effective_publish_time(article)
        print(f"  {article['title']:30} → {effective_time}")
