import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from reddit_scrapper import RedditScraper
from reddit_parser import RedditParser

def get_sentiment_label(compound_score):
    """Convert compound score to sentiment label."""
    if compound_score >= 0.05:
        return 'positive'
    elif compound_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

def analyze_text(text, analyzer):
    """Analyze sentiment of a text using VADER."""
    scores = analyzer.polarity_scores(text)
    sentiment = get_sentiment_label(scores['compound'])
    return {
        'sentiment': sentiment,
        'scores': {
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'positive': scores['pos'],
            'compound': scores['compound']
        }
    }

def analyze_comments(comments, analyzer):
    """Analyze comments recursively."""
    analyzed_comments = []
    
    for comment in comments:
        # Analyze current comment
        sentiment_result = analyze_text(comment['content'], analyzer)
        
        analyzed_comment = {
            'author': comment['author'],
            'content': comment['content'],
            'level': comment['level'],
            'sentiment': sentiment_result['sentiment'],
            'sentiment_scores': sentiment_result['scores']
        }
        
        # Analyze replies recursively
        if comment.get('replies'):
            analyzed_comment['replies'] = analyze_comments(comment['replies'], analyzer)
        else:
            analyzed_comment['replies'] = []
            
        analyzed_comments.append(analyzed_comment)
    
    return analyzed_comments

def summarize_analysis(df):
    summary = {
      'total_posts': int(len(df)),
      'sentiment_distribution': {
          k: int(v) for k, v in df['post_sentiment'].value_counts().to_dict().items()
      },
      'comment_statistics': {
          'total_comments': int(df['comment_count'].sum()),
          'positive_comments': int(df['positive_comments'].sum()),
          'neutral_comments': int(df['neutral_comments'].sum()),
          'negative_comments': int(df['negative_comments'].sum())
      },
      'subreddits': df['subreddit'].unique().tolist(),
      'average_compound_score': float(df['sentiment_compound'].mean())
    }
    
    return summary

def get_sentiment_analysis_for_stock(stock):

    scraper = RedditScraper(
        user_agent="MyRedditApp/1.0 (by u/my_username)",
        max_pages=1,
        sleep_time=1
    )
    
    #### TODO: Use a better query to get relevant posts
    # to improve this part
    # Fetch posts and comments
    posts_with_comments = scraper.search_keywords_and_get_posts_comments(
            query="NVDA",
            limit=2,
            sort="relevance",
            time_filter="day"
    )
    # Combine posts and comments into a single text
    text = scraper.posts_and_comments_to_text(posts_with_comments, max_comment_level=2)

    # Create parser instance
    parser = RedditParser(text)

    data = parser.process_and_save()
    print(data)
    # END OF SCRAPING AND PARSING


    print("Initializing VADER sentiment analyzer...")
    analyzer = SentimentIntensityAnalyzer()

    analyzed_posts = []

    # Process each post
    print("Analyzing posts and comments...")
    for post in data['posts']:
        # Analyze post content
        post_text = f"{post['title']} {post['body']}"
        post_sentiment = analyze_text(post_text, analyzer)
        
        analyzed_post = {
            'subreddit': post['subreddit'],
            'title': post['title'],
            'body': post['body'],
            'sentiment': post_sentiment['sentiment'],
            'sentiment_scores': post_sentiment['scores']
        }
        
        # Analyze comments if present
        if post.get('comments'):
            analyzed_post['comments'] = analyze_comments(post['comments'], analyzer)
        else:
            analyzed_post['comments'] = []
            
        analyzed_posts.append(analyzed_post)


    summary_data = []
    for post in analyzed_posts:
        comment_sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        def count_sentiments(comments):
            for comment in comments:
                comment_sentiments[comment['sentiment']] += 1
                if comment['replies']:
                    count_sentiments(comment['replies'])
        
        count_sentiments(post['comments'])
        
        summary_data.append({
            'subreddit': post['subreddit'],
            'title': post['title'],
            'post_sentiment': post['sentiment'],
            'sentiment_compound': post['sentiment_scores']['compound'],
            'comment_count': sum(comment_sentiments.values()),
            'positive_comments': comment_sentiments['positive'],
            'neutral_comments': comment_sentiments['neutral'],
            'negative_comments': comment_sentiments['negative']
        })

    # Save summary
    df = pd.DataFrame(summary_data)
    result = summarize_analysis(df)
    print(result)
    
    return result