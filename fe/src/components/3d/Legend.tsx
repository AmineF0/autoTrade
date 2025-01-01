import { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { Stats } from '../../types';

interface LegendProps {
  stats: Stats;
  selectedSection: string | null;
  onSectionSelect: (section: string | null) => void;
  hoveredSection: string | null;
  onSectionHover: (section: string | null) => void;
}

export function Legend({
  stats,
  selectedSection,
  onSectionSelect,
  hoveredSection,
  onSectionHover,
}: LegendProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  // Group sensors by section
  const sections = Object.entries(stats)
    .filter(([key, value]): value is [string, any] => 
      typeof value === 'object' && 
      value !== null && 
      'metadata' in value
    )
    .reduce((acc, [id, sensor]) => {
      const section = sensor.metadata.departement.split(' ')[2];
      if (!acc[section]) {
        acc[section] = [];
      }
      acc[section].push({ id, ...sensor });
      return acc;
    }, {} as Record<string, any[]>);

  const getSectionColor = (sectionData: any[]) => {
    const hasAlert = sectionData.some(sensor => {
      const value = sensor.statistics.average;
      return value > sensor.metadata.upper || value < sensor.metadata.lower;
    });
    return hasAlert ? 'bg-red-500' : 'bg-green-500';
  };

  const getSensorColor = (sensor: any) => {
    const value = sensor.statistics.average;
    if (value > sensor.metadata.upper) return 'bg-red-500';
    if (value < sensor.metadata.lower) return 'bg-orange-500';
    return 'bg-green-500';
  };

  return (
    <div className="absolute left-4 top-4 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div 
        className="p-3 bg-gray-100 dark:bg-gray-700 flex items-center justify-between cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 className="font-semibold text-gray-900 dark:text-white">Sections & Sensors</h3>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-500 dark:text-gray-400" />
        )}
      </div>

      {isExpanded && (
        <div className="max-h-[calc(100vh-16rem)] overflow-y-auto p-4 space-y-4">
          {Object.entries(sections).map(([section, sectionData]) => (
            <div 
              key={section}
              className={`rounded-md transition-colors ${
                hoveredSection === section || selectedSection === section
                  ? 'bg-blue-50 dark:bg-blue-900/50'
                  : ''
              }`}
              onMouseEnter={() => onSectionHover(section)}
              onMouseLeave={() => onSectionHover(null)}
            >
              <button
                onClick={() => onSectionSelect(selectedSection === section ? null : section)}
                className="w-full flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md"
              >
                <div className={`w-3 h-3 rounded-full ${getSectionColor(sectionData)}`} />
                <span className="ml-2 text-gray-900 dark:text-white">Section {section}</span>
                {selectedSection === section ? (
                  <ChevronDown className="w-4 h-4 ml-auto text-gray-500 dark:text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 ml-auto text-gray-500 dark:text-gray-400" />
                )}
              </button>

              {selectedSection === section && (
                <div className="ml-6 space-y-1 mt-1">
                  {sectionData.map(sensor => (
                    <div 
                      key={sensor.id}
                      className="flex items-center space-x-2 p-2 rounded-md text-sm"
                    >
                      <div className={`w-2 h-2 rounded-full ${getSensorColor(sensor)}`} />
                      <span className="text-gray-700 dark:text-gray-300 flex-1">
                        {sensor.metadata.name}
                      </span>
                      <span className="text-gray-500 dark:text-gray-400 text-xs">
                        {sensor.statistics.average.toFixed(1)} {sensor.metadata.unit}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}