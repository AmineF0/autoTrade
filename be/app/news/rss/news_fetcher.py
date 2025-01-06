import feedparser
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import time
from typing import Dict, List, Optional, Union
import logging
from urllib.parse import urlparse
import json


class FinancialNewsFetcher:
    """A robust financial news fetcher that collects news from multiple RSS feeds"""
    
    def __init__(self):
        """Initialize the news fetcher"""
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Default RSS feeds - using a smaller, tested set
        self.default_feeds = {
            # 'Bloomberg - Markets': 'https://www.bloomberg.com/markets/rss',
            'CNBC': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
            # 'CNBC - Investing': 'https://www.cnbc.com/id/15839069/device/rss/rss.html',
            # 'CNBC - Markets': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            # 'Financial Times - Markets': 'https://www.ft.com/markets?format=rss',
        #    'Investing.com': 'https://www.investing.com/rss/news.rss',
            # 'Money - Markets': 'https://money.com/markets/feed/',
            # 'Money - Personal Finance': 'https://money.com/personal-finance/feed/',
            # 'Moneycontrol - News': 'https://www.moneycontrol.com/rss/latestnews.xml',
            # 'NerdWallet': 'https://www.nerdwallet.com/blog/feed/',
            # 'NerdWallet - Investing': 'https://www.nerdwallet.com/blog/investing/feed/',
            # 'Seeking Alpha': 'https://seekingalpha.com/feed.xml',
            # 'The Economist - Business': 'http://www.economist.com/feeds/print-sections/77/business.xml',
            # 'The Economist - Finance and Economics': 'http://www.economist.com/feeds/print-sections/79/finance-and-economics.xml',
            # 'The Motley Fool': 'https://www.fool.com/feeds/index.aspx',
            # 'The Wall Street Journal - Markets': 'https://feeds.a.dj.com/rss/RSSMarketsMain.xml',
        #    'Yahoo Finance': 'https://finance.yahoo.com/news/rssindex',
            # 'http://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms': 'http://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
        #    'https://feeds.content.dowjones.io/public/rss/mw_topstories': 'https://feeds.content.dowjones.io/public/rss/mw_topstories',
            # 'https://stockstotrade.com/blog/': 'https://stockstotrade.com/blog/',
            # 'https://tradebrains.in/blog/feed/': 'https://tradebrains.in/blog/feed/',
        #    'https://www.investing.com/rss/news_25.rss': 'https://www.investing.com/rss/news_25.rss'
        }
        
        # Initialize feeds dictionary with default feeds
        self.feeds = self.default_feeds.copy()

    def add_feed(self, name: str, url: str) -> None:
        """Add a new RSS feed to the fetcher"""
        try:
            result = urlparse(url)
            if all([result.scheme, result.netloc]):
                self.feeds[name] = url
                self.logger.info(f"Added new feed: {name}")
            else:
                raise ValueError("Invalid URL format")
        except Exception as e:
            self.logger.error(f"Error adding feed {name}: {str(e)}")
    
    def remove_feed(self, name: str) -> None:
        """Remove a feed from the fetcher"""
        if name in self.feeds:
            del self.feeds[name]
            self.logger.info(f"Removed feed: {name}")
    
    def reset_feeds(self) -> None:
        """Reset feeds to default list"""
        self.feeds = self.default_feeds.copy()
        self.logger.info("Reset feeds to default list")
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Safely parse dates from RSS feeds"""
        try:
            return parser.parse(date_str).replace(tzinfo=None)
        except Exception as e:
            self.logger.warning(f"Error parsing date {date_str}: {str(e)}")
            return None

    def fetch_all_feeds(self, 
                       start_date: Optional[Union[str, datetime]] = None,
                       end_date: Optional[Union[str, datetime]] = None,
                       sources: Optional[List[str]] = None) -> pd.DataFrame:
        """Fetch news from all configured RSS feeds with date filtering"""
        if isinstance(start_date, str):
            start_date = parser.parse(start_date)
        if isinstance(end_date, str):
            end_date = parser.parse(end_date)
        
        feeds_to_fetch = {k: v for k, v in self.feeds.items() 
                         if sources is None or k in sources}
        
        all_entries = []
        
        for source, url in feeds_to_fetch.items():
            try:
                self.logger.info(f"Fetching from {source}...")
                feed = feedparser.parse(url)
                
                # Add debug print
                self.logger.info(f"Feed status: {feed.status if hasattr(feed, 'status') else 'No status'}")
                self.logger.info(f"Number of entries: {len(feed.entries)}")
                
                for entry in feed.entries:
                    # Get all possible content fields
                    summary = entry.get('summary', '')
                    description = entry.get('description', '')
                    content = entry.get('content', [{}])[0].get('value', '') if 'content' in entry else ''
                    
                    # Choose the longest content available
                    full_content = max([summary, description, content], key=len)
                    
                    # Add debug print for first entry
                    if len(all_entries) == 0:
                        self.logger.info(f"Sample entry title: {entry.get('title', '')}")
                        self.logger.info(f"Sample entry content length: {len(full_content)}")
                    
                    news_item = {
                        'source': source,
                        'title': entry.get('title', ''),
                        'published': self.parse_date(entry.get('published', '')),
                        'summary': full_content,
                        'link': entry.get('link', ''),
                        'authors': ', '.join(author.get('name', '') for author in entry.get('authors', [])) if 'authors' in entry else '',
                        'categories': ', '.join(entry.get('tags', [])) if 'tags' in entry else '',
                        'guid': entry.get('guid', '')
                    }
                    all_entries.append(news_item)
                
                self.logger.info(f"Successfully fetched {len(feed.entries)} entries from {source}")
                time.sleep(1)  # Be nice to the servers
                
            except Exception as e:
                self.logger.error(f"Error fetching from {source}: {str(e)}")
                self.logger.error(f"Error details: {type(e).__name__}")  # Add error type
                
        # Add debug print for final results
        self.logger.info(f"Total entries collected: {len(all_entries)}")
        
        df = pd.DataFrame(all_entries)
        
        if not df.empty:
            df = df.dropna(subset=['published'])
            if start_date:
                df = df[df['published'] >= start_date]
            if end_date:
                df = df[df['published'] <= end_date]
            df = df.sort_values('published', ascending=False)
            
            # Add debug print for final dataframe
            self.logger.info(f"Final dataframe shape: {df.shape}")
        else:
            self.logger.warning("No entries were collected in the dataframe")
            
        return df   

    def get_news_by_keywords(self, 
                           keywords: List[str],
                           start_date: Optional[Union[str, datetime]] = None,
                           end_date: Optional[Union[str, datetime]] = None,
                           case_sensitive: bool = False) -> pd.DataFrame:
        """Get news filtered by keywords"""
        df = self.fetch_all_feeds(start_date, end_date)
        
        if df.empty:
            return df
        
        def contains_keywords(text):
            if text is None:
                return False
            if not case_sensitive:
                text = text.lower()
                keywords_lower = [k.lower() for k in keywords]
                return any(k in text for k in keywords_lower)
            return any(k in text for k in keywords)
        
        mask = df['title'].apply(contains_keywords)
        mask |= df['summary'].apply(contains_keywords)
        
        return df[mask]

    def to_json(self, df: pd.DataFrame, output_file: str = None, orient: str = 'records') -> str:
        """Convert news DataFrame to JSON format and optionally save to file"""
        df_copy = df.copy()
        if 'published' in df_copy.columns:
            df_copy['published'] = df_copy['published'].astype(str)
        
        json_str = df_copy.to_json(orient=orient, date_format='iso')
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json.loads(json_str), f, indent=2, ensure_ascii=False)
        
        return json_str