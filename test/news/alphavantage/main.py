from api_rotator import APIKeyRotator
from stock_analyzer import StockNewsAnalyzer
from datetime import datetime
import pandas as pd
import os

def main():
    # Configuration
    API_KEYS = [
        "SU778HG0EYAA5PPN",
        "backup_key_1",
        "backup_key_2"
    ]
    BASE_URL = "https://www.alphavantage.co/query"

    # Initialize API rotator and stock analyzer
    api_rotator = APIKeyRotator(API_KEYS, BASE_URL)
    analyzer = StockNewsAnalyzer(api_rotator)

    # Example 1: Compare multiple tech stocks
    print("\n=== Tech Stocks Sentiment Comparison ===")
    tech_tickers = ['NVDA', 'AMD', 'INTC', 'AAPL']
    comparison = analyzer.compare_tickers_news(tech_tickers)
    print("\nTech Stock News Sentiment Comparison:")
    print(comparison)

    # Example 2: Detailed analysis of NVIDIA
    print("\n=== NVIDIA Detailed Analysis ===")
    nvidia_timeline = analyzer.get_sentiment_timeline('NVDA', days=7)
    print("\nNVIDIA Sentiment Timeline (Last 7 days):")
    print(nvidia_timeline)

    # Example 3: Top positive articles for Apple
    print("\n=== Apple Top Articles ===")
    top_articles = analyzer.get_top_articles('AAPL', n=3, sort_by='sentiment')
    print("\nTop Apple Articles by Sentiment:")
    print(top_articles)

    # Example 4: Recent news analysis for Tesla
    print("\n=== Tesla Recent News Analysis ===")
    tesla_news = analyzer.get_top_articles('TSLA', n=5, sort_by='recent')
    print("\nMost Recent Tesla Articles:")
    print(tesla_news)

if __name__ == "__main__":
    main()