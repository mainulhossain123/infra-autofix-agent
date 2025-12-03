import { useState, useEffect } from 'react';
import { getHealth, getMetrics } from '../services/api';
import websocketService from '../services/websocket';
import { formatPercent, formatBytes, formatDuration } from '../utils/formatters';
import { Activity, Cpu, MemoryStick, AlertCircle, Clock, TrendingUp, Server } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);

  // Fetch initial data
  const fetchData = async () => {
    try {
      const [healthRes, metricsRes] = await Promise.all([
        getHealth(),
        getMetrics()
      ]);
      
      setHealth(healthRes.data);
      setMetrics(metricsRes.data);
      
      // Add to historical data for charts (keep last 20 points)
      setHistoricalData(prev => {
        const newData = [...prev, {
          time: new Date().toLocaleTimeString(),
          cpu: healthRes.data.metrics.cpu_usage_percent || 0,
          memory: healthRes.data.metrics.memory_usage_mb || 0,
          errors: healthRes.data.metrics.total_errors || 0,
          errorRate: (healthRes.data.metrics.error_rate * 100) || 0,
        }];
        return newData.slice(-20); // Keep last 20 data points
      });
      
      setError(null);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
      setError('Failed to load dashboard data');
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();
    
    // Connect to WebSocket
    websocketService.connect('http://localhost:5000');
    
    // WebSocket event handlers
    const unsubMetrics = websocketService.onMetrics((data) => {
      console.log('Received metrics via WebSocket:', data);
      
      // Update current metrics
      setMetrics(data);
      
      // Update historical data
      setHistoricalData(prev => {
        const newData = [...prev, {
          time: new Date().toLocaleTimeString(),
          cpu: data.cpu_percent || 0,
          memory: data.memory_mb || 0,
          errors: data.total_errors || 0,
          errorRate: (data.error_rate * 100) || 0,
        }];
        return newData.slice(-20);
      });
    });
    
    const unsubConnect = websocketService.onConnect(() => {
      console.log('Dashboard: WebSocket connected');
      setWsConnected(true);
    });
    
    const unsubDisconnect = websocketService.onDisconnect(() => {
      console.log('Dashboard: WebSocket disconnected');
      setWsConnected(false);
    });
    
    // Fallback polling if WebSocket fails
    const pollInterval = setInterval(() => {
      if (!websocketService.isConnected()) {
        fetchData();
      }
    }, 10000); // Poll every 10s as fallback
    
    // Cleanup
    return () => {
      unsubMetrics();
      unsubConnect();
      unsubDisconnect();
      clearInterval(pollInterval);
      websocketService.disconnect();
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Activity className="h-12 w-12 text-primary-500 animate-pulse mx-auto mb-4" />
          <p className="text-slate-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-danger-900/20 border border-danger-500 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <AlertCircle className="h-6 w-6 text-danger-500" />
          <div>
            <h3 className="text-danger-500 font-semibold">Error Loading Dashboard</h3>
            <p className="text-slate-400 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const statusColor = health?.status === 'ok' ? 'success' : 'danger';
  const cpuColor = (metrics?.cpu_percent || health?.metrics.cpu_usage_percent || 0) > 80 ? 'danger' 
    : (metrics?.cpu_percent || health?.metrics.cpu_usage_percent || 0) > 50 ? 'warning' : 'success';
  const errorRateColor = (metrics?.error_rate || health?.metrics.error_rate || 0) > 0.2 ? 'danger' 
    : (metrics?.error_rate || health?.metrics.error_rate || 0) > 0.1 ? 'warning' : 'success';

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Dashboard</h1>
          <p className="text-slate-400 mt-1">Real-time system monitoring and metrics</p>
        </div>
        <div className="flex items-center space-x-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
          <div className={`h-2 w-2 rounded-full ${wsConnected ? 'bg-success-500' : 'bg-warning-500'} animate-pulse`}></div>
          <span className="text-sm text-slate-300">{wsConnected ? 'WebSocket: Connected' : 'Polling Mode'}</span>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* System Status */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">System Status</p>
                <p className={`text-2xl font-bold text-${statusColor}-500`}>
                  {health?.status === 'ok' ? 'Healthy' : 'Degraded'}
                </p>
              </div>
              <Server className={`h-10 w-10 text-${statusColor}-500`} />
            </div>
            <div className="mt-3 flex items-center text-xs text-slate-400">
              <Clock className="h-3 w-3 mr-1" />
              Uptime: {formatDuration(health?.uptime_seconds || 0)}
            </div>
          </div>
        </div>

        {/* CPU Usage */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">CPU Usage</p>
                <p className={`text-2xl font-bold text-${cpuColor}-500`}>
                  {formatPercent(health?.metrics.cpu_usage_percent || 0)}
                </p>
              </div>
              <Cpu className={`h-10 w-10 text-${cpuColor}-500`} />
            </div>
            <div className="mt-3">
              <div className="w-full bg-slate-700 rounded-full h-2">
                <div 
                  className={`bg-${cpuColor}-500 h-2 rounded-full transition-all duration-300`}
                  style={{ width: `${health?.metrics.cpu_usage_percent || 0}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Memory Usage */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Memory Usage</p>
                <p className="text-2xl font-bold text-primary-500">
                  {formatBytes((health?.metrics.memory_usage_mb || 0) * 1024 * 1024)}
                </p>
              </div>
              <MemoryStick className="h-10 w-10 text-primary-500" />
            </div>
            <div className="mt-3 text-xs text-slate-400">
              {health?.metrics.memory_usage_mb?.toFixed(2) || 0} MB
            </div>
          </div>
        </div>

        {/* Error Rate */}
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Error Rate</p>
                <p className={`text-2xl font-bold text-${errorRateColor}-500`}>
                  {formatPercent((health?.metrics.error_rate || 0) * 100)}
                </p>
              </div>
              <AlertCircle className={`h-10 w-10 text-${errorRateColor}-500`} />
            </div>
            <div className="mt-3 text-xs text-slate-400">
              {health?.metrics.total_errors || 0} / {health?.metrics.total_requests || 0} requests
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Usage Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-primary-500" />
              CPU Usage Trend
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={historicalData}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Area type="monotone" dataKey="cpu" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Memory Usage Chart */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-semibold text-white flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-success-500" />
              Memory Usage Trend
            </h3>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={historicalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                  labelStyle={{ color: '#94a3b8' }}
                />
                <Line type="monotone" dataKey="memory" stroke="#22c55e" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Metrics Details */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-semibold text-white">Performance Metrics</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-slate-400 mb-2">Response Time (p50)</p>
              <p className="text-xl font-semibold text-white">
                {health?.metrics.response_time_p50_ms?.toFixed(2) || 0} ms
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Response Time (p95)</p>
              <p className="text-xl font-semibold text-white">
                {health?.metrics.response_time_p95_ms?.toFixed(2) || 0} ms
              </p>
            </div>
            <div>
              <p className="text-sm text-slate-400 mb-2">Response Time (p99)</p>
              <p className="text-xl font-semibold text-white">
                {health?.metrics.response_time_p99_ms?.toFixed(2) || 0} ms
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Simulation Status */}
      {(health?.flags.cpu_spike || health?.flags.error_spike) && (
        <div className="bg-warning-900/20 border border-warning-500 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <AlertCircle className="h-6 w-6 text-warning-500" />
            <div>
              <h3 className="text-warning-500 font-semibold">Active Simulation</h3>
              <p className="text-slate-400 text-sm">
                {health?.flags.cpu_spike && 'CPU spike simulation in progress. '}
                {health?.flags.error_spike && 'Error spike simulation in progress.'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
