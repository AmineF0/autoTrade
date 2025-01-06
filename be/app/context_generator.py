from trader.trader import Trader, get_scoped_session
from time_series.predictor import Predictor
from social_media_analysis.reddit_sentiment_analysis import get_sentiment_analysis_for_stocks
from news.news_sentiment import NewsSentimentAnalyzer

from trader.llm_trader import LLMTrader

def generate_context(predictor: Predictor, news_analyzer: NewsSentimentAnalyzer):
    """
    Generate context for the dashboard.
    """
    predictor.train(force=False)
        
    return {
        "sentiment_analysis": {
            "reddit": get_sentiment_analysis_for_stocks(),
            "news": news_analyzer.compare_sentiment_stocks()
        },
        "forecast": predictor.forcast_and_format(),
        "current_prices": predictor.get_current_prices()
    }

if __name__ == "__main__":
    session = get_scoped_session("sqlite:///db.sqlite")

    # Create a new trader with an initial balance if not already present
    if not session.query(Trader).first():
      trader = Trader(name="Alice", balance=100_000)
      session.add(trader)
      session.commit()
    else:
      trader = session.query(Trader).first()
      
    predictor = Predictor()
    news_analyzer = NewsSentimentAnalyzer() 
    context = generate_context(predictor, news_analyzer)
    print(context)
    llmTrader = LLMTrader(trader, session)
    
    llmTrader.run_decision_making(session=session, context=context, market_data=context["current_prices"])
