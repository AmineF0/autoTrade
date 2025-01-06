import React from 'react';
import { TrendingUp, Shield, Gauge, LineChart, DollarSign } from 'lucide-react';
import { TradingStrategy as TradingStrategyType } from '../types';

interface StrategyCardProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

const StrategyCard: React.FC<StrategyCardProps> = ({ label, value, icon, color }) => (
  <div className="bg-white rounded-lg p-4 flex items-center space-x-4">
    <div className={`p-3 rounded-lg ${color}`}>
      {icon}
    </div>
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <div className="mt-1 flex items-center">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${color.replace('bg-', 'bg-opacity-75 bg-')}`}
            style={{ width: `${value}%` }}
          />
        </div>
        <span className="ml-2 text-sm font-medium">{value}%</span>
      </div>
    </div>
  </div>
);

interface TradingStrategyProps {
  strategy: TradingStrategyType;
}

export const TradingStrategy: React.FC<TradingStrategyProps> = ({ strategy }) => {
  const strategies = [
    {
      label: 'Value',
      value: strategy.value,
      icon: <DollarSign className="h-5 w-5 text-blue-600" />,
      color: 'bg-blue-100',
    },
    {
      label: 'Growth',
      value: strategy.growth,
      icon: <TrendingUp className="h-5 w-5 text-green-600" />,
      color: 'bg-green-100',
    },
    {
      label: 'Momentum',
      value: strategy.momentum,
      icon: <Gauge className="h-5 w-5 text-purple-600" />,
      color: 'bg-purple-100',
    },
    {
      label: 'Defensive',
      value: strategy.defensive,
      icon: <Shield className="h-5 w-5 text-red-600" />,
      color: 'bg-red-100',
    },
    {
      label: 'Ideal',
      value: strategy.ideal,
      icon: <LineChart className="h-5 w-5 text-yellow-600" />,
      color: 'bg-yellow-100',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold mb-4">Trading Strategy</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {strategies.map((strategy) => (
          <StrategyCard key={strategy.label} {...strategy} />
        ))}
      </div>
    </div>
  );
};