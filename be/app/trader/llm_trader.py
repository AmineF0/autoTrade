import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import openai

# -----------------------------
#    STRATEGY PROMPTS (MODES)
# -----------------------------
MODES = {
    "value": """You are a meticulous value investor focused on fundamental analysis and portfolio management.
Key objectives:
- Analyze sentiment trends across social media and news
- Compare current prices against forecasted values
- Consider market sentiment stability (sentiment_std)
- Look for stocks with positive but not overhyped sentiment
- Prioritize reducing losses in underwater positions
- Consider portfolio concentration and balance
- Factor in realized profits/losses when sizing positions

Make conservative decisions based on convergence of multiple positive indicators.
Use strict position sizing based on current equity and existing exposure.""",

    "growth": """You are an aggressive growth investor seeking high-potential opportunities while managing risk.
Key objectives:
- Focus on stocks with accelerating positive sentiment trends
- Prioritize stocks where recent_sentiment > avg_sentiment
- Look for strong upward price forecasts, especially in short-term
- Consider social media momentum and engagement metrics
- Monitor position sizes relative to total equity
- Look for opportunities to average down on high-conviction positions
- Balance new positions against existing exposure

Be aggressive when multiple growth indicators align, but maintain prudent position sizing.""",

    "momentum": """You are a momentum trader capitalizing on market psychology while protecting capital.
Key objectives:
- Focus heavily on sentiment_std as a volatility indicator
- Compare short-term vs long-term forecasts for acceleration
- Analyze comment velocity and sentiment shifts
- Monitor portfolio concentration risk
- Consider realized profits/losses when sizing new positions
- Cut losses quickly on positions moving against momentum
- Scale into winning positions showing strong momentum

Act decisively when momentum indicators converge, with strict attention to position sizing.""",

    "defensive": """You are a defensive investor prioritizing capital preservation and risk management.
Key objectives:
- Favor stocks with low sentiment_std values
- Look for consistent sentiment across news and social media
- Prefer forecasts where LSTM and MLP models agree
- Monitor and limit exposure to any single position
- Focus on reducing realized losses through careful entry/exit
- Maintain balanced portfolio exposure
- Consider total equity when sizing positions

Focus on capital preservation and steady growth while managing existing positions.""",

    "ideal": """You are a balanced investor combining multiple strategies with strong risk management.
Key objectives:
- Analyze both technical and sentiment indicators holistically
- Consider short and long-term forecasts from both models
- Weight social and news sentiment based on volume and confidence
- Monitor portfolio concentration and balance
- Manage position sizes relative to total equity
- Consider realized profits/losses in decision making
- Look for opportunities to improve existing positions

Maintain a balanced approach while protecting and growing capital efficiently."""
}

# modes : value, growth, momentum, defensive, ideal

# Additional prompt to ensure the response is valid JSON
OUTPUT_FORMAT_PROMPT = """
Return valid JSON following this exact format:
[{
    "action": "BUY|SELL|HOLD",
    "stock": "SYMBOL",
    "quantity": NUMBER,
    "confidence": FLOAT,  # 0.0 to 1.0
    "reasoning": "Brief explanation including position sizing rationale"
}]

Consider in your decisions:
1. Current portfolio holdings and values
2. Realized profits/losses by position
3. Total equity and position sizing
4. Current price vs forecasted values
5. Sentiment trends and stability
6. Portfolio concentration risk
7. Risk management based on realized P/L

THIS FORMAT IS MANDATORY. Dont mention anything else in the response. it s imperative to follow the format. dont add the formatting in the response. just the json object.
"""

class LLMTrader:
    """
    A lightweight class that uses OpenAI to propose trading decisions
    based on the trader's portfolio, sentiment/forecast data, and a
    selected strategy mode. It does NOT inherit from the Trader model
    or map to the database.
    """
    
    def __init__(self, trader, openai_api_key: str, mode: str = "ideal"):
        """
        Initialize the LLMTrader.

        :param trader: An instance of your Trader model (already loaded from DB).
        :param openai_api_key: The API key to authenticate with OpenAI.
        :param mode: One of ("value", "growth", "momentum", "defensive", "ideal").
                     Defaults to "ideal" if an invalid mode is provided.
        """
        self.trader = trader
        import os
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        # If the user specifies an invalid mode, default to "ideal"
        self.mode = mode if mode in MODES else "ideal"
        self.model = "gpt-4o-mini"  # Example model name (adjust if needed)

    # ------------------------------------------------------------------------
    #    PROMPT BUILDERS - Combine portfolio, sentiment, and forecast data
    # ------------------------------------------------------------------------
    
    def _process_portfolio_data(self, context: Dict[str, Any]) -> str:
        """
        Format portfolio data (equity, holdings, realized profit) into
        a clear, structured string for the LLM prompt.

        :param context: A dictionary that should contain:
                        - total_equity
                        - current_balance
                        - portfolio_value
                        - realized_profit
                        - holdings (dict)
                        - holdings_value (dict)
                        - realized_profit_by_stock (dict)
        :return: A string summarizing portfolio details.
        """
        return context

    def _process_sentiment_data(self, context: Dict[str, Any]) -> str:
        """
        Format sentiment data (Reddit, News, etc.) into a clear, structured string.

        :param context: A dictionary that may contain:
                        - sentiment_analysis -> {
                            "reddit": {symbol: {...}},
                            "news":   {symbol: {...}}
                          }
        :return: A string summarizing sentiment analysis.
        """
        return context
        reddit = context.get('sentiment_analysis', {}).get('reddit', {})
        news = context.get('sentiment_analysis', {}).get('news', {})

        lines = ["\nSentiment Analysis:"]
        for symbol, reddit_data in reddit.items():
            news_data = news.get(symbol, {})

            lines.append(f"\n{symbol}:")
            lines.append("Social Sentiment:")
            lines.append(f"- Posts: {reddit_data.get('total_posts', 0)}")
            lines.append(f"- Avg Score: {reddit_data.get('average_compound_score', 0):.3f}")
            cstats = reddit_data.get('comment_statistics', {})
            lines.append(f"- Comments: +{cstats.get('positive_comments', 0)} / -{cstats.get('negative_comments', 0)}")

            if news_data:
                lines.append("News Sentiment:")
                lines.append(f"- Articles: {news_data.get('total_articles', 0)}")
                lines.append(f"- Confidence: {float(news_data.get('average_confidence', 0)):.3f}")

        return "\n".join(lines)

    def _process_forecast_data(self, forecast_str: str) -> str:
        """
        Format the forecast data (as plain text) into a structured summary.

        :param forecast_str: Multi-line string containing forecast info.
        :return: A string summarizing price predictions by stock.
        """
        sections = forecast_str.split('\n\n')
        processed = ["\nPrice Forecasts:"]

        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split('\n')
            stock = lines[0].replace(':', '').strip()
            if not stock:
                continue

            processed.append(f"\n{stock}:")

            # For demonstration, we assume lines 2-3 are short-term LSTM/MLP
            # and lines 5-6 are long-term LSTM/MLP, as in your example structure.
            if 'next 7 hours' in section.lower() and len(lines) >= 4:
                # short-term forecast
                lstm_hours = [float(x) for x in lines[2].split(':')[1].split()]
                mlp_hours = [float(x) for x in lines[3].split(':')[1].split()]
                processed.append("Short-term (7h):")
                processed.append(f"- LSTM: {lstm_hours[0]:.2f} → {lstm_hours[-1]:.2f}")
                processed.append(f"- MLP: {mlp_hours[0]:.2f} → {mlp_hours[-1]:.2f}")

            if 'next 7 days' in section.lower() and len(lines) >= 7:
                # long-term forecast
                lstm_days = [float(x) for x in lines[5].split(':')[1].split()]
                mlp_days = [float(x) for x in lines[6].split(':')[1].split()]
                processed.append("Long-term (7d):")
                processed.append(f"- LSTM: {lstm_days[0]:.2f} → {lstm_days[-1]:.2f}")
                processed.append(f"- MLP: {mlp_days[0]:.2f} → {mlp_days[-1]:.2f}")

        return "\n".join(processed)

    def _build_prompt(self, market_data: Dict[str, float], context: Dict[str, Any]) -> str:
        """
        Create a single prompt string by combining the strategy prompt (mode),
        market data (prices), portfolio info, sentiment analysis, and forecast data.

        :param market_data: Mapping of {stock_symbol -> current_price}.
        :param context: Dictionary containing:
                        - total_equity, current_balance, portfolio_value, realized_profit
                        - holdings, holdings_value, realized_profit_by_stock
                        - sentiment_analysis, forecast, etc.
        :return: A large text prompt to be passed to OpenAI.
        """
        # 1. Strategy text
        base_prompt = MODES[self.mode]

        # 2. Current prices
        prices_str = "\nCurrent Prices:\n" + "\n".join(
            f"- {sym}: ${float(price):.2f}"
            for sym, price in market_data.items()
        )

        # 3. Portfolio info, sentiment, forecast
        portfolio_str = self._process_portfolio_data(context)
        sentiment_str = self._process_sentiment_data(context)
        forecast_str = self._process_forecast_data(context.get('forecast', ''))

        # 4. Risk metrics (example: show each stock’s share of total_equity)
        # risk_metrics = "\nRisk Metrics:"
        # total_equity = float(context['total_equity'])
        # for symbol, value in context.get('holdings_value', {}).items():
        #     position_size = float(value)
        #     position_risk = (position_size / total_equity) * 100
        #     realized_pnl = float(context.get('realized_profit_by_stock', {}).get(symbol, 0))
        #     risk_metrics += (
        #         f"\n- {symbol}: {position_risk:.1f}% of portfolio, "
        #         f"Realized P/L: ${realized_pnl:,.2f}"
        #     )

        # 5. Construct final combined prompt
        final_prompt = (
            f"{base_prompt}\n\n"
            "Market Context:\n"
            f"{prices_str}\n"
            f"{portfolio_str}\n"
            # f"{risk_metrics}\n"
            f"{sentiment_str}\n"
            f"{forecast_str}\n\n"
            f"{OUTPUT_FORMAT_PROMPT}"
        )
        return final_prompt

    # ------------------------------------------------------------------------
    #       OPENAI API CALL
    # ------------------------------------------------------------------------
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Make the actual request to OpenAI using a ChatCompletion call.
        Returns the raw text from OpenAI, which should be valid JSON.

        :param prompt: The full text prompt to send to the model.
        :return: The model's raw response content (expected to be JSON).
        """
        openai.api_key = self.openai_api_key

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": (
                        "Analyze the provided data and generate trading decisions. "
                        "Consider portfolio balance, risk management, and position sizing. "
                    )}
                ],
                temperature=0.4,
            )
            print(f"[LLMTrader] OpenAI response: {response.choices[0].message['content']}")
            return response.choices[0].message["content"]
        except Exception as e:
            # On API error, return a fallback JSON plan that does nothing
            print(f"[LLMTrader] OpenAI API error: {e}")
            fallback = [{
                "action": "HOLD",
                "stock": "ERROR",
                "quantity": 0,
                "confidence": 0.0,
                "reasoning": "API error occurred"
            }]
            return json.dumps(fallback)

    # ------------------------------------------------------------------------
    #       MAIN ENTRY POINT: DECISION & EXECUTION
    # ------------------------------------------------------------------------
    
    def run_decision_making(
        self,
        session: Session,
        market_data: Dict[str, float],
        context: Dict[str, Any]
    ) -> None:
        """
        1. Build an LLM prompt from the strategy, market data, and context.
        2. Call OpenAI to get a JSON plan (list of trade actions).
        3. Parse and execute the plan using the underlying Trader’s buy/sell methods,
           subject to risk constraints (e.g., max position size).

        :param session: An active SQLAlchemy Session for database operations.
        :param market_data: Dict of {symbol -> current_price}.
        :param context: Dict containing portfolio, sentiment, forecast, etc.
                        Must include 'total_equity' at minimum.
        """
        # 1. Build prompt
        prompt = self._build_prompt(market_data, context)

        # 2. Call OpenAI to get plan in JSON form
        plan_json = self._call_openai_api(prompt)

        # 3. Parse the plan
        try:
            plan = json.loads(plan_json)
        except json.JSONDecodeError:
            print("[LLMTrader] Error parsing JSON response.")
            return

        # total_equity = float(context['total_equity'])
        # max_position_fraction = 0.25  # e.g. max 25% of total equity in any single stock

        # 4. Execute plan
        for item in plan:
            action = item.get("action", "HOLD").upper()
            stock = item.get("stock")
            quantity = item.get("quantity", 0)
            confidence = float(item.get("confidence", 0.0))
            reasoning = item.get("reasoning", "No reasoning provided")
            
            if action == "HOLD":
                self.trader.add_thought(session, action, stock, quantity, confidence, reasoning, self.mode)
                print(f"[LLMTrader] Decision for {stock}: HOLD")
                
            # Current price from market_data (fall back to 0.0 if not found)
            current_price = float(market_data.get(stock, 0.0))

            # Summarize the decision
            print(f"\n[LLMTrader] Decision for {stock}:")
            print(f"Action: {action} | Quantity: {quantity} | Confidence: {confidence:.2f}")
            print(f"Price: ${current_price:.2f}")
            print(f"Reasoning: {reasoning}")

            # Fetch how many shares we currently hold (for SELL checks)
            current_holdings = context.get('holdings', {}).get(stock, 0)

            # Decide whether to buy or sell (with minimal risk checks)
            if action == "BUY" and confidence >= 0.6:
                future_position_value = (current_holdings + quantity) * current_price
                try:
                    self.trader.buy_stock(session, stock, quantity, current_price)
                    self.trader.add_thought(session, action, stock, quantity, confidence, reasoning, self.mode)
                    print(f"[LLMTrader] Executed BUY: {quantity} {stock} @ ${current_price:.2f}")
                except ValueError as e:
                    print(f"[LLMTrader] BUY failed: {e}")

            elif action == "SELL" and confidence >= 0.6:
                if quantity > current_holdings:
                    print(f"[LLMTrader] SELL rejected: Trying to sell more than currently held.")
                    continue
                try:
                    self.trader.sell_stock(session, stock, quantity, current_price)
                    self.trader.add_thought(session, action, stock, quantity, confidence, reasoning, self.mode)
                    print(f"[LLMTrader] Executed SELL: {quantity} {stock} @ ${current_price:.2f}")
                except ValueError as e:
                    print(f"[LLMTrader] SELL failed: {e}")

            else:
                print(f"[LLMTrader] No action taken for {stock} (confidence too low or HOLD).")
