import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';
import { SensorData } from '../types';
import { SensorChart } from './SensorChart';
import { SensorStats } from './SensorStats';
import { Tooltip } from './Tooltip';

interface SensorCardProps {
  id: string;
  sensor: SensorData;
  chartType: 'line' | 'bar';
}

export function SensorCard({ id, sensor, chartType }: SensorCardProps) {
  const checkAlerts = (sensor: SensorData) => {
    const latest = sensor.statistics.average;
    return latest > sensor.metadata.upper || latest < sensor.metadata.lower;
  };

  const getAlertMessage = (sensor: SensorData) => {
    const latest = sensor.statistics.average;
    if (latest > sensor.metadata.upper) {
      return `Value (${latest.toFixed(2)}) exceeds upper bound of ${sensor.metadata.upper} ${sensor.metadata.unit}`;
    }
    if (latest < sensor.metadata.lower) {
      return `Value (${latest.toFixed(2)}) is below lower bound of ${sensor.metadata.lower} ${sensor.metadata.unit}`;
    }
    return '';
  };

  return (
    <motion.div
      key={id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 transition-colors"
    >
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white">{sensor.metadata.name}</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">{sensor.metadata.description}</p>
        </div>
        {checkAlerts(sensor) && (
          <Tooltip content={getAlertMessage(sensor)}>
            <AlertTriangle className="text-red-500 animate-pulse cursor-help w-6 h-6" />
          </Tooltip>
        )}
      </div>

      <div className="h-96">
        <SensorChart
          sensor={sensor}
          type={chartType}
        />
      </div>

      <SensorStats sensor={sensor} />
    </motion.div>
  );
}