import React from 'react';
import { useUserData } from '../hooks/useUserData';
import { useTradingData } from '../hooks/useTradingData';

interface HoldingsProps {
  userId: string;
}

export const Holdings: React.FC<HoldingsProps> = ({ userId }) => {
  const { apiResponse } = useTradingData();
  const { performance } = useUserData(userId, apiResponse);

  if (!performance) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4">Current Holdings</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(performance.holdings).map(([symbol, quantity]) => (
          <div key={symbol} className="border rounded-lg p-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">{symbol}</h3>
              <span className="text-sm text-gray-500">{quantity} shares</span>
            </div>
            <div className="mt-2">
              <p className="text-gray-600">
                Value: ${performance.holdings_value[symbol].toLocaleString()}
              </p>
              <p className={`text-sm ${performance.realized_profit_by_stock[symbol] >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                Realized P/L: ${performance.realized_profit_by_stock[symbol].toLocaleString()}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};