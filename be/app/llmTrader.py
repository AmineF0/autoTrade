import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

# Example modes mapped to hypothetical strategy prompts
MODES = {
    "value": (
        "You are a meticulous value investor. "
        "Look for undervalued companies with strong fundamentals. "
        "Generate a JSON array of trade actions in this format: "
        '[{"action": "BUY|SELL|HOLD", "stock": "SYM", "quantity": N}, ...]'
    ),
    "growth": (
        "You are an aggressive growth investor. "
        "Focus on high-growth companies, even with high valuations. "
        "Generate a JSON array of trade actions in this format: "
        '[{"action": "BUY|SELL|HOLD", "stock": "SYM", "quantity": N}, ...]'
    ),
    "momentum": (
        "You are a momentum trader. "
        "Focus on recent winners that show strong price momentum. "
        "Generate a JSON array of trade actions in this format: "
        '[{"action": "BUY|SELL|HOLD", "stock": "SYM", "quantity": N}, ...]'
    ),
    "defensive": (
        "You are a defensive investor. "
        "Focus on stable, dividend-paying stocks with low volatility. "
        "Generate a JSON array of trade actions in this format: "
        '[{"action": "BUY|SELL|HOLD", "stock": "SYM", "quantity": N}, ...]'
    ),
    "ideal": (
        "You combine value, growth, momentum, and defensive tactics "
        "to create an optimal balanced approach. "
        "Generate a JSON array of trade actions in this format: "
        '[{"action": "BUY|SELL|HOLD", "stock": "SYM", "quantity": N}, ...]'
    ),
}

openai_api_key = "your-open_ai_api_key_here"

class LLMTrader:
    """
    A lightweight class that wraps around a Trader object and uses OpenAI 
    to generate and execute a trading plan. Does not inherit from Trader 
    or map to the DB.
    """

    def __init__(self, trader, mode: str = "ideal"):
        """
        :param trader: An instance of Trader (SQLAlchemy model)
        :param openai_api_key: API key for OpenAI
        :param mode: One of ("value", "growth", "momentum", "defensive", "ideal")
        """
        self.trader = trader
        self.openai_api_key = openai_api_key
        self.mode = mode if mode in MODES else "ideal"

    def run_decision_making(self, session: Session, market_data: Dict[str, float]) -> None:
        """
        1. Choose a prompt based on self.mode.
        2. Call OpenAI to get JSON actions, e.g.:
           [
             {"action": "BUY",  "stock": "AAPL", "quantity": 5},
             {"action": "SELL", "stock": "TSLA", "quantity": 2}
           ]
        3. Parse and execute those actions by calling the underlying Trader's buy/sell methods.
        """
        # 1. Build prompt
        prompt = self._build_prompt(market_data)

        # 2. Call OpenAI (mocked here) to get JSON plan
        plan_json = self._call_openai_api(prompt)

        # 3. Parse the plan
        try:
            plan = json.loads(plan_json)
        except json.JSONDecodeError:
            print("[LLMTrader] Error parsing JSON from OpenAI.")
            return

        # 4. Execute the plan
        for item in plan:
            action = item.get("action", "HOLD").upper()
            stock = item.get("stock")
            quantity = item.get("quantity", 0)

            current_price = market_data.get(stock, 0.0)

            if action == "BUY":
                try:
                    self.trader.buy_stock(session, stock, quantity, current_price)
                    print(f"[LLMTrader] Executed BUY of {quantity} {stock} @ {current_price}")
                except ValueError as e:
                    print(f"[LLMTrader] BUY failed: {e}")
            elif action == "SELL":
                try:
                    self.trader.sell_stock(session, stock, quantity, current_price)
                    print(f"[LLMTrader] Executed SELL of {quantity} {stock} @ {current_price}")
                except ValueError as e:
                    print(f"[LLMTrader] SELL failed: {e}")
            else:
                print(f"[LLMTrader] Action was HOLD or invalid. Skipping {stock}.")

    # ----------------------------------------------------------------
    # Internal / Helper Methods
    # ----------------------------------------------------------------

    def _build_prompt(self, market_data: Dict[str, float]) -> str:
        """
        Create a single prompt string by combining the strategy prompt 
        (based on self.mode) + the market data.
        """
        base_prompt = MODES[self.mode]
        market_data_str = ", ".join(f"{k}={v}" for k, v in market_data.items())

        final_prompt = (
            f"{base_prompt}\n\n"
            f"Market Data: {market_data_str}.\n\n"
            "Return valid JSON in the specified format, no extra text.\n"
        )
        return final_prompt

    def _call_openai_api(self, prompt: str) -> str:
        """
        Placeholder method for calling OpenAI. 
        In reality, you'd use 'openai.ChatCompletion.create' or a similar method.

        We'll mock the response as a hard-coded JSON string for demonstration.
        """
        print(f"[LLMTrader] (Mock) calling OpenAI with prompt: {prompt}\n")
        # Mocked JSON response (imagine it came from OpenAI)
        mocked_response_json = """
        [
          { "action": "BUY",  "stock": "AAPL", "quantity": 5 },
          { "action": "SELL", "stock": "TSLA", "quantity": 2 }
        ]
        """
        return mocked_response_json
