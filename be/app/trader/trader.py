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
    thoughts = relationship("Thought", back_populates="trader", cascade="all, delete-orphan")

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
        print(stocks_current_value)
        holdings = self.get_holdings(session)
        
        portfolio_value = 0.0
        for symbol, qty in holdings.items():
            # Use the current value of the stock
            stock_current_value = stocks_current_value.get(symbol, 0.0)
            
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

    def add_thought(self, session, action: str, stock: str, quantity: int, confidence: float, reasoning: str, mode: str):
        """
        Add a reasoning entry to the trader's history.
        """
        thought = Thought(
            trader=self,
            action=action,
            stock=stock,
            quantity=quantity,
            confidence=confidence,
            reasoning=reasoning,
            mode=mode
        )
        session.add(thought)
        session.commit()
        
    def add_thoughts(self, session, thoughts):
        """
        Add multiple reasoning entries to the trader's history.
        """
        for thought in thoughts:
            thought = Thought(
                trader=self,
                action=thought["action"],
                stock=thought["stock"],
                quantity=thought["quantity"],
                confidence=thought["confidence"],
                reasoning=thought["reasoning"],
                mode=thought["mode"]
            )
            session.add(thought)
        session.commit()
        
    def get_thoughts(self):
        """Return a list of all reasoning entries (for convenience)."""
        return self.thoughts
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

class Thought(Base):
    """
    A model to record one or more 'reasoning' entries associated with a Trader.
    
    
        "action": "BUY|SELL|HOLD",
        "stock": "SYMBOL",
        "quantity": 0,
        "confidence": 0.0,
        "reasoning": "Brief explanation including position sizing rationale"
        "timestamp": "2021-01-01T12:00:00Z"
        "mode": "str"
        
    """
    __tablename__ = "thoughts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trader_id = Column(Integer, ForeignKey("traders.id"), nullable=False)

    # For example, "automatic", "manual", "simulation", etc.
    mode = Column(String, nullable=False, doc="Indicates how or why these reasonings were generated.")

    action = Column(String, nullable=False)
    stock = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    reasoning = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to Trader
    trader = relationship("Trader", back_populates="thoughts")

def get_scoped_session(db_url: str = "sqlite:///:memory:"):
    """
    Return a thread-safe scoped session connected to the given database URL.
    By default, uses an in-memory SQLite DB for demonstration.
    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    return scoped_session(factory)
