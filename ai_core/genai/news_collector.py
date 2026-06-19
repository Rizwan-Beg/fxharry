"""Financial news ingestion pipeline using RSS feeds."""

from __future__ import annotations

import asyncio
import time
from typing import List, Dict, Any, Optional
import feedparser
from ai_core.core.logger import get_logger

logger = get_logger(__name__)


class NewsCollector:
    """Fetch and normalize market-moving news articles from RSS feeds."""

    def __init__(self, feed_urls: Optional[List[str]] = None):
        """Initialize news collector with RSS feeds."""
        # By default, use Yahoo Finance Forex news or generic market news
        # In production, use high-quality feeds like ForexLive or Investing.com
        self.feed_urls = feed_urls or [
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=EURUSD=X,GBPUSD=X,JPY=X",
            "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664" # CNBC Finance
        ]
        logger.info(f"NewsCollector initialized with {len(self.feed_urls)} feeds")

    async def fetch_latest(self, limit_per_feed: int = 5) -> List[Dict[str, Any]]:
        """Fetch latest news articles from configured sources asynchronously."""
        articles = []
        
        for url in self.feed_urls:
            try:
                # feedparser.parse is blocking, so we run it in an executor
                loop = asyncio.get_running_loop()
                feed = await loop.run_in_executor(None, feedparser.parse, url)
                
                if feed.bozo:
                    logger.warning(f"Error parsing feed {url}: {feed.bozo_exception}")
                    continue
                    
                for entry in feed.entries[:limit_per_feed]:
                    articles.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.get("title", "Unknown Source"),
                        "timestamp": time.time()
                    })
            except Exception as e:
                logger.error(f"Failed to fetch news from {url}: {e}")
                
        # Sort by most recent (rough sort based on index if timestamp string parsing is complex)
        # We just return them for now.
        logger.info(f"NewsCollector fetched {len(articles)} articles.")
        return articles

    async def fetch_by_symbol(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Fetch news articles and filter for a specific trading symbol."""
        all_articles = await self.fetch_latest(limit_per_feed=10)
        
        # Simple keyword filtering based on symbol (e.g., EURUSD -> EUR, USD, Europe, Fed)
        keywords = []
        if symbol == "EURUSD":
            keywords = ["EUR", "USD", "Euro", "Dollar", "ECB", "Fed", "Powell", "Lagarde"]
        elif symbol == "GBPUSD":
            keywords = ["GBP", "USD", "Pound", "Dollar", "BOE", "Fed"]
        elif symbol == "USDJPY":
            keywords = ["JPY", "USD", "Yen", "Dollar", "BOJ", "Fed"]
        else:
            keywords = [symbol[:3], symbol[3:], "Market", "Economy"]
            
        filtered = []
        for article in all_articles:
            text = f"{article['title']} {article['summary']}".upper()
            if any(k.upper() in text for k in keywords):
                filtered.append(article)
                
        # If filtering is too strict and yields nothing, return the top general news
        if not filtered:
            return all_articles[:limit]
            
        return filtered[:limit]
