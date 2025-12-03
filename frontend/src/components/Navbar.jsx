import { Menu, Activity, Bell } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getHealth } from '../services/api';

export default function Navbar({ onMenuClick }) {
  const [healthStatus, setHealthStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await getHealth();
        setHealthStatus(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch health:', error);
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Refresh every 30s

    return () => clearInterval(interval);
  }, []);

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side */}
          <div className="flex items-center">
            <button
              onClick={onMenuClick}
              className="lg:hidden text-slate-400 hover:text-white p-2 rounded-md"
              aria-label="Toggle menu"
            >
              <Menu className="h-6 w-6" />
            </button>
            
            <div className="flex items-center space-x-3 ml-2 lg:ml-0">
              <Activity className="h-8 w-8 text-primary-500" />
              <div>
                <h1 className="text-xl font-bold text-white">Auto-Remediation</h1>
                <p className="text-xs text-slate-400">Infrastructure Platform</p>
              </div>
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Health status indicator */}
            <div className="hidden sm:flex items-center space-x-2">
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-slate-500 animate-pulse"></div>
                  <span className="text-sm text-slate-400">Connecting...</span>
                </div>
              ) : healthStatus?.status === 'ok' ? (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-success-500 animate-pulse"></div>
                  <span className="text-sm text-slate-300">System Healthy</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-danger-500 animate-pulse"></div>
                  <span className="text-sm text-slate-300">System Issues</span>
                </div>
              )}
            </div>

            {/* Notifications */}
            <button
              className="relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-slate-700 transition-colors"
              aria-label="Notifications"
            >
              <Bell className="h-5 w-5" />
              <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-danger-500"></span>
            </button>

            {/* User menu placeholder */}
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
              <span className="text-white text-sm font-medium">AD</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
