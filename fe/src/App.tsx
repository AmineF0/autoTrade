import React, { useState } from 'react';
import { LayoutGrid } from 'lucide-react';
import { StockChart } from './components/StockChart';
import { PortfolioMetrics } from './components/PortfolioMetrics';
import { TradeHistory } from './components/TradeHistory';
import { Holdings } from './components/Holdings';
import { UserSelector } from './components/UserSelector';
import { useTradingData } from './hooks/useTradingData';

const STOCKS = ['AMZN', 'MSFT', 'TSLA', 'NVDA'];

function App() {
  const { loading, error, users, stocksData } = useTradingData();
  const [selectedUserId, setSelectedUserId] = useState<string>('');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-red-50 text-red-700 p-4 rounded-lg">
          {error.message}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <LayoutGrid className="h-8 w-8 text-blue-500 mr-3" />
              <h1 className="text-2xl font-bold text-gray-900">Trading Portfolio</h1>
            </div>
            <UserSelector
              users={users}
              selectedUserId={selectedUserId}
              onUserChange={setSelectedUserId}
            />
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="space-y-6">
          {selectedUserId && (
            <>
              <PortfolioMetrics userId={selectedUserId} />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {STOCKS.map(symbol => (
                  <StockChart 
                    key={symbol}
                    data={stocksData[symbol]}
                  />
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Holdings userId={selectedUserId} />
                <TradeHistory userId={selectedUserId} />
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;