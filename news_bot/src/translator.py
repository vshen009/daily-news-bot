"""翻译模块 - 使用Claude API"""

import anthropic
from typing import Optional
from loguru import logger

from .models import NewsArticle
from .config import Config


class Translator:
    """Claude翻译器"""

    def __init__(self):
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("未设置 ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(
            api_key=Config.ANTHROPIC_API_KEY,
            base_url=Config.ANTHROPIC_BASE_URL
        )

    def translate_article(self, article: NewsArticle) -> NewsArticle:
        """翻译文章"""
        if article.language == "zh":
            # 中文新闻无需翻译
            return article

        logger.info(f"翻译文章: {article.title_original}")

        try:
            # 翻译标题（即使内容为空也要翻译标题）
            title_zh = self._translate_text(
                article.title_original,
                "title"
            )

            # 检查正文是否为空
            if not article.content_original or len(article.content_original.strip()) == 0:
                logger.warning(f"文章正文为空，仅翻译标题: {article.title_original}")
                article.title = title_zh
                article.title_original = article.title_original  # 保留原文
                article.content = "英文文章本身内容为空因此没有翻译"
                article.content_original = article.content_original  # 保留原文
                article.translated = True
                article.translation_method = "claude"
                return article

            # 翻译摘要
            content_zh = self._translate_text(
                article.content_original,
                "summary"
            )

            # 更新文章
            article.title = title_zh
            article.title_original = article.title_original  # 保留原文
            article.content = content_zh
            article.content_original = article.content_original  # 保留原文
            article.translated = True
            article.translation_method = "claude"

            logger.info(f"翻译完成: {title_zh}")

        except Exception as e:
            logger.error(f"翻译失败: {e}")
            # 翻译失败时保留原文
            article.title = article.title_original or article.title
            article.content = article.content_original or article.content

        return article

    def _translate_text(self, text: str, context: str = "general") -> str:
        """翻译文本"""

        if context == "title":
            prompt = self._get_title_translation_prompt(text)
            max_tokens = 100
        else:  # summary
            prompt = self._get_summary_translation_prompt(text)
            max_tokens = 500

        try:
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            translated = response.content[0].text.strip()

            return translated

        except Exception as e:
            logger.error(f"Claude API调用失败: {e}")
            raise

    def _get_title_translation_prompt(self, title: str) -> str:
        """获取标题翻译Prompt"""
        return f"""你是一位专业的金融新闻翻译。请将以下英文新闻标题翻译成地道的中文。

## 要求：
1. 保持金融专业性，准确翻译金融术语
2. 标题简洁有力（不超过30字）
3. 只根据原文翻译，不要补充背景或改写
4. 符合中文新闻表达习惯

## 常用术语对照：
- Central Bank: 央行
- Interest Rate: 利率
- Inflation: 通胀/通货膨胀
- Federal Reserve: 美联储
- Treasury Yield: 国债收益率

## 原标题：
{title}

## 翻译（只输出翻译结果，不要解释）："""

    def _get_summary_translation_prompt(self, content: str) -> str:
        """获取摘要翻译Prompt"""
        return f"""你是一位专业的金融新闻翻译。请将以下英文新闻摘要翻译成地道的中文，并在不新增事实的前提下适度扩写。

## 要求：
1. 保持金融专业性，准确翻译金融术语
2. 只基于原文信息进行扩写，不引入新事实、新数据、新机构或新人物
3. 允许适度改写与串联，但不得概括或省略原文要点
4. 译文长度控制在150字以内，优先120字左右
5. 不要增删事实与数据
6. 符合中文新闻表达习惯
7. 保留关键数据、机构名称、人名

## 原文：
{content}

## 翻译（只输出翻译结果，不要解释）："""


def translate_articles(articles: list) -> list:
    """批量翻译文章"""
    translator = Translator()

    translated_articles = []

    for article in articles:
        if article.language == "en" and not article.translated:
            try:
                translated = translator.translate_article(article)
                translated_articles.append(translated)
            except Exception as e:
                logger.error(f"翻译文章失败: {e}")
                # 翻译失败时添加原文
                translated_articles.append(article)
        else:
            # 无需翻译的文章
            translated_articles.append(article)

    return translated_articles
