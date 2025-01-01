import { ChevronDown } from 'lucide-react';

interface DepartmentSelectProps {
  departments: string[];
  selectedDepartment: string;
  onSelect: (department: string) => void;
}

export function DepartmentSelect({
  departments,
  selectedDepartment,
  onSelect,
}: DepartmentSelectProps) {
  return (
    <div className="relative">
      <select 
        className="appearance-none px-4 py-2 pr-10 border dark:border-gray-700 rounded-lg 
                   bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                   focus:outline-none focus:ring-2 focus:ring-blue-500
                   transition-colors cursor-pointer"
        value={selectedDepartment}
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="all" className="dark:bg-gray-800">All Departments</option>
        {departments.map(dept => (
          <option key={dept} value={dept} className="dark:bg-gray-800">
            {dept}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 dark:text-gray-400 pointer-events-none" />
    </div>
  );
}