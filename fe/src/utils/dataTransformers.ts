import { ApiResponse } from '../types/api';
import { User, StockData } from '../types/domain';

export function transformUsers(apiResponse: ApiResponse): User[] {
  return Object.entries(apiResponse.people).map(([name, mode]) => ({
    id: name.toLowerCase(),
    name,
    tradingMode: mode,
  }));
}

export function transformStockData(
  symbol: string,
  apiResponse: ApiResponse
): StockData {
  const forecast = apiResponse.data_and_forecast[symbol] || apiResponse.data_and_forecast['NVDA'];
  const currentPrice = apiResponse.current_prices[symbol];

  // Transform 1d forecast data into our domain model
  const forecastPoints = forecast['1d'].forecast.MLP_univariate.map((price, index) => ({
    date: new Date(Date.now() + index * 24 * 60 * 60 * 1000).toISOString(),
    price,
    confidence: 1 - (index * 0.1),
  }));

  // Create historical data points using current price as reference
  const historicalPrices = Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
    price: currentPrice * (1 + (Math.random() - 0.5) * 0.1),
  }));

  return {
    symbol,
    currentPrice,
    historicalPrices,
    forecast: forecastPoints,
  };
}