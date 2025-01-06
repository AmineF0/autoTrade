// API Response Types
export interface ApiResponse {
  people: Record<string, TradingMode>;
  people_performance: Record<string, UserPerformance>;
  people_thoughts: Record<string, TradeThought[]>;
  current_prices: Record<string, number>;
  data_and_forecast: Record<string, StockForecast>;
}

export interface UserPerformance {
  current_balance: number;
  realized_profit: number;
  portfolio_value: number;
  total_equity: number;
  holdings: Record<string, number>;
  holdings_value: Record<string, number>;
  realized_profit_by_stock: Record<string, number>;
}

export interface TradeThought {
  mode: TradingMode;
  stock: string;
  confidence: number;
  timestamp: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  id: number;
  trader_id: number;
  quantity: number;
  reasoning: string;
}

export interface StockForecast {
  '1h': TimeFrameForecast;
  '1d': TimeFrameForecast;
}

interface TimeFrameForecast {
  forecast: {
    LSTM_univariate: number[];
    MLP_univariate: number[];
  };
}