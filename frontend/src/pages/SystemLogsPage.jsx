import { useState, useEffect } from 'react';
import { getHealth, getIncidents } from '../services/api';
import {
  AlertCircle, AlertTriangle, CheckCircle, Activity,
  Cpu, MemoryStick, RefreshCw, Clock, Zap, Server,
} from 'lucide-react';
import { formatDateTime, formatPercent, formatBytes, formatDuration } from '../utils/formatters';

export default function SystemLogsPage() {
  const [health, setHealth] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [apiError, setApiError] = useState(null);

  const fetchAll = async (manual = false) => {
    if (manual) setRefreshing(true);

    const [healthResult, incidentsResult] = await Promise.allSettled([
      getHealth(),
      getIncidents({ limit: 50, status: 'active' }),
    ]);

    if (healthResult.status === 'fulfilled') {
      setHealth(healthResult.value.data);
      setApiError(null);
    } else {
      setApiError(healthResult.reason?.message || 'Cannot reach API');
    }

    if (incidentsResult.status === 'fulfilled') {
      setIncidents(incidentsResult.value.data.incidents || []);
    }

    setLastUpdated(new Date());
    setLoading(false);
    if (manual) setRefreshing(false);
  };

  useEffect(() => {
    fetchAll();
    const interval = setInterval(() => fetchAll(), 15000);
    return () => clearInterval(interval);
  }, []);

  const cpu        = health?.metrics?.cpu_usage_percent ?? 0;
  const memMb      = health?.metrics?.memory_usage_mb   ?? 0;
  const errorRate  = health?.metrics?.error_rate        ?? 0;
  const uptime     = health?.uptime_seconds              ?? 0;
  const isHealthy  = health?.status === 'ok';

  const criticalCount = incidents.filter((i) => i.severity === 'critical').length;
  const highCount     = incidents.filter((i) => i.severity === 'high').length;
  const otherCount    = incidents.filter(
    (i) => i.severity !== 'critical' && i.severity !== 'high'
  ).length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">System Logs</h1>
          <p className="text-slate-400 mt-1">
            Live health status, active incidents, and performance metrics
          </p>
        </div>
        <div className="flex items-center space-x-3">
          {lastUpdated && (
            <span className="text-xs text-slate-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          <button
            onClick={() => fetchAll(true)}
            disabled={refreshing}
            className="flex items-center space-x-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-300 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* API connection error */}
      {apiError && (
        <div className="bg-danger-900/20 border border-danger-500/50 rounded-lg p-4 flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-danger-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-danger-400 font-medium">Cannot reach the backend API</p>
            <p className="text-slate-400 text-sm mt-0.5">{apiError}</p>
            <p className="text-slate-500 text-xs mt-2">
              The Flask app may still be starting up. Check{' '}
              <code className="text-slate-400">docker compose logs app</code> on the server.
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <Activity className="h-10 w-10 text-primary-500 animate-pulse" />
        </div>
      ) : (
        <>
          {/* Overall health banner */}
          <div
            className={`rounded-lg p-4 flex items-center space-x-3 border ${
              isHealthy
                ? 'bg-success-900/20 border-success-700/40'
                : 'bg-danger-900/20 border-danger-700/40'
            }`}
          >
            {isHealthy ? (
              <CheckCircle className="h-6 w-6 text-success-500 flex-shrink-0" />
            ) : (
              <AlertCircle className="h-6 w-6 text-danger-500 flex-shrink-0" />
            )}
            <div>
              <p className={`font-semibold ${isHealthy ? 'text-success-400' : 'text-danger-400'}`}>
                {isHealthy ? 'All Systems Operational' : 'System Degraded — Attention Required'}
              </p>
              <p className="text-slate-400 text-sm mt-0.5">
                Uptime: {formatDuration(uptime)}
                &nbsp;·&nbsp;
                {incidents.length} active incident{incidents.length !== 1 ? 's' : ''}
              </p>
            </div>
          </div>

          {/* Metrics row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* CPU */}
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-400">CPU Usage</p>
                  <Cpu
                    className={`h-5 w-5 ${
                      cpu > 80 ? 'text-danger-500' : cpu > 50 ? 'text-warning-500' : 'text-success-500'
                    }`}
                  />
                </div>
                <p
                  className={`text-2xl font-bold ${
                    cpu > 80 ? 'text-danger-500' : cpu > 50 ? 'text-warning-500' : 'text-success-500'
                  }`}
                >
                  {formatPercent(cpu)}
                </p>
                <div className="mt-2 w-full bg-slate-700 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all ${
                      cpu > 80 ? 'bg-danger-500' : cpu > 50 ? 'bg-warning-500' : 'bg-success-500'
                    }`}
                    style={{ width: `${Math.min(cpu, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Memory */}
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-400">Memory</p>
                  <MemoryStick className="h-5 w-5 text-primary-500" />
                </div>
                <p className="text-2xl font-bold text-primary-400">
                  {formatBytes(memMb * 1024 * 1024)}
                </p>
              </div>
            </div>

            {/* Error rate */}
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-400">Error Rate</p>
                  <Zap
                    className={`h-5 w-5 ${
                      errorRate > 0.2
                        ? 'text-danger-500'
                        : errorRate > 0.1
                        ? 'text-warning-500'
                        : 'text-success-500'
                    }`}
                  />
                </div>
                <p
                  className={`text-2xl font-bold ${
                    errorRate > 0.2
                      ? 'text-danger-500'
                      : errorRate > 0.1
                      ? 'text-warning-500'
                      : 'text-success-500'
                  }`}
                >
                  {formatPercent(errorRate * 100)}
                </p>
              </div>
            </div>

            {/* Uptime */}
            <div className="card">
              <div className="card-body">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-slate-400">Uptime</p>
                  <Clock className="h-5 w-5 text-slate-400" />
                </div>
                <p className="text-2xl font-bold text-white">{formatDuration(uptime)}</p>
              </div>
            </div>
          </div>

          {/* Incident severity summary — only when there are incidents */}
          {incidents.length > 0 && (
            <div className="grid grid-cols-3 gap-4">
              <div className="card border-danger-700/30 bg-danger-900/10">
                <div className="card-body text-center">
                  <p className="text-3xl font-bold text-danger-400">{criticalCount}</p>
                  <p className="text-sm text-slate-400 mt-1">Critical</p>
                </div>
              </div>
              <div className="card border-orange-700/30 bg-orange-900/10">
                <div className="card-body text-center">
                  <p className="text-3xl font-bold text-orange-400">{highCount}</p>
                  <p className="text-sm text-slate-400 mt-1">High</p>
                </div>
              </div>
              <div className="card border-warning-700/30 bg-warning-900/10">
                <div className="card-body text-center">
                  <p className="text-3xl font-bold text-warning-400">{otherCount}</p>
                  <p className="text-sm text-slate-400 mt-1">Medium / Low</p>
                </div>
              </div>
            </div>
          )}

          {/* Active incidents list */}
          <div className="card">
            <div className="card-body">
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                <AlertTriangle className="h-5 w-5 text-warning-500" />
                <span>Active Incidents ({incidents.length})</span>
              </h2>

              {incidents.length === 0 ? (
                <div className="text-center py-10">
                  <CheckCircle className="h-12 w-12 text-success-500 mx-auto mb-3" />
                  <p className="text-slate-300 font-medium">No active incidents</p>
                  <p className="text-slate-500 text-sm mt-1">All systems are operating normally</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {incidents.map((incident) => (
                    <div
                      key={incident.id}
                      className={`flex items-start space-x-3 p-3 rounded-lg border ${
                        incident.severity === 'critical'
                          ? 'bg-danger-900/20 border-danger-700/40'
                          : incident.severity === 'high'
                          ? 'bg-orange-900/20 border-orange-700/40'
                          : 'bg-warning-900/10 border-warning-700/30'
                      }`}
                    >
                      <AlertTriangle
                        className={`h-4 w-4 mt-0.5 flex-shrink-0 ${
                          incident.severity === 'critical'
                            ? 'text-danger-500'
                            : incident.severity === 'high'
                            ? 'text-orange-400'
                            : 'text-warning-500'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <p className="text-sm font-medium text-white">
                            {incident.incident_type || incident.description || 'Unknown incident'}
                          </p>
                          <span
                            className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full capitalize border ${
                              incident.severity === 'critical'
                                ? 'bg-danger-900/60 text-danger-400 border-danger-700/50'
                                : incident.severity === 'high'
                                ? 'bg-orange-900/60 text-orange-400 border-orange-700/50'
                                : 'bg-warning-900/60 text-warning-400 border-warning-700/50'
                            }`}
                          >
                            {incident.severity}
                          </span>
                        </div>
                        {incident.description && incident.incident_type && (
                          <p className="text-xs text-slate-400 mt-0.5 truncate">
                            {incident.description}
                          </p>
                        )}
                        <p className="text-xs text-slate-500 mt-1">
                          {formatDateTime(incident.created_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Raw health JSON — useful for debugging */}
          {health && (
            <div className="card">
              <div className="card-body">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
                  <Server className="h-5 w-5 text-slate-400" />
                  <span>Raw Health Response</span>
                </h2>
                <pre className="text-xs text-slate-400 bg-slate-900 rounded-lg p-4 overflow-x-auto">
                  {JSON.stringify(health, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
