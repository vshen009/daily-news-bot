"""AI评论生成器 - 使用Claude API"""

import anthropic
from typing import Optional
from loguru import logger

from .models import NewsArticle
from .config import Config


class AICommentGenerator:
    """AI评论生成器"""

    def __init__(self):
        if not Config.ANTHROPIC_API_KEY:
            raise ValueError("未设置 ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(
            api_key=Config.ANTHROPIC_API_KEY,
            base_url=Config.ANTHROPIC_BASE_URL
        )

    def generate_comment(self, article: NewsArticle) -> str:
        """为新闻生成AI评论"""
        logger.info(f"生成AI评论: {article.title[:30]}...")

        try:
            prompt = self._build_prompt(article)

            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            comment = response.content[0].text.strip()

            logger.info(f"AI评论生成成功: {comment[:30]}...")

            return comment

        except Exception as e:
            logger.error(f"AI评论生成失败: {e}")
            return ""

    def _build_prompt(self, article: NewsArticle) -> str:
        """构建Prompt"""

        prompt = f"""你是一位资深金融分析师，请为以下新闻撰写一句专业评论（30-50字）。

## 新闻标题：
{article.title}

## 新闻摘要：
{article.content}

## 评论要求：
1. 使用金融专业术语（如：存量博弈、货币政策、风险溢价、carry trade等）
2. 揭示背后的逻辑和影响
3. 提供前瞻性判断
4. 一句话，30-50字

## 示例风格：
输入："日本央行维持利率不变"
输出："按兵不动符合市场预期，但上调通胀预期暗示日央行对可持续通胀回归的信心增强，下半年加息预期升温将支撑日元汇率。"

输入："基金行业费率改革持续深化"
输出："费率战本质是存量博弈下的价格竞争，长期看将推动行业向规模效应和投研能力分化，中小公司生存压力加剧。"

## 请撰写评论（只输出评论，不要解释）："""

        return prompt


def generate_comments(articles: list) -> list:
    """批量生成AI评论"""
    generator = AICommentGenerator()

    for article in articles:
        if not article.ai_comment:
            try:
                comment = generator.generate_comment(article)
                article.ai_comment = comment
            except Exception as e:
                logger.error(f"生成评论失败: {e}")
                article.ai_comment = ""

    return articles


def generate_comment(article: NewsArticle) -> str:
    """为单条新闻生成AI评论"""
    generator = AICommentGenerator()
    return generator.generate_comment(article)
