"""
新闻去重模块

实现板块内去重和跨板块去重逻辑，确保每个板块都有足够的新闻。
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def deduplicate_by_title(articles: List[dict]) -> List[dict]:
    """
    在单个板块内去重

    规则：
    1. 英文新闻：根据 title_original 去重
    2. 中文新闻：根据 title 去重
    3. 保留最新的一条（按 crawl_time）

    Args:
        articles: 同一板块的新闻列表

    Returns:
        去重后的新闻列表
    """
    if not articles:
        return []

    seen = {}  # {dedupe_key: article}

    for article in articles:
        # 确定去重键
        if article.get('language') == 'en':
            key = article.get('title_original', '')
        else:
            key = article.get('title', '')

        # 如果键为空，跳过
        if not key:
            logger.warning(f"标题为空，跳过: {article.get('url', '')}")
            continue

        # 保留最新的一条（按 crawl_time）
        if key not in seen:
            # 第一次遇到，直接保存
            seen[key] = article
        else:
            # 已经存在，比较时间
            existing_article = seen[key]
            existing_time = existing_article.get('crawl_time', '')
            current_time = article.get('crawl_time', '')

            if current_time > existing_time:
                # 当前文章更新，替换
                seen[key] = article
                logger.debug(f"更新新闻: {key[:50]}")

    return list(seen.values())


def cross_category_deduplicate(
    grouped_articles: Dict[str, List[dict]]
) -> Tuple[Dict[str, List[dict]], Dict[str, List[dict]]]:
    """
    跨板块全局去重（核心改进 ⭐）

    规则：
    1. 基于 title_original + url 判断是否为同一条新闻
    2. 保留第一次出现的板块
    3. 删除后续板块中的重复

    板块优先级：
    - domestic (国内) > asia_pacific (亚太) > us_europe (美欧)

    Args:
        grouped_articles: 按板块分组的新闻字典

    Returns:
        (去重后的分组新闻, 每个板块的候补新闻)
    """
    seen = {}  # {(title_original, url): (article, category)}
    deduped = {
        'domestic': [],
        'asia_pacific': [],
        'us_europe': []
    }
    backup = {
        'domestic': [],      # 候补新闻（被跨板块去重删除的）
        'asia_pacific': [],
        'us_europe': []
    }

    # 按板块顺序处理（优先级：domestic > asia_pacific > us_europe）
    category_order = ['domestic', 'asia_pacific', 'us_europe']

    for category in category_order:
        articles = grouped_articles.get(category, [])

        for article in articles:
            # 构建唯一键
            if article.get('language') == 'en':
                key = (article.get('title_original', ''), article.get('url', ''))
            else:
                key = (article.get('title', ''), article.get('url', ''))

            # 检查是否已存在
            if key not in seen:
                # 第一次出现，保留
                seen[key] = (article, category)
                deduped[category].append(article)
            else:
                # 重复新闻，记录为候补
                existing_article, existing_category = seen[key]
                backup[existing_category].append(article)

                title_preview = article.get('title', article.get('title_original', ''))[:50]
                logger.info(f"跨板块去重: {title_preview} (已存在于 {existing_category})")

    return deduped, backup


def fill_top_10(
    deduped_articles: Dict[str, List[dict]],
    backup_articles: Dict[str, List[dict]],
    top_n: int = 10
) -> Dict[str, List[dict]]:
    """
    填充每个板块到TOP 10（如果不足10条）

    规则：
    1. 每个板块必须有 top_n 条新闻
    2. 如果不足 top_n 条，从候补新闻中补齐
    3. 候补新闻按关键词评分排序

    Args:
        deduped_articles: 去重后的分组新闻
        backup_articles: 候补新闻
        top_n: 每个板块的目标数量（默认10）

    Returns:
        填充后的分组新闻
    """
    # 延迟导入避免循环依赖
    from news_bot.src.scorer import calculate_priority_score

    final = {}

    for category in ['domestic', 'asia_pacific', 'us_europe']:
        articles = deduped_articles.get(category, [])
        backup = backup_articles.get(category, [])

        # 如果已有 top_n 条，直接使用
        if len(articles) >= top_n:
            final[category] = articles[:top_n]
            logger.info(f"{category}: {len(articles)}条（已满{top_n}条）")
        else:
            # 不足 top_n 条，需要补齐
            needed = top_n - len(articles)
            logger.info(f"{category}: 只有{len(articles)}条，从候补中补齐{needed}条")

            # 从候补新闻中选择评分最高的
            if backup:
                backup_sorted = sorted(
                    backup,
                    key=lambda x: calculate_priority_score(x),
                    reverse=True
                )
                articles.extend(backup_sorted[:needed])

            final[category] = articles

            logger.info(f"{category}: 补齐后共{len(final[category])}条")

    return final


def remove_duplicates_by_url(
    articles: List[dict],
    seen_urls: set = None
) -> Tuple[List[dict], set]:
    """
    基于URL去重（简单版本）

    用于快速过滤明显的重复新闻。

    Args:
        articles: 新闻列表
        seen_urls: 已见过的URL集合

    Returns:
        (去重后的新闻, 更新后的URL集合)
    """
    if seen_urls is None:
        seen_urls = set()

    unique_articles = []

    for article in articles:
        url = article.get('url', '')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
        elif not url:
            # 没有URL的新闻也保留
            unique_articles.append(article)

    return unique_articles, seen_urls


# 测试代码
if __name__ == "__main__":
    # 模拟数据
    test_articles_domestic = [
        {
            'id': 1,
            'title': '央行降息0.25个百分点',
            'title_original': '',
            'language': 'zh',
            'crawl_time': '2026-01-26 18:00:00',
            'url': 'http://example.com/1'
        },
        {
            'id': 2,
            'title': '央行降息0.25个百分点',  # 重复标题
            'title_original': '',
            'language': 'zh',
            'crawl_time': '2026-01-26 18:12:00',  # 更新的时间
            'url': 'http://example.com/1'
        },
        {
            'id': 3,
            'title': '央行宣布降息25个基点',  # 不同表述
            'title_original': '',
            'language': 'zh',
            'crawl_time': '2026-01-26 18:15:00',
            'url': 'http://example.com/3'
        },
    ]

    # 测试板块内去重
    print("测试板块内去重:")
    deduped = deduplicate_by_title(test_articles_domestic)
    print(f"  去重前: {len(test_articles_domestic)}条")
    print(f"  去重后: {len(deduped)}条")
    for article in deduped:
        print(f"    - {article['title']} (crawl_time: {article['crawl_time']})")

    # 测试跨板块去重
    test_grouped = {
        'domestic': [
            {
                'id': 1,
                'title': '国内新闻A',
                'language': 'zh',
                'url': 'http://example.com/a'
            }
        ],
        'asia_pacific': [
            {
                'id': 2,
                'title': '日本央行维持利率不变',
                'title_original': 'BOJ Keeps Rate Unchanged',
                'language': 'en',
                'url': 'http://example.com/b'
            },
            {
                'id': 3,
                'title': '亚太新闻B',
                'language': 'zh',
                'url': 'http://example.com/c'
            }
        ],
        'us_europe': [
            {
                'id': 4,
                'title': '美联储可能降息',
                'title_original': 'Fed Signals Rate Cuts',
                'language': 'en',
                'url': 'http://example.com/b'  # 重复URL
            },
            {
                'id': 5,
                'title': '美股新闻D',
                'language': 'zh',
                'url': 'http://example.com/d'
            }
        ]
    }

    print("\n测试跨板块去重:")
    deduped, backup = cross_category_deduplicate(test_grouped)
    print(f"  domestic: {len(deduped['domestic'])}条")
    print(f"  asia_pacific: {len(deduped['asia_pacific'])}条")
    print(f"  us_europe: {len(deduped['us_europe'])}条")
    print(f"  backup-asia_pacific: {len(backup['asia_pacific'])}条候补")

    # 测试填充TOP 10
    print("\n测试填充TOP 10:")
    filled = fill_top_10(deduped, backup, top_n=10)
    for category, articles in filled.items():
        print(f"  {category}: {len(articles)}条")
