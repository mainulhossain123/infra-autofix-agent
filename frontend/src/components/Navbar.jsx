import { Menu, Activity, Bell, X, AlertTriangle, ChevronRight } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getHealth, getIncidents } from '../services/api';
import { formatRelativeTime } from '../utils/formatters';

export default function Navbar({ onMenuClick }) {
  const navigate = useNavigate();
  const [healthStatus, setHealthStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  // Track when the user last opened the bell to compute unread count
  const [lastReadTime, setLastReadTime] = useState(Date.now());
  const notificationRef = useRef(null);

  const unreadCount = notifications.filter(
    (n) => new Date(n.created_at).getTime() > lastReadTime
  ).length;

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await getHealth();
        setHealthStatus(response.data);
      } catch {
        // ignore — keep previous status
      } finally {
        setHealthLoading(false);
      }
    };

    // Fetch active incidents to populate notification bell
    const fetchIncidents = async () => {
      try {
        const response = await getIncidents({ limit: 8, status: 'active' });
        setNotifications(response.data.incidents || []);
      } catch {
        // silently ignore
      }
    };

    fetchHealth();
    fetchIncidents();
    const healthInterval    = setInterval(fetchHealth,    30000);
    const incidentInterval  = setInterval(fetchIncidents, 15000);
    return () => {
      clearInterval(healthInterval);
      clearInterval(incidentInterval);
    };
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (notificationRef.current && !notificationRef.current.contains(e.target)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleBellClick = () => {
    // Mark all as read when opening
    if (!showNotifications) setLastReadTime(Date.now());
    setShowNotifications((prev) => !prev);
  };

  const isHealthy = healthStatus?.status === 'ok';

  return (
    <nav className="bg-slate-800 border-b border-slate-700 sticky top-0 z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">

          {/* Left — logo + hamburger */}
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

          {/* Right — health indicator + bell + avatar */}
          <div className="flex items-center space-x-4">

            {/* Health status — clickable button when system has issues */}
            <div className="hidden sm:block">
              {healthLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-slate-500 animate-pulse" />
                  <span className="text-sm text-slate-400">Connecting...</span>
                </div>
              ) : isHealthy ? (
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 rounded-full bg-success-500 animate-pulse" />
                  <span className="text-sm text-slate-300">System Healthy</span>
                </div>
              ) : (
                <button
                  onClick={() => navigate('/system-logs')}
                  title="View system logs"
                  className="flex items-center space-x-2 px-3 py-1 rounded-md bg-danger-900/30 border border-danger-700/50 hover:bg-danger-900/60 transition-colors"
                >
                  <div className="h-2 w-2 rounded-full bg-danger-500 animate-pulse" />
                  <span className="text-sm text-danger-400">System Issues</span>
                  <ChevronRight className="h-3 w-3 text-danger-400" />
                </button>
              )}
            </div>

            {/* Notification bell */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={handleBellClick}
                className="relative p-2 text-slate-400 hover:text-white rounded-full hover:bg-slate-700 transition-colors"
                aria-label="Notifications"
              >
                <Bell className="h-5 w-5" />
                {/* Red badge when there are unread notifications */}
                {unreadCount > 0 ? (
                  <span className="absolute top-0.5 right-0.5 h-4 w-4 rounded-full bg-danger-500 flex items-center justify-center text-[9px] font-bold text-white leading-none">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                ) : notifications.length > 0 ? (
                  /* Grey dot when there are read notifications */
                  <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-slate-500" />
                ) : null}
              </button>

              {/* Notification dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50">
                  <div className="flex items-center justify-between px-4 py-3 border-b border-slate-700">
                    <h3 className="text-sm font-semibold text-white">
                      Active Incidents
                      {notifications.length > 0 && (
                        <span className="ml-2 text-xs font-normal text-slate-400">
                          ({notifications.length})
                        </span>
                      )}
                    </h3>
                    <button
                      onClick={() => setShowNotifications(false)}
                      className="text-slate-400 hover:text-white"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="max-h-72 overflow-y-auto divide-y divide-slate-700/50">
                    {notifications.length === 0 ? (
                      <div className="px-4 py-6 text-center text-slate-400 text-sm">
                        No active incidents
                      </div>
                    ) : (
                      notifications.map((incident) => (
                        <button
                          key={incident.id}
                          onClick={() => {
                            navigate('/incidents');
                            setShowNotifications(false);
                          }}
                          className="w-full px-4 py-3 text-left hover:bg-slate-700/60 transition-colors"
                        >
                          <div className="flex items-start space-x-3">
                            <AlertTriangle
                              className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                                incident.severity === 'critical' ? 'text-danger-500'  :
                                incident.severity === 'high'     ? 'text-orange-400'  :
                                incident.severity === 'medium'   ? 'text-warning-500' :
                                                                   'text-slate-400'
                              }`}
                            />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-white truncate">
                                {incident.incident_type || incident.description || 'Incident'}
                              </p>
                              <p className="text-xs text-slate-400 mt-0.5">
                                {formatRelativeTime(incident.created_at)}
                              </p>
                            </div>
                            <span
                              className={`flex-shrink-0 text-xs px-1.5 py-0.5 rounded capitalize ${
                                incident.severity === 'critical' ? 'bg-danger-900/60 text-danger-400'  :
                                incident.severity === 'high'     ? 'bg-orange-900/60 text-orange-400'  :
                                                                   'bg-warning-900/60 text-warning-400'
                              }`}
                            >
                              {incident.severity}
                            </span>
                          </div>
                        </button>
                      ))
                    )}
                  </div>

                  <div className="px-4 py-3 border-t border-slate-700 flex justify-between items-center">
                    <button
                      onClick={() => { navigate('/incidents'); setShowNotifications(false); }}
                      className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
                    >
                      View all incidents →
                    </button>
                    <button
                      onClick={() => { navigate('/system-logs'); setShowNotifications(false); }}
                      className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
                    >
                      System logs →
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* User avatar */}
            <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center">
              <span className="text-white text-sm font-medium">AD</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
