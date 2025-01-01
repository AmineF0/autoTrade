import { Stats } from '../../types';
import { ChevronRight, ChevronDown } from 'lucide-react';

interface SidePanelProps {
  stats: Stats;
  hoveredDepartment: string | null;
  selectedDepartment: string | null;
  onDepartmentHover: (department: string | null) => void;
  onDepartmentSelect: (department: string | null) => void;
}

export function SidePanel({ 
  stats, 
  hoveredDepartment,
  selectedDepartment,
  onDepartmentHover,
  onDepartmentSelect,
}: SidePanelProps) {
  const departments = Array.from(
    new Set(
      Object.entries(stats)
        .filter(([key, value]): value is [string, any] => 
          typeof value === 'object' && 
          value !== null && 
          'metadata' in value
        )
        .map(([_, sensor]) => sensor.metadata.departement)
    )
  );

  const getStatusColor = (value: number, upper: number, lower: number) => {
    if (value > upper) return 'bg-red-500';
    if (value < lower) return 'bg-orange-500';
    return 'bg-green-500';
  };

  return (
    <div className="fixed left-4 top-[8rem] w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 max-h-[calc(100vh-10rem)] overflow-y-auto z-50">
      <h2 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Departments</h2>
      <div className="space-y-2">
        {departments.map(department => {
          const isExpanded = selectedDepartment === department;
          const departmentSensors = Object.entries(stats)
            .filter(([_, value]): value is [string, any] => 
              typeof value === 'object' && 
              value !== null && 
              'metadata' in value && 
              value.metadata.departement === department
            );

          return (
            <div 
              key={department}
              className={`rounded-md transition-colors ${
                hoveredDepartment === department 
                  ? 'bg-blue-50 dark:bg-blue-900/50'
                  : isExpanded
                  ? 'bg-blue-100 dark:bg-blue-900'
                  : ''
              }`}
              onMouseEnter={() => onDepartmentHover(department)}
              onMouseLeave={() => onDepartmentHover(null)}
            >
              <button
                onClick={() => onDepartmentSelect(isExpanded ? null : department)}
                className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
              >
                {isExpanded ? (
                  <ChevronDown className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500 dark:text-gray-400" />
                )}
                <span className="ml-2 text-gray-900 dark:text-white">{department}</span>
              </button>

              {isExpanded && (
                <div className="ml-6 space-y-1 mt-1">
                  {departmentSensors.map(([id, sensor]) => (
                    <div 
                      key={id}
                      className="flex items-center space-x-2 p-2 rounded-md text-sm"
                    >
                      <div 
                        className={`w-3 h-3 rounded-full ${
                          getStatusColor(
                            sensor.statistics.average,
                            sensor.metadata.upper,
                            sensor.metadata.lower
                          )
                        }`}
                      />
                      <span className="text-gray-700 dark:text-gray-300 flex-1">
                        {sensor.metadata.name}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400">
                        {sensor.statistics.average.toFixed(2)} {sensor.metadata.unit}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}