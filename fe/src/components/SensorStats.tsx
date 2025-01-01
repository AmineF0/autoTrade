import { SensorData } from '../types';

interface SensorStatsProps {
  sensor: SensorData;
}

export function SensorStats({ sensor }: SensorStatsProps) {
  return (
    <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
      <div className="text-center">
        <p className="text-gray-600 dark:text-gray-400">Min</p>
        <p className="font-semibold dark:text-white">
          {Number(sensor.statistics.minimum).toFixed(2)} {sensor.metadata.unit}
        </p>
      </div>
      <div className="text-center">
        <p className="text-gray-600 dark:text-gray-400">Avg</p>
        <p className="font-semibold dark:text-white">
          {Number(sensor.statistics.average).toFixed(2)} {sensor.metadata.unit}
        </p>
      </div>
      <div className="text-center">
        <p className="text-gray-600 dark:text-gray-400">Max</p>
        <p className="font-semibold dark:text-white">
          {Number(sensor.statistics.maximum).toFixed(2)} {sensor.metadata.unit}
        </p>
      </div>
    </div>
  );
}