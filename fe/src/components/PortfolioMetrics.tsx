import React from 'react';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { useUserData } from '../hooks/useUserData';
import { useTradingData } from '../hooks/useTradingData';

interface PortfolioMetricsProps {
  userId: string;
}

export const PortfolioMetrics: React.FC<PortfolioMetricsProps> = ({ userId }) => {
  const { apiResponse } = useTradingData();
  const { performance } = useUserData(userId, apiResponse);

  if (!performance) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-gray-500">Total Equity</h3>
          <DollarSign className="text-green-500" size={24} />
        </div>
        <p className="text-2xl font-bold">${performance.current_balance.toLocaleString()}</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-gray-500">Realized Profit</h3>
          {performance.realized_profit >= 0 ? (
            <TrendingUp className="text-green-500" size={24} />
          ) : (
            <TrendingDown className="text-red-500" size={24} />
          )}
        </div>
        <p className={`text-2xl font-bold ${performance.realized_profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
          ${performance.realized_profit.toLocaleString()}
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-gray-500">Portfolio Value</h3>
          <DollarSign className="text-blue-500" size={24} />
        </div>
        <p className="text-2xl font-bold">${performance.portfolio_value.toLocaleString()}</p>
      </div>
    </div>
  );
};