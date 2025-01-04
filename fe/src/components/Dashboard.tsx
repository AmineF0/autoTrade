import { useState } from 'react';
import { SensorData, Stats, Role } from '../types';
import { SensorCard } from './SensorCard';
import { Chat } from './Chat';
import { DepartmentSelect } from './DepartmentSelect';
import { motion } from 'framer-motion';

interface DashboardProps {
  stats: Stats;
  role: Role;
}

export function Dashboard({ stats, role }: DashboardProps) {
  const [selectedDepartment, setSelectedDepartment] = useState<string>('all');
  
  const departments = Array.from(
    new Set(
      Object.entries(stats)
        .filter(([key, value]): value is [string, SensorData] => 
          typeof value === 'object' && 
          value !== null && 
          'metadata' in value
        )
        .map(([_, sensor]) => sensor.metadata.departement)
    )
  );

  const sensors = Object.entries(stats)
    .filter(([key, value]): value is [string, SensorData] => 
      typeof value === 'object' && 
      value !== null && 
      'metadata' in value && 
      (selectedDepartment === 'all' || value.metadata.departement === selectedDepartment)
    );

  const getChartType = (sensor: SensorData) => {
    if (sensor.metadata.unit === '%' || sensor.metadata.unit === 'ppm') return 'line';
    if (sensor.metadata.unit === 'µg/m³' || sensor.metadata.unit === 'NTU') return 'bar';
    return 'line';
  };

  return (
    <div>
      <div className="mb-8 flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
          {selectedDepartment === 'all' ? 'All Departments' : selectedDepartment}
        </h2>
        <DepartmentSelect
          departments={departments}
          selectedDepartment={selectedDepartment}
          onSelect={setSelectedDepartment}
        />
      </div>

      <motion.div 
        layout
        className="grid grid-cols-1 md:grid-cols-2 gap-8"
      >
        {sensors.map(([id, sensor]) => (
          <SensorCard
            key={id}
            id={id}
            sensor={sensor}
            chartType={getChartType(sensor)}
          />
        ))}
      </motion.div>

      <div className="fixed bottom-6 right-6">
        <Chat role={role} />
      </div>
    </div>
  );
}