import React from 'react';
import { StockData } from '../types/domain';
import { PriceChart } from './charts/PriceChart';
import { ProjectionChart } from './charts/ProjectionChart';

interface StockChartProps {
  data: StockData;
}

export const StockChart: React.FC<StockChartProps> = ({ data }) => {
  if (!data) {
    return null;
  }

  const latestPrice = data.historicalPrices[data.historicalPrices.length - 1]?.price;
  const projectedPrice = data.forecast[data.forecast.length - 1]?.price;
  const priceChange = projectedPrice - latestPrice;
  const percentChange = (priceChange / latestPrice) * 100;

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold">{data.symbol}</h3>
        <div className="text-right">
          <p className="text-lg font-semibold">
            ${data.currentPrice.toFixed(2)}
          </p>
          <p className={`text-sm ${priceChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {priceChange >= 0 ? '↑' : '↓'} {Math.abs(percentChange).toFixed(2)}%
          </p>
        </div>
      </div>
      
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2">Historical Price</h4>
          <PriceChart data={data.historicalPrices} />
        </div>
        
        <div>
          <h4 className="text-sm font-medium text-gray-500 mb-2">Price Projection</h4>
          <ProjectionChart data={data.forecast} />
        </div>
      </div>
    </div>
  );
};