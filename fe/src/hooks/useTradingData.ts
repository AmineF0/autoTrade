import { useState, useEffect } from 'react';
import { ApiResponse } from '../types/api';
import { User, StockData } from '../types/domain';
import { fetchTradingData } from '../services/api';
import { transformUsers, transformStockData } from '../utils/dataTransformers';

export function useTradingData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [apiResponse, setApiResponse] = useState<ApiResponse | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [stocksData, setStocksData] = useState<Record<string, StockData>>({});

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const response = await fetchTradingData();
        setApiResponse(response);
        
        const transformedUsers = transformUsers(response);
        const transformedStocks = Object.keys(response.current_prices).reduce(
          (acc, symbol) => ({
            ...acc,
            [symbol]: transformStockData(symbol, response),
          }),
          {}
        );

        setUsers(transformedUsers);
        setStocksData(transformedStocks);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('An error occurred'));
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  return { loading, error, apiResponse, users, stocksData };
}