"""LLM-powered market news analyzer."""

from __future__ import annotations

import json
import os
import time
from typing import List, Dict, Any
from ai_core.core.logger import get_logger
from .news_collector import NewsCollector

logger = get_logger(__name__)


class NewsAnalyzer:
    """Aggregate and score financial news using LLMs."""

    def __init__(self):
        """Initialize news analyzer with collector."""
        self.collector = NewsCollector()
        self._client = None
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        logger.info("NewsAnalyzer initialized")
        
    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise RuntimeError("openai package not installed.")

        api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("API key is not set in environment.")

        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        return self._client

    async def analyze(self, articles: List[Dict[str, Any]], symbol: str = "EURUSD") -> Dict[str, Any]:
        """Analyze news articles and return aggregated sentiment and insights."""
        if not articles:
            return {
                "sentiment": "NEUTRAL",
                "score": 0.0,
                "summary": "No recent news available.",
                "headlines": [],
                "timestamp": time.time()
            }
            
        headlines = [f"- {a['title']} ({a['source']})" for a in articles]
        headlines_text = "\n".join(headlines)

        prompt = f"""You are an expert financial news sentiment analyzer.
Analyze the following recent headlines for the trading symbol {symbol}.

HEADLINES:
{headlines_text}

Determine the overall macroeconomic sentiment for {symbol}.
Return ONLY valid JSON with no markdown formatting.

{{
  "sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
  "score": <float between -1.0 (extremely bearish) and 1.0 (extremely bullish)>,
  "summary": "<1-2 sentence summary of the news impact on {symbol}>"
}}
"""

        try:
            client = self._get_client()
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial news AI. Always respond with raw JSON only."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
            )

            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()

            result = json.loads(raw)
            
            # Attach the headlines we analyzed
            result["headlines"] = [a['title'] for a in articles]
            result["articles"] = articles
            result["timestamp"] = time.time()
            
            logger.info(f"📰 News Sentiment for {symbol}: {result.get('sentiment')} ({result.get('score')})")
            return result
            
        except Exception as e:
            logger.error(f"News sentiment analysis failed: {e}")
            return {
                "sentiment": "NEUTRAL",
                "score": 0.0,
                "summary": f"Analysis failed: {str(e)[:100]}",
                "headlines": [a['title'] for a in articles],
                "articles": articles,
                "timestamp": time.time()
            }

    async def analyze_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """Fetch and analyze news for a specific symbol."""
        articles = await self.collector.fetch_by_symbol(symbol)
        return await self.analyze(articles, symbol)
