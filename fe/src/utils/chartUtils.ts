import { StockData } from '../types';

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

export const formatPrice = (price: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(price);
};

export const prepareChartData = (data: StockData) => {
  const historicalData = data.history.map(item => ({
    date: formatDate(item.date),
    price: item.price,
    volume: item.volume,
  }));

  const projectionData = data.projection.map(item => ({
    date: formatDate(item.date),
    price: item.price,
    confidence: item.confidence,
  }));

  return {
    historical: historicalData,
    projection: projectionData,
  };
};