import { useState, useEffect } from 'react';
import { getIncidents, getIncident, resolveIncident } from '../services/api';
import { formatDateTime, formatRelativeTime, getSeverityColor, getStatusColor } from '../utils/formatters';
import { AlertTriangle, CheckCircle, Clock, Filter, X, Eye, Check } from 'lucide-react';

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [filters, setFilters] = useState({
    status: '',
    severity: '',
  });
  const [pagination, setPagination] = useState({
    total: 0,
    limit: 10,
    offset: 0,
  });

  const fetchIncidents = async () => {
    try {
      const params = {
        limit: pagination.limit,
        offset: pagination.offset,
        ...(filters.status && { status: filters.status }),
        ...(filters.severity && { severity: filters.severity }),
      };
      
      const response = await getIncidents(params);
      setIncidents(response.data.incidents);
      setPagination(prev => ({
        ...prev,
        total: response.data.total,
      }));
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch incidents:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, [filters, pagination.offset]);

  const viewIncidentDetails = async (id) => {
    try {
      const response = await getIncident(id);
      setSelectedIncident(response.data);
      setShowModal(true);
    } catch (error) {
      console.error('Failed to fetch incident details:', error);
    }
  };

  const handleResolveIncident = async (id) => {
    try {
      await resolveIncident(id);
      fetchIncidents();
      setShowModal(false);
    } catch (error) {
      console.error('Failed to resolve incident:', error);
    }
  };

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

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Incidents</h1>
          <p className="text-slate-400 mt-1">Monitor and manage system incidents</p>
        </div>
        <div className="flex items-center space-x-2 px-4 py-2 bg-slate-800 rounded-lg border border-slate-700">
          <AlertTriangle className="h-4 w-4 text-warning-500" />
          <span className="text-sm text-slate-300">{pagination.total} Total</span>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="card-body">
          <div className="flex items-center space-x-4">
            <Filter className="h-5 w-5 text-slate-400" />
            <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-2">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="input"
                >
                  <option value="">All Statuses</option>
                  <option value="ACTIVE">Active</option>
                  <option value="RESOLVED">Resolved</option>
                  <option value="ESCALATED">Escalated</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">Severity</label>
                <select
                  value={filters.severity}
                  onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
                  className="input"
                >
                  <option value="">All Severities</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="WARNING">Warning</option>
                  <option value="INFO">Info</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={() => setFilters({ status: '', severity: '' })}
                  className="btn btn-secondary w-full"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Service</th>
                <th>Time</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-slate-400">
                    Loading incidents...
                  </td>
                </tr>
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-8 text-slate-400">
                    No incidents found
                  </td>
                </tr>
              ) : (
                incidents.map((incident) => (
                  <tr key={incident.id}>
                    <td className="font-mono text-sm">#{incident.id}</td>
                    <td>
                      <span className="font-medium text-white">{incident.type}</span>
                    </td>
                    <td>
                      <span className={`badge ${getSeverityColor(incident.severity)}`}>
                        {incident.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getStatusColor(incident.status)}`}>
                        {incident.status}
                      </span>
                    </td>
                    <td className="text-slate-300">{incident.affected_service}</td>
                    <td className="text-sm text-slate-400">
                      {formatRelativeTime(incident.timestamp)}
                    </td>
                    <td>
                      <button
                        onClick={() => viewIncidentDetails(incident.id)}
                        className="text-primary-500 hover:text-primary-400 mr-3"
                        title="View details"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="card-body border-t border-slate-700">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-400">
              Showing {pagination.offset + 1} to {Math.min(pagination.offset + pagination.limit, pagination.total)} of {pagination.total} incidents
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

      {/* Detail Modal */}
      {showModal && selectedIncident && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="card-header flex items-center justify-between">
              <h3 className="text-xl font-semibold text-white">Incident Details</h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="card-body space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Incident ID</p>
                  <p className="text-white font-mono">#{selectedIncident.id}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Type</p>
                  <p className="text-white">{selectedIncident.type}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Severity</p>
                  <span className={`badge ${getSeverityColor(selectedIncident.severity)}`}>
                    {selectedIncident.severity}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Status</p>
                  <span className={`badge ${getStatusColor(selectedIncident.status)}`}>
                    {selectedIncident.status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Service</p>
                  <p className="text-white">{selectedIncident.affected_service}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Timestamp</p>
                  <p className="text-white text-sm">{formatDateTime(selectedIncident.timestamp)}</p>
                </div>
                {selectedIncident.resolved_at && (
                  <div>
                    <p className="text-sm text-slate-400">Resolved At</p>
                    <p className="text-white text-sm">{formatDateTime(selectedIncident.resolved_at)}</p>
                  </div>
                )}
                {selectedIncident.resolution_time_seconds && (
                  <div>
                    <p className="text-sm text-slate-400">Resolution Time</p>
                    <p className="text-white">{selectedIncident.resolution_time_seconds}s</p>
                  </div>
                )}
              </div>

              <div>
                <p className="text-sm text-slate-400 mb-2">Details</p>
                <pre className="bg-slate-900 p-4 rounded-lg text-sm text-slate-300 overflow-x-auto">
                  {JSON.stringify(selectedIncident.details, null, 2)}
                </pre>
              </div>

              {selectedIncident.remediation_actions && selectedIncident.remediation_actions.length > 0 && (
                <div>
                  <p className="text-sm text-slate-400 mb-2">Remediation Actions ({selectedIncident.remediation_actions.length})</p>
                  <div className="space-y-2">
                    {selectedIncident.remediation_actions.map((action) => (
                      <div key={action.id} className="bg-slate-900 p-3 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="text-white font-medium">{action.action_type}</span>
                          <span className={action.success ? 'text-success-500' : 'text-danger-500'}>
                            {action.success ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400 mt-1">Target: {action.target}</p>
                        <p className="text-xs text-slate-500 mt-1">{formatDateTime(action.timestamp)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedIncident.status === 'ACTIVE' && (
                <button
                  onClick={() => handleResolveIncident(selectedIncident.id)}
                  className="btn btn-success w-full"
                >
                  <Check className="h-4 w-4 mr-2" />
                  Mark as Resolved
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
