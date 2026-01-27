"""
新闻评分模块

根据关键词和优先级规则计算新闻得分，包含v2.1改进的得分上限机制。
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


# 通用关键词配置
HIGH_PRIORITY_KEYWORDS = {
    'zh': [
        '央行', '美联储', '欧洲央行', '日本央行', '英国央行',
        '利率', '降息', '加息', '基准利率', '负利率',
        'gdp', '国内生产总值', '经济增速', '经济衰退',
        '通胀', '通货膨胀', 'cpi', '消费者物价', '通缩',
        '财政政策', '货币政策', '量化宽松', '缩表', 'qe'
    ],
    'en': [
        'central bank', 'ecb', 'boj', 'bank of england',
        'interest rate', 'rate cut', 'rate hike', 'benchmark rate', 'negative rate',
        'gdp', 'economic growth', 'recession',
        'inflation', 'cpi', 'deflation',
        'monetary policy', 'fiscal policy', 'qe', 'balance sheet reduction'
    ]
}

MEDIUM_PRIORITY_KEYWORDS = {
    'zh': [
        '股市', '大盘', '指数', '涨跌', '震荡',
        '上证指数', '深证成指', '标普500', '纳斯达克',
        '道琼斯', '日经指数', '恒生指数',
        '牛市', '熊市', '反弹', '回调',
        '财报', '营收', '利润', '季度', '年报',
        '并购', '收购', 'ipo', '上市', '退市',
        'ceo', '高管', '董事会', '股东大会',
        '油价', '黄金', '白银', '铜', '铝',
        '原油', '期货', '大宗商品'
    ],
    'en': [
        'stock market', 'index', 'rally', 'drop', 'volatility',
        's&p 500', 'nasdaq', 'dow jones',
        'nikkei', 'hang seng', 'ftse',
        'bull market', 'bear market', 'rebound', 'correction',
        'earnings', 'revenue', 'profit', 'quarterly', 'annual report',
        'm&a', 'acquisition', 'ipo', 'listing', 'delisting',
        'ceo', 'executive', 'board of directors', 'shareholder meeting',
        'oil price', 'gold', 'silver', 'copper', 'aluminum',
        'crude oil', 'futures', 'commodities'
    ]
}

# 板块特有关键词（加分规则）
CATEGORY_KEYWORDS = {
    'domestic': {
        'zh': ['中国', '内地', '国内', '全国', '大陆', '国务院', '证监会', '银保监会'],
        'en': ['china', 'chinese', 'mainland', 'domestic', 'state council', 'pboc', 'csrc'],
        'bonus': 10
    },
    'asia_pacific': {
        'zh': ['日本', '韩国', '印度', '澳大利亚', '亚太', '亚洲', '东盟'],
        'en': ['japan', 'korea', 'india', 'australia', 'asia-pacific', 'asia', 'asean'],
        'bonus': 10
    },
    'us_europe': {
        'zh': ['美国', '美利坚', '美股', '华尔街', '美联储', '欧洲', '欧盟', '欧元'],
        'en': ['us', 'usa', 'united states', 'america', 'wall street', 'fed', 'europe', 'eu', 'euro'],
        'bonus': 15
    }
}


def calculate_priority_score(article: dict, category: str = None) -> int:
    """
    计算新闻的优先级得分（v2.0改进版 ⭐）

    改进点：
    1. 设置关键词得分上限，防止SEO堆砌
    2. 标题匹配得分上限：+40分（最多2个高优先级关键词）
    3. 内容匹配得分上限：+20分（最多1个高优先级关键词）
    4. 总分上限：60分（避免垃圾新闻高分）

    Args:
        article: 新闻文章字典
        category: 板块分类（可选，用于额外加分）

    Returns:
        int: 优先级得分（0-60）
    """
    # 提取标题和内容
    if article.get('language') == 'en':
        title = (article.get('title_original') or article.get('title') or '').lower()
        content = (article.get('content_original') or article.get('content') or '').lower()
        lang = 'en'
    else:
        title = (article.get('title') or '').lower()
        content = (article.get('content') or '').lower()
        lang = 'zh'

    score = 10  # 基础分

    # 高优先级关键词（标题+20，内容+10）
    high_keywords = HIGH_PRIORITY_KEYWORDS.get(lang, [])

    # ⭐ 标题匹配：最多2个关键词，上限+40分
    title_high_count = 0
    for keyword in high_keywords:
        if keyword in title:
            score += 20
            title_high_count += 1
            if title_high_count >= 2:  # 最多2个关键词
                break

    # ⭐ 内容匹配：最多1个关键词，上限+10分
    content_high_count = 0
    for keyword in high_keywords:
        if keyword in content:
            score += 10
            content_high_count += 1
            if content_high_count >= 1:  # 最多1个关键词
                break

    # 中优先级关键词（标题+10，内容+5）
    medium_keywords = MEDIUM_PRIORITY_KEYWORDS.get(lang, [])

    # ⭐ 标题匹配：最多2个关键词，上限+20分
    title_medium_count = 0
    for keyword in medium_keywords:
        if keyword in title:
            score += 10
            title_medium_count += 1
            if title_medium_count >= 2:  # 最多2个关键词
                break

    # ⭐ 内容匹配：最多1个关键词，上限+5分
    content_medium_count = 0
    for keyword in medium_keywords:
        if keyword in content:
            score += 5
            content_medium_count += 1
            if content_medium_count >= 1:  # 最多1个关键词
                break

    # 板块特有关键词额外加分
    if category:
        category_config = CATEGORY_KEYWORDS.get(category, {})
        category_keywords = category_config.get(lang, [])
        category_bonus = category_config.get('bonus', 0)

        for keyword in category_keywords:
            if keyword in title or keyword in content:
                score += category_bonus
                break

    # ⭐ 总分上限：60分（避免SEO堆砌）
    return min(score, 60)


def classify_by_score(score: int) -> str:
    """
    根据得分分类优先级

    Args:
        score: 优先级得分

    Returns:
        str: 优先级类别 ('high', 'medium', 'low')
    """
    if score >= 50:
        return 'high'
    elif score >= 30:
        return 'medium'
    else:
        return 'low'


def select_top_news(
    articles: List[dict],
    category: str,
    top_n: int = 10
) -> List[dict]:
    """
    根据优先级得分筛选TOP N新闻

    策略：
    1. 计算每条新闻的优先级得分
    2. 按优先级分组（高/中/低）
    3. 每组内按时间排序
    4. 按比例选择（高:中:低 = 5:3:2）
    5. 最终总数为 top_n

    Args:
        articles: 新闻列表
        category: 板块分类
        top_n: 要选择的新闻数量

    Returns:
        精选的新闻列表
    """
    if not articles:
        return []

    if len(articles) <= top_n:
        return articles

    # 第1步：计算每条新闻的优先级得分
    scored_articles = []
    for article in articles:
        score = calculate_priority_score(article, category)
        scored_articles.append({
            'article': article,
            'score': score,
            'priority': classify_by_score(score),
            'publish_time': article.get('publish_time', '')
        })

    # 第2步：按优先级分组
    high_priority = []   # 得分 >= 50
    medium_priority = [] # 得分 30-49
    low_priority = []    # 得分 < 30

    for item in scored_articles:
        if item['priority'] == 'high':
            high_priority.append(item)
        elif item['priority'] == 'medium':
            medium_priority.append(item)
        else:
            low_priority.append(item)

    # 第3步：每组内按时间排序（最新的在前）
    for group in [high_priority, medium_priority, low_priority]:
        group.sort(key=lambda x: x['publish_time'], reverse=True)

    # 第4步：按比例选择（高:中:低 = 5:3:2）
    high_count = int(top_n * 0.5)    # 5条
    medium_count = int(top_n * 0.3)  # 3条
    low_count = top_n - high_count - medium_count  # 2条

    selected = []
    selected.extend([item['article'] for item in high_priority[:high_count]])
    selected.extend([item['article'] for item in medium_priority[:medium_count]])
    selected.extend([item['article'] for item in low_priority[:low_count]])

    # 如果某组数量不足，从其他组补充
    if len(selected) < top_n:
        # 按优先级和时间顺序补充
        remaining = scored_articles
        remaining.sort(key=lambda x: (x['score'], x['publish_time']), reverse=True)

        for item in remaining:
            if item['article'] not in selected:
                selected.append(item['article'])
                if len(selected) >= top_n:
                    break

    logger.info(f"{category}: 筛选 {len(articles)} → {len(selected)} (高:{len(high_priority)}, 中:{len(medium_priority)}, 低:{len(low_priority)})")

    return selected


# 测试代码
if __name__ == "__main__":
    # 测试正常新闻
    test_articles = [
        {
            'title': '中国央行宣布降息0.25个百分点，提振股市',
            'title_original': '',
            'content': '中国人民银行宣布降息25个基点',
            'language': 'zh'
        },
        {
            'title': '美联储暗示降息',
            'title_original': 'Fed Signals Rate Cuts Coming in 2026',
            'content': 'The Federal Reserve signaled potential rate cuts',
            'language': 'en'
        },
        {
            'title': '股市上涨 大盘指数反弹',
            'title_original': '',
            'content': '今日股市表现良好',
            'language': 'zh'
        },
        {
            'title': '广告推广免责声明',
            'title_original': '',
            'content': '这是一条广告',
            'language': 'zh'
        }
    ]

    print("测试评分系统:")
    for article in test_articles:
        score = calculate_priority_score(article, 'domestic')
        priority = classify_by_score(score)
        title = article.get('title', article.get('title_original', ''))[:50]
        print(f"  {title:50} 得分: {score:2d} ({priority})")

    # 测试SEO堆砌
    seo_spam = {
        'title': '央行央行央行降息降息降息加息加息股市股市股市股市',
        'content': '',
        'language': 'zh'
    }
    score = calculate_priority_score(seo_spam)
    print(f"\nSEO堆砌测试: {score:2d} (应该有上限)")

    # 测试筛选
    print("\n测试TOP 10筛选:")
    selected = select_top_news(test_articles * 3, 'domestic', top_n=10)
    print(f"  筛选结果: {len(selected)}条")
