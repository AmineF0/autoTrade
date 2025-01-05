from news_fetcher import FinancialNewsFetcher
from sentiment_analyzer import FinancialSentimentAnalyzer
from datetime import datetime, timedelta
import logging
import json
import os
def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Create output directory
    # output_dir = setup_output_directory()

    # Initialize the fetcher and sentiment analyzer
    fetcher = FinancialNewsFetcher()
    analyzer = FinancialSentimentAnalyzer()
    
    try:
        # Example 1: Fetch recent news
        logger.info("Fetching recent news from all sources...")
        start_date = datetime.now() - timedelta(days=2)
        recent_news = fetcher.fetch_all_feeds(start_date=start_date)
        
        if not recent_news.empty:
            # Analyze sentiment
            logger.info("Analyzing sentiment for recent news...")
            recent_news_with_sentiment = analyzer.analyze_dataframe(recent_news)
            sentiment_summary = analyzer.get_sentiment_summary(recent_news_with_sentiment)
            
            # Save results to JSON
            # timestamp = get_timestamp_string()
            
            # Save news with sentiment
            # filename = f"recent_news_with_sentiment_{timestamp}.json"
            # json_data = fetcher.to_json(recent_news_with_sentiment)
            # filepath = save_json_output(json_data, filename, output_dir)
            # logger.info(f"Saved news with sentiment to {filepath}")
            
            # Save sentiment summary
            # summary_filename = f"sentiment_summary_{timestamp}.json"
            # summary_filepath = os.path.join(output_dir, summary_filename)
            # with open(summary_filepath, 'w', encoding='utf-8') as f:
            #     json.dump(sentiment_summary, f, indent=2, ensure_ascii=False)
            # logger.info(f"Saved sentiment summary to {summary_filepath}")
            
            # print(f"\nRecent news count: {len(recent_news)}")
            # print("\nSentiment Summary:")
            # print(f"Total articles: {sentiment_summary['total_articles']}")
            # print("\nSentiment Distribution:")
            # for sentiment, count in sentiment_summary['sentiment_distribution'].items():
            #     percentage = sentiment_summary['sentiment_percentages'][sentiment]
            #     print(f"{sentiment}: {count} articles ({percentage:.1f}%)")

        # Example 2: Get tech company news
        logger.info("\nFetching tech company news...")
        tech_keywords = ["Apple", "Google", "Microsoft"]
        tech_news = fetcher.get_news_by_keywords(
            keywords=tech_keywords,
            start_date=start_date
        )
        
        if not tech_news.empty:
            # Analyze sentiment
            logger.info("Analyzing sentiment for tech news...")
            tech_news_with_sentiment = analyzer.analyze_dataframe(tech_news)
            tech_sentiment_summary = analyzer.get_sentiment_summary(tech_news_with_sentiment)
            
            # Save results
            # timestamp = get_timestamp_string()
            
            # Save news with sentiment
            # filename = f"tech_news_with_sentiment_{timestamp}.json"
            # json_data = fetcher.to_json(tech_news_with_sentiment)
            # filepath = save_json_output(json_data, filename, output_dir)
            # logger.info(f"Saved tech news with sentiment to {filepath}")
            
            # # Save sentiment summary
            # summary_filename = f"tech_sentiment_summary_{timestamp}.json"
            # summary_filepath = os.path.join(output_dir, summary_filename)
            # with open(summary_filepath, 'w', encoding='utf-8') as f:
            #     json.dump(tech_sentiment_summary, f, indent=2, ensure_ascii=False)
            # logger.info(f"Saved tech sentiment summary to {summary_filepath}")
            
            # print(f"\nTech company news count: {len(tech_news)}")
            # print("\nTech News Sentiment Summary:")
            # print(f"Total articles: {tech_sentiment_summary['total_articles']}")
            # print("\nSentiment Distribution:")
            # for sentiment, count in tech_sentiment_summary['sentiment_distribution'].items():
            #     percentage = tech_sentiment_summary['sentiment_percentages'][sentiment]
            #     print(f"{sentiment}: {count} articles ({percentage:.1f}%)")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()