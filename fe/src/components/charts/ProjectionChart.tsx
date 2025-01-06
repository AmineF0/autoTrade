import React from 'react';
import {
  Area,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { formatPrice } from '../../utils/chartUtils';

interface ProjectionChartProps {
  data: Array<{
    date: string;
    price: number;
    confidence: number;
  }>;
}

export const ProjectionChart: React.FC<ProjectionChartProps> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={120}>
      <ComposedChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis
          yAxisId="price"
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => formatPrice(value)}
        />
        <YAxis
          yAxisId="confidence"
          orientation="right"
          domain={[0, 1]}
          tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
        />
        <Tooltip
          formatter={(value: number, name: string) => [
            name === 'price' ? formatPrice(value) : `${(value * 100).toFixed(1)}%`,
            name === 'price' ? 'Projected Price' : 'Confidence',
          ]}
        />
        <Area
          yAxisId="price"
          type="monotone"
          dataKey="price"
          stroke="#10B981"
          fill="#10B981"
          fillOpacity={0.2}
        />
        <Line
          yAxisId="confidence"
          type="monotone"
          dataKey="confidence"
          stroke="#6366F1"
          strokeDasharray="3 3"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
};