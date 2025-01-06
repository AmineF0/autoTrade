from datetime import datetime
import enum
from typing import Dict, Any
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    relationship,
    scoped_session
)

Base = declarative_base()

class TransactionType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trader(Base):
    """
    A Trader ORM model that keeps track of balance and has relationships to
    transaction records. Provides methods for buying/selling stocks and
    computing performance statistics.
    """
    __tablename__ = "traders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)

    transactions = relationship("Transaction", back_populates="trader", cascade="all, delete-orphan")

    def buy_stock(self, session, symbol: str, quantity: int, price: float):
        """
        Attempt to buy `quantity` shares of `symbol` at `price`.
        Deducts cost from the trader's balance if sufficient funds are available.
        Raises ValueError if not enough balance.
        """
        total_cost = price * quantity
        if self.balance < total_cost:
            raise ValueError("Insufficient balance to execute buy.")
        
        # Deduct balance
        self.balance -= total_cost
        
        # Create a transaction record
        tx = Transaction(
            trader=self,
            symbol=symbol,
            quantity=quantity,
            price=price,
            transaction_type=TransactionType.BUY
        )
        session.add(tx)
        session.commit()

    def sell_stock(self, session, symbol: str, quantity: int, price: float):
        """
        Attempt to sell `quantity` shares of `symbol` at `price`.
        Ensures the trader actually holds at least `quantity` shares of that symbol.
        Raises ValueError if not enough shares.
        Adds proceeds to the trader's balance.
        """
        # Check holdings
        holdings = self.get_holdings(session)
        current_holding = holdings.get(symbol, 0)
        if current_holding < quantity:
            raise ValueError(f"Not enough shares of {symbol} to sell.")

        # Increase balance
        proceeds = price * quantity
        self.balance += proceeds
        
        # Create a transaction record
        tx = Transaction(
            trader=self,
            symbol=symbol,
            quantity=quantity,
            price=price,
            transaction_type=TransactionType.SELL
        )
        session.add(tx)
        session.commit()

    def get_holdings(self, session) -> Dict[str, int]:
        """
        Return the current holdings of the trader as a dictionary:
            { 'SYMBOL': quantity, ... }
        """
        # Aggregate all BUY - SELL
        buys = (
            session.query(Transaction.symbol, Transaction.quantity)
            .filter_by(trader_id=self.id, transaction_type=TransactionType.BUY)
            .all()
        )
        sells = (
            session.query(Transaction.symbol, Transaction.quantity)
            .filter_by(trader_id=self.id, transaction_type=TransactionType.SELL)
            .all()
        )

        holdings = {}
        for symbol, qty in buys:
            holdings[symbol] = holdings.get(symbol, 0) + qty
        for symbol, qty in sells:
            holdings[symbol] = holdings.get(symbol, 0) - qty

        return {s: q for s, q in holdings.items() if q > 0}

    def get_transaction_history(self):
        """Return a list of all transactions (for convenience)."""
        return self.transactions

    def get_realized_profit(self, session) -> float:
        """
        Naive realized profit calculation:
        Sum of (sell proceeds) - (buy costs) for matching sold quantity.
        This is an *extremely* simplified version (no partial-lot handling).
        """
        # Sum total buy cost
        total_buy = (
            session.query(Transaction)
            .filter_by(trader_id=self.id, transaction_type=TransactionType.BUY)
        )
        total_buy_amount = sum(tx.price * tx.quantity for tx in total_buy)

        # Sum total sell proceeds
        total_sell = (
            session.query(Transaction)
            .filter_by(trader_id=self.id, transaction_type=TransactionType.SELL)
        )
        total_sell_amount = sum(tx.price * tx.quantity for tx in total_sell)

        return total_sell_amount - total_buy_amount
    
    def get_realized_profit_by_stock(self, session) -> Dict[str, float]:
        """
        Return the realized profit by stock symbol.
        """
        realized_profit_by_stock = {}
        for tx in self.transactions:
            if tx.transaction_type == TransactionType.SELL:
                realized_profit_by_stock[tx.symbol] = realized_profit_by_stock.get(tx.symbol, 0.0) + tx.price * tx.quantity
            elif tx.transaction_type == TransactionType.BUY:
                realized_profit_by_stock[tx.symbol] = realized_profit_by_stock.get(tx.symbol, 0.0) - tx.price * tx.quantity
        return realized_profit_by_stock
        
    def get_performance_stats(self, session, stocks_current_value) -> Dict[str, Any]:
        """
        Return some basic performance stats, e.g.:
        - current balance
        - total realized profit by summing all sell proceeds - buy costs
        - total real-time portfolio value by summing all current stock values
        - total equity by adding balance and portfolio value
        - current holdings
        - total realized profit by each stock
        - total equity by stock
        """
        holdings = self.get_holdings(session)
        
        portfolio_value = 0.0
        for symbol, qty in holdings.items():
            # Use the current value of the stock
            stock_current_value = stocks_current_value.get(symbol)
            
            if stocks_current_value is None:
                raise ValueError(f"Stock {symbol} not found in current value data.")
            else:
                portfolio_value += stock_current_value * qty

        stats = {
            "current_balance": self.balance,
            "realized_profit": self.get_realized_profit(session),
            "portfolio_value": portfolio_value,
            "total_equity": self.balance + portfolio_value,
            "holdings": holdings,
            "holdings_value": {symbol: stocks_current_value.get(symbol, 0.0) * qty for symbol, qty in holdings.items()},
            "realized_profit_by_stock": self.get_realized_profit_by_stock(session),
        }
        return stats

    def run_string_action(self, session, action: str, stocks_current_value: Dict[str, float]):
        """
        Run a string action on the trader instance.
        This is a simple way to execute arbitrary actions on the trader instance.
        """
        # Create a temporary dictionary to hold the session and trader instance
        # This is a simple way to expose the session and trader instance to the action
        action_locals = {"session": session, "trader": self}
        exec(action, action_locals)
class Transaction(Base):
    """
    A Transaction ORM model to record buy/sell events, with a relationship back to the Trader.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trader_id = Column(Integer, ForeignKey("traders.id"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    trader = relationship("Trader", back_populates="transactions")


def get_scoped_session(db_url: str = "sqlite:///:memory:"):
    """
    Return a thread-safe scoped session connected to the given database URL.
    By default, uses an in-memory SQLite DB for demonstration.
    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return scoped_session(factory)
