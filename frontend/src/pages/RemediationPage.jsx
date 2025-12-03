import { useState, useEffect } from 'react';
import { getRemediationHistory } from '../services/api';
import { formatDateTime, formatRelativeTime, getSuccessColor } from '../utils/formatters';
import { History, CheckCircle, XCircle, Filter, Clock, Zap } from 'lucide-react';

export default function RemediationPage() {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    success: '',
    action_type: '',
  });
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 15,
    offset: 0,
  });
  const [stats, setStats] = useState({
    total: 0,
    successful: 0,
    failed: 0,
    successRate: 0,
  });

  const fetchActions = async () => {
    try {
      const params = {
        limit: pagination.limit,
        offset: pagination.offset,
        ...(filters.success !== '' && { success: filters.success === 'true' }),
        ...(filters.action_type && { action_type: filters.action_type }),
      };
      
      const response = await getRemediationHistory(params);
      setActions(response.data.actions);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
      }));
      
      // Calculate stats
      const successful = response.data.actions.filter(a => a.success).length;
      const failed = response.data.actions.filter(a => !a.success).length;
      setStats({
        total: response.data.total,
        successful,
        failed,
        successRate: response.data.total > 0 ? (successful / response.data.actions.length) * 100 : 0,
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch remediation history:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
    const interval = setInterval(fetchActions, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [filters, pagination.offset]);

  const nextPage = () => {
    if (pagination.offset + pagination.limit < pagination.total) {
      setPagination(prev => ({
        ...prev,
        offset: prev.offset + prev.limit,
      }));
    }
  };

  const prevPage = () => {
    if (pagination.offset > 0) {
      setPagination(prev => ({
        ...prev,
        offset: Math.max(0, prev.offset - prev.limit),
      }));
    }
  };

  const actionTypes = [...new Set(actions.map(a => a.action_type))];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Remediation History</h1>
          <p className="text-slate-400 mt-1">Track all automated remediation actions</p>
        </div>
        <div className="flex items-center space-x-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
          <History className="h-4 w-4 text-primary-500" />
          <span className="text-sm text-slate-300">{pagination.total} Actions</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Total Actions</p>
                <p className="text-2xl font-bold text-white">{stats.total}</p>
              </div>
              <Zap className="h-8 w-8 text-primary-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Successful</p>
                <p className="text-2xl font-bold text-success-500">{stats.successful}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-success-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Failed</p>
                <p className="text-2xl font-bold text-danger-500">{stats.failed}</p>
              </div>
              <XCircle className="h-8 w-8 text-danger-500" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400 mb-1">Success Rate</p>
                <p className="text-2xl font-bold text-primary-500">{stats.successRate.toFixed(1)}%</p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-slate-400" />
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-2">Result</label>
                <select
                  value={filters.success}
                  onChange={(e) => setFilters(prev => ({ ...prev, success: e.target.value }))}
                  className="input"
                >
                  <option value="">All Results</option>
                  <option value="true">Successful</option>
                  <option value="false">Failed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">Action Type</label>
                <select
                  value={filters.action_type}
                  onChange={(e) => setFilters(prev => ({ ...prev, action_type: e.target.value }))}
                  className="input"
                >
                  <option value="">All Types</option>
                  {actionTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setFilters({ success: '', action_type: '' })}
                  className="btn btn-secondary w-full"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Action Type</th>
                <th>Target</th>
                <th>Result</th>
                <th>Execution Time</th>
                <th>Triggered By</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-slate-400">
                    Loading history...
                  </td>
                </tr>
              ) : actions.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-slate-400">
                    No remediation actions found
                  </td>
                </tr>
              ) : (
                actions.map((action) => (
                  <tr key={action.id}>
                    <td className="font-mono text-sm">#{action.id}</td>
                    <td>
                      <span className="font-medium text-white">{action.action_type}</span>
                    </td>
                    <td className="text-slate-300">{action.target}</td>
                    <td>
                      <span className={`badge ${getSuccessColor(action.success)} flex items-center justify-center`}>
                        {action.success ? (
                          <>
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Success
                          </>
                        ) : (
                          <>
                            <XCircle className="h-3 w-3 mr-1" />
                            Failed
                          </>
                        )}
                      </span>
                    </td>
                    <td className="text-slate-300">
                      {action.execution_time_ms > 0 ? `${action.execution_time_ms}ms` : 'N/A'}
                    </td>
                    <td>
                      <span className="badge badge-info">{action.triggered_by}</span>
                    </td>
                    <td className="text-sm text-slate-400">
                      {formatRelativeTime(action.timestamp)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Error Messages (for failed actions) */}
        {actions.some(a => !a.success && a.error_message) && (
          <div className="card-body border-t border-slate-700">
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Recent Errors</h4>
            <div className="space-y-2">
              {actions
                .filter(a => !a.success && a.error_message)
                .slice(0, 3)
                .map((action) => (
                  <div key={action.id} className="bg-danger-900/20 border border-danger-500/30 rounded p-3">
                    <div className="flex items-start space-x-2">
                      <XCircle className="h-4 w-4 text-danger-500 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm text-danger-400 font-medium">
                          {action.action_type} on {action.target}
                        </p>
                        <p className="text-xs text-slate-400 mt-1">{action.error_message}</p>
                        <p className="text-xs text-slate-500 mt-1">{formatDateTime(action.timestamp)}</p>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Pagination */}
        <div className="card-body border-t border-slate-700">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} actions
            </p>
            <div className="flex space-x-2">
              <button
                onClick={prevPage}
                disabled={pagination.offset === 0}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={nextPage}
                disabled={pagination.offset + pagination.limit >= pagination.total}
                className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
