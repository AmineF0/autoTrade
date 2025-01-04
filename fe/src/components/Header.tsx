import { Role } from '../types';
import { Building2, User, Sun, Moon, LayoutDashboard, Boxes } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import { Link, useLocation } from 'react-router-dom';

interface HeaderProps {
  role: Role;
  onRoleChange: (role: Role) => void;
}

export function Header({ role, onRoleChange }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  return (
    <div className="bg-white dark:bg-gray-800 shadow-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <Building2 className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-3" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">EcoSense Dashboard</h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">Waste Management Solutions</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-6">
            <nav className="flex space-x-4">
              <Link
                to="/"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md ${
                  location.pathname === '/'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <LayoutDashboard className="w-5 h-5" />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/3d"
                className={`flex items-center space-x-2 px-3 py-2 rounded-md ${
                  location.pathname === '/3d'
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Boxes className="w-5 h-5" />
                <span>3D View</span>
              </Link>
            </nav>
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {theme === 'light' ? (
                <Moon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              ) : (
                <Sun className="h-5 w-5 text-gray-400" />
              )}
            </button>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <select
                value={role}
                onChange={(e) => onRoleChange(e.target.value as Role)}
                className="text-sm font-medium text-gray-700 dark:text-gray-300 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md cursor-pointer"
              >
                <option value="CEO" className="dark:bg-gray-800">CEO</option>
                <option value="manager" className="dark:bg-gray-800">Manager</option>
                <option value="worker" className="dark:bg-gray-800">Worker</option>
                <option value="auditor" className="dark:bg-gray-800">Auditor</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}