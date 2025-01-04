import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Dashboard } from './components/Dashboard';
import { Header } from './components/Header';
import { Stats, Role } from './types';
import toast, { Toaster } from 'react-hot-toast';
import { fetchStats } from './utils/api';
import { ThemeProvider } from './components/ThemeProvider';
import { ThreeDView } from './components/3d/ThreeDView';

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [role, setRole] = useState<Role>('manager');

  useEffect(() => {
    const loadStats = async () => {
      const { data, error } = await fetchStats();
      if (error) {
        setError(error);
        toast.error(error);
      } else {
        setStats(data);
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 5000);
    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <ThemeProvider>
        <div className="min-h-screen flex items-center justify-center dark:bg-gray-900">
          <p className="text-red-500">{error}</p>
        </div>
      </ThemeProvider>
    );
  }

  if (!stats) {
    return (
      <ThemeProvider>
        <div className="min-h-screen flex items-center justify-center dark:bg-gray-900">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600" />
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
          <Header role={role} onRoleChange={setRole} />
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<Dashboard stats={stats} role={role} />} />
              <Route path="/3d" element={<ThreeDView stats={stats} />} />
            </Routes>
          </main>
          <Toaster position="top-right" />
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}