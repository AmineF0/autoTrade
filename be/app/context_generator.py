from trader import Trader, get_scoped_session
from time_series.predictor import Predictor
from social_media_analysis.reddit_sentiment_analysis import get_sentiment_analysis_for_stocks

def generate_context(trader: Trader, session, predictor: Predictor):
    """
    Generate context for the dashboard.
    """
    predictor.train()
    
    # Get performance stats
    performance_stats = trader.get_performance_stats(session, predictor.get_current_prices())

    # Get forecast
    forecast = predictor.forecast_nhours()

    # Get sentiment analysis
    sentiment_analysis = get_sentiment_analysis_for_stocks()

    return {
        "trade_summary": {
            "current_balance": performance_stats["current_balance"],
            "realized_profit": performance_stats["realized_profit"],
            "portfolio_value": performance_stats["portfolio_value"],
            "total_equity": performance_stats["total_equity"],
            "holdings": performance_stats["holdings"],
            "holdings_value": performance_stats["holdings_value"],
            "realized_profit_by_stock": performance_stats["realized_profit_by_stock"]
        },
        "performance_stats": performance_stats,
        # "forecast": forecast,
        "sentiment_analysis": sentiment_analysis
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
    context = generate_context(trader, session,  predictor)
    print(context)
