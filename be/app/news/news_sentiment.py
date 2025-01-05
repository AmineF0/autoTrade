from .rss.news_fetcher import FinancialNewsFetcher
from .rss.sentiment_analyzer import FinancialSentimentAnalyzer
from datetime import datetime, timedelta
import logging

from .alphavantage.api_rotator import APIKeyRotator
from .alphavantage.stock_analyzer import StockNewsAnalyzer


class NewsSentimentAnalyzer:
  
    API_KEYS = [
        "SU778HG0EYAA5PPN",
        "DU9EJJ9651DMN64Y",
        "CW4YB5WZT1SLZ5A1"
    ]
    BASE_URL = "https://www.alphavantage.co/query"
    
    keywords= {
    'AAPL': ['Apple', 'Apple stock', 'AAPL ticker', 'NASDAQ:AAPL', 'Apple earnings', 'Apple dividend', 'Apple market cap', 'Apple revenue', 'technology sector', 'consumer electronics', 'FAANG stocks', 'Apple quarterly reports'],
    'AMZN': ['Amazon', 'Amazon stock', 'AMZN ticker', 'NASDAQ:AMZN', 'Amazon earnings', 'Amazon revenue', 'Amazon market cap', 'e-commerce sector', 'AWS growth', 'FAANG stocks', 'Amazon quarterly reports', 'retail sector'],
    'GOOGL': ['Google', 'Google stock', 'Alphabet stock', 'GOOGL ticker', 'NASDAQ:GOOGL', 'Alphabet earnings', 'Alphabet revenue', 'Google market cap', 'advertising revenue', 'FAANG stocks', 'technology sector', 'Alphabet quarterly reports'],
    'MSFT': ['Microsoft', 'Microsoft stock', 'MSFT ticker', 'NASDAQ:MSFT', 'Microsoft earnings', 'Microsoft revenue', 'Microsoft market cap', 'cloud computing growth', 'enterprise software', 'technology sector', 'Microsoft quarterly reports', 'Azure revenue'],
    'TSLA': ['Tesla', 'Tesla stock', 'TSLA ticker', 'NASDAQ:TSLA', 'Tesla earnings', 'Tesla revenue', 'Tesla market cap', 'electric vehicles sector', 'renewable energy', 'Elon Musk leadership', 'Tesla quarterly reports', 'automotive sector'],
    'NVDA': ['Nvidia', 'Nvidia stock', 'NVDA ticker', 'NASDAQ:NVDA', 'Nvidia earnings', 'Nvidia revenue', 'Nvidia market cap', 'semiconductor sector', 'graphics processing units', 'artificial intelligence', 'Nvidia quarterly reports', 'data center growth']
    }
    
    cache = {}

    
    def __init__(self, stocks=['AAPL', 'AMZN', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']):
        self.logger = logging.getLogger(__name__)
        self.fetcher = FinancialNewsFetcher()
        self.analyzer = FinancialSentimentAnalyzer()
        self.api_rotator = APIKeyRotator(self.API_KEYS, self.BASE_URL)
        self.stock_analyzer = StockNewsAnalyzer(self.api_rotator)
        self.stocks = stocks
        
    def get_rss_sentiment_stock(self, stock:str, days:int=60):
        news = self.fetcher.get_news_by_keywords(
            keywords=[stock] + self.keywords[stock],
            start_date=datetime.now() - timedelta(days=days),
        )
        print(news)
        tech_news_with_sentiment = self.analyzer.analyze_dataframe(news)
        tech_sentiment_summary = self.analyzer.get_sentiment_summary(tech_news_with_sentiment)

        return tech_sentiment_summary
      
    def get_alphavantage_sentiment_stock(self, stock:str, days:int=7):
        return self.stock_analyzer.get_sentiment_timeline(stock, days)
      
    def compare_sentiment_stocks(self, stocks:list=None, days:int=45, force=False):
        
        if not force and "rss_sentiments" in self.cache:
            return self.cache["rss_sentiments"], self.cache["comparison"]
        
        if not stocks:
            stocks = self.stocks
            
        rss_sentiments = {}
        # alphavantage_sentiments = {}
        comparison = self.stock_analyzer.compare_tickers_news(stocks)

        for stock in stocks:
            rss_sentiments[stock] = self.get_rss_sentiment_stock(stock, days)
            # alphavantage_sentiments[stock] = self.get_alphavantage_sentiment_stock(stock, days)
            
        self.cache["rss_sentiments"] = rss_sentiments
        # cache["alphavantage_sentiments"] = alphavantage_sentiments
        self.cache["comparison"] = comparison
        
        return rss_sentiments, comparison
      

def main():
    analyzer = NewsSentimentAnalyzer()
    rss_sentiments, comparison = analyzer.compare_sentiment_stocks()
    
    print("RSS Sentiments:")
    print(rss_sentiments)
    
    print("Comparison:")
    print(comparison)

if __name__ == "__main__":
    main()