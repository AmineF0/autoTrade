import React from 'react';
import { useUserData } from '../hooks/useUserData';
import { useTradingData } from '../hooks/useTradingData';

interface TradeHistoryProps {
  userId: string;
}

export const TradeHistory: React.FC<TradeHistoryProps> = ({ userId }) => {
  const { apiResponse } = useTradingData();
  const { thoughts } = useUserData(userId, apiResponse);

  if (!thoughts.length) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4">Trade History</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reasoning</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {thoughts.map((trade) => (
              <tr key={trade.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold
                    ${trade.action === 'BUY' ? 'bg-green-100 text-green-800' : 
                      trade.action === 'SELL' ? 'bg-red-100 text-red-800' : 
                      'bg-gray-100 text-gray-800'}`}>
                    {trade.action}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{trade.stock}</td>
                <td className="px-6 py-4 whitespace-nowrap">{trade.quantity}</td>
                <td className="px-6 py-4 whitespace-nowrap">{(trade.confidence * 100).toFixed(1)}%</td>
                <td className="px-6 py-4">{trade.reasoning}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};