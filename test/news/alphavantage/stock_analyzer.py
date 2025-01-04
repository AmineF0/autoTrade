import pandas as pd
from typing import List, Dict, Optional, Union
from datetime import datetime, timedelta
import numpy as np
from pprint import pprint

class StockNewsAnalyzer:
    def __init__(self, api_rotator: 'APIKeyRotator'):
        """
        Initialize the Stock News Analyzer with an API key rotator
        
        Args:
            api_rotator: Instance of APIKeyRotator class for handling API requests
        """
        self.api_rotator = api_rotator
        self.news_cache = {}  # Cache for storing news data
        self.cache_duration = timedelta(hours=1)  # Cache duration
        self.cache_timestamps = {}  # Timestamps for cached data

    def fetch_news(self, ticker: str) -> Optional[Dict]:
        """
        Fetch news for a given ticker symbol with caching
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dict containing news data if successful, None otherwise
        """
        # Check cache first
        if ticker in self.news_cache:
            if datetime.now() - self.cache_timestamps[ticker] < self.cache_duration:
                return self.news_cache[ticker]

        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker,
            "sort": "RELEVANCE"
        }
        
        response = self.api_rotator.make_request("", params)
        
        if response:
            self.news_cache[ticker] = response
            self.cache_timestamps[ticker] = datetime.now()
            return response
        return None

    def news_to_dataframe(self, news_data: Dict) -> pd.DataFrame:
        """
        Convert news feed to a pandas DataFrame
        
        Args:
            news_data: Raw news data from API
            
        Returns:
            DataFrame containing processed news data
        """
        if not news_data or 'feed' not in news_data:
            return pd.DataFrame()
        
        news_list = []
        for item in news_data['feed']:
            news_list.append({
                'time_published': item['time_published'],
                'title': item['title'],
                'summary': item['summary'],
                'source': item['source'],
                'url': item.get('url', ''),
                'overall_sentiment_score': item.get('overall_sentiment_score', 0),
                'overall_sentiment_label': item.get('overall_sentiment_label', 'neutral'),
                'ticker_sentiment': item.get('ticker_sentiment', [])
            })
        
        df = pd.DataFrame(news_list)
        if not df.empty:
            df['time_published'] = pd.to_datetime(df['time_published'])
            df = df.sort_values('time_published', ascending=False)
        return df

    def analyze_sentiment_distribution(self, df: pd.DataFrame) -> Dict:
        """
        Analyze the distribution of sentiment in news articles
        
        Args:
            df: DataFrame containing news data
            
        Returns:
            Dict containing sentiment analysis statistics
        """
        if df.empty:
            return {
                'average_sentiment': 0,
                'sentiment_counts': pd.Series(),
                'max_sentiment': None,
                'min_sentiment': None
            }

        sentiment_stats = {
            'average_sentiment': df['overall_sentiment_score'].mean(),
            'sentiment_counts': df['overall_sentiment_label'].value_counts(),
            'max_sentiment': df.loc[df['overall_sentiment_score'].idxmax()],
            'min_sentiment': df.loc[df['overall_sentiment_score'].idxmin()],
            'sentiment_std': df['overall_sentiment_score'].std(),
            'recent_sentiment_trend': df.head(5)['overall_sentiment_score'].mean()
        }
        
        return sentiment_stats

    def compare_tickers_news(self, tickers: List[str]) -> pd.DataFrame:
        """
        Compare news sentiment across multiple tickers
        
        Args:
            tickers: List of stock ticker symbols
            
        Returns:
            DataFrame containing comparison of news sentiment across tickers
        """
        results = {}
        for ticker in tickers:
            news = self.fetch_news(ticker)
            if news and 'feed' in news:
                df = self.news_to_dataframe(news)
                if not df.empty:
                    sentiment_analysis = self.analyze_sentiment_distribution(df)
                    results[ticker] = {
                        'article_count': len(df),
                        'avg_sentiment': sentiment_analysis['average_sentiment'],
                        'recent_sentiment': sentiment_analysis['recent_sentiment_trend'],
                        'sentiment_std': sentiment_analysis['sentiment_std'],
                        'latest_article_time': df['time_published'].max(),
                        'most_common_sentiment': sentiment_analysis['sentiment_counts'].index[0]
                    }
        
        return pd.DataFrame(results).T

    def get_sentiment_timeline(self, ticker: str, days: int = 7) -> pd.DataFrame:
        """
        Get sentiment timeline for a specific ticker
        
        Args:
            ticker: Stock ticker symbol
            days: Number of days to analyze
            
        Returns:
            DataFrame containing daily sentiment aggregates
        """
        news = self.fetch_news(ticker)
        if not news:
            return pd.DataFrame()

        df = self.news_to_dataframe(news)
        if df.empty:
            return df

        df['date'] = df['time_published'].dt.date
        cutoff_date = datetime.now().date() - timedelta(days=days)
        df = df[df['date'] >= cutoff_date]

        daily_sentiment = df.groupby('date').agg({
            'overall_sentiment_score': ['mean', 'std', 'count'],
            'overall_sentiment_label': lambda x: x.mode()[0] if not x.empty else 'neutral'
        }).reset_index()

        return daily_sentiment

    def get_top_articles(self, ticker: str, n: int = 5, sort_by: str = 'sentiment') -> pd.DataFrame:
        """
        Get top n articles for a ticker based on specified criteria
        
        Args:
            ticker: Stock ticker symbol
            n: Number of articles to return
            sort_by: Criteria to sort by ('sentiment' or 'recent')
            
        Returns:
            DataFrame containing top articles
        """
        news = self.fetch_news(ticker)
        if not news:
            return pd.DataFrame()

        df = self.news_to_dataframe(news)
        if df.empty:
            return df

        if sort_by == 'sentiment':
            return df.nlargest(n, 'overall_sentiment_score')[
                ['time_published', 'title', 'source', 'overall_sentiment_score', 'url']
            ]
        else:  # sort by recent
            return df.nlargest(n, 'time_published')[
                ['time_published', 'title', 'source', 'overall_sentiment_score', 'url']
            ]