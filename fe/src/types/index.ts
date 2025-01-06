export interface StockData {
  history: Array<{
    date: string;
    price: number;
    volume: number;
  }>;
  projection: Array<{
    date: string;
    price: number;
    confidence: number;
  }>;
}

export interface TradeAction {
  action: 'BUY' | 'SELL' | 'HOLD';
  stock: string;
  quantity: number;
  confidence: number;
  reasoning: string;
}

export type TradingMode = 'value' | 'growth' | 'momentum' | 'defensive' | 'ideal';

export interface User {
  id: string;
  name: string;
  email: string;
  tradingMode: TradingMode;
}

export interface UserMetrics {
  current_balance: number;
  realized_profit: number;
  portfolio_value: number;
  total_equity: number;
  holdings: Record<string, number>;
  holdings_value: Record<string, number>;
  realized_profit_by_stock: Record<string, number>;
}