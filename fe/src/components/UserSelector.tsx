import React from 'react';
import { User, TradingMode } from '../types';
import { Users, TrendingUp, Shield, Gauge, LineChart, DollarSign } from 'lucide-react';

const getTradingModeIcon = (mode: TradingMode) => {
  switch (mode) {
    case 'value':
      return <DollarSign className="h-4 w-4 text-blue-600" />;
    case 'growth':
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    case 'momentum':
      return <Gauge className="h-4 w-4 text-purple-600" />;
    case 'defensive':
      return <Shield className="h-4 w-4 text-red-600" />;
    case 'ideal':
      return <LineChart className="h-4 w-4 text-yellow-600" />;
  }
};

const getTradingModeColor = (mode: TradingMode) => {
  switch (mode) {
    case 'value':
      return 'bg-blue-100 text-blue-800';
    case 'growth':
      return 'bg-green-100 text-green-800';
    case 'momentum':
      return 'bg-purple-100 text-purple-800';
    case 'defensive':
      return 'bg-red-100 text-red-800';
    case 'ideal':
      return 'bg-yellow-100 text-yellow-800';
  }
};

interface UserSelectorProps {
  users: User[];
  selectedUserId: string;
  onUserChange: (userId: string) => void;
}

export const UserSelector: React.FC<UserSelectorProps> = ({
  users,
  selectedUserId,
  onUserChange,
}) => {
  const selectedUser = users.find(user => user.id === selectedUserId);

  return (
    <div className="relative group">
      <button className="flex items-center space-x-3 px-4 py-2 bg-white rounded-lg shadow-sm hover:bg-gray-50 transition-colors">
        <Users className="h-5 w-5 text-gray-500" />
        <div className="text-left">
          <span className="block text-sm font-medium text-gray-700">
            {selectedUser?.name || 'Select User'}
          </span>
          {selectedUser && (
            <div className="flex items-center mt-1">
              {getTradingModeIcon(selectedUser.tradingMode)}
              <span className={`ml-1 text-xs px-2 py-0.5 rounded-full ${getTradingModeColor(selectedUser.tradingMode)}`}>
                {selectedUser.tradingMode}
              </span>
            </div>
          )}
        </div>
      </button>

      <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
        <div className="p-2">
          {users.map(user => (
            <button
              key={user.id}
              onClick={() => onUserChange(user.id)}
              className={`w-full flex items-center space-x-3 px-4 py-2 rounded-md text-left ${
                user.id === selectedUserId
                  ? 'bg-blue-50 text-blue-700'
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
            >
              <div className="flex-1">
                <p className="text-sm font-medium">{user.name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
              <div className="flex items-center">
                {getTradingModeIcon(user.tradingMode)}
                <span className={`ml-1 text-xs px-2 py-0.5 rounded-full ${getTradingModeColor(user.tradingMode)}`}>
                  {user.tradingMode}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};