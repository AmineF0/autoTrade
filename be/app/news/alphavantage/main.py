from api_rotator import APIKeyRotator
from stock_analyzer import StockNewsAnalyzer
from datetime import datetime
import pandas as pd
import os

def main():
    # Configuration
    API_KEYS = [
        "SU778HG0EYAA5PPN",
        "DU9EJJ9651DMN64Y",
        "CW4YB5WZT1SLZ5A1"
    ]
    BASE_URL = "https://www.alphavantage.co/query"

    # Initialize API rotator and stock analyzer
    api_rotator = APIKeyRotator(API_KEYS, BASE_URL)
    analyzer = StockNewsAnalyzer(api_rotator)

    tech_tickers = ['NVDA', 'AMD', 'INTC', 'AAPL']
    comparison = analyzer.compare_tickers_news(tech_tickers)
    nvidia_timeline = analyzer.get_sentiment_timeline('NVDA', days=7)
    top_articles = analyzer.get_top_articles('AAPL', n=3, sort_by='sentiment')
    tesla_news = analyzer.get_top_articles('TSLA', n=5, sort_by='recent')
    
    print("Comparison of news sentiment across tech tickers:")
    print(comparison)
    print("\nSentiment timeline for NVDA:")
    print(nvidia_timeline)
    print("\nTop articles for AAPL:")
    print(top_articles)
    print("\nTop articles for TSLA:")
    print(tesla_news)
    

if __name__ == "__main__":
    main()