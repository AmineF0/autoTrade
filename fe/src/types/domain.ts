export type TradingMode = 'value' | 'growth' | 'momentum' | 'defensive' | 'ideal';

export interface User {
  id: string;
  name: string;
  tradingMode: TradingMode;
}

export interface StockData {
  symbol: string;
  currentPrice: number;
  historicalPrices: PricePoint[];
  forecast: ForecastPoint[];
}

export interface PricePoint {
  date: string;
  price: number;
}

export interface ForecastPoint extends PricePoint {
  confidence: number;
}