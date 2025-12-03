import { useState, useEffect } from 'react';
import { getConfig, updateConfig } from '../services/api';
import { Settings, Save, RotateCcw, CheckCircle, AlertCircle } from 'lucide-react';
import { getErrorMessage } from '../utils/formatters';

export default function ConfigPage() {
  const [config, setConfig] = useState(null);
  const [formData, setFormData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await getConfig();
      const configData = response.data;
      setConfig(configData);
      setFormData(configData);
      setHasChanges(false);
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (category, key, value) => {
    const newFormData = {
      ...formData,
      [category]: {
        ...formData[category],
        [key]: parseFloat(value) || 0,
      },
    };
    setFormData(newFormData);
    setHasChanges(JSON.stringify(newFormData) !== JSON.stringify(config));
    setMessage(null);
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    
    try {
      const response = await updateConfig(formData);
      setConfig(formData);
      setHasChanges(false);
      setMessage({ 
        type: 'success', 
        text: response.data.message || 'Configuration saved successfully' 
      });
    } catch (error) {
      setMessage({ type: 'error', text: getErrorMessage(error) });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setFormData(config);
    setHasChanges(false);
    setMessage(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-400">Failed to load configuration</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Configuration</h1>
          <p className="text-slate-400 mt-1">Manage auto-remediation thresholds and settings</p>
        </div>
        <Settings className="h-8 w-8 text-primary-500" />
      </div>

      {/* Message Banner */}
      {message && (
        <div className={`rounded-lg p-4 border ${
          message.type === 'success' 
            ? 'bg-success-900/20 border-success-500' 
            : 'bg-danger-900/20 border-danger-500'
        }`}>
          <div className="flex items-center space-x-3">
            {message.type === 'success' ? (
              <CheckCircle className="h-5 w-5 text-success-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-danger-500" />
            )}
            <p className={`text-sm ${message.type === 'success' ? 'text-success-500' : 'text-danger-500'}`}>
              {message.text}
            </p>
          </div>
        </div>
      )}

      {/* Thresholds Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-white">Alert Thresholds</h2>
          <p className="text-sm text-slate-400 mt-1">Configure when incidents should be triggered</p>
        </div>
        <div className="card-body space-y-6">
          {/* CPU Thresholds */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                CPU Warning Threshold (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={formData.thresholds.cpu_warning}
                onChange={(e) => handleChange('thresholds', 'cpu_warning', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Trigger warning when CPU exceeds this value</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                CPU Critical Threshold (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={formData.thresholds.cpu_critical}
                onChange={(e) => handleChange('thresholds', 'cpu_critical', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Trigger critical incident and auto-remediation</p>
            </div>
          </div>

          {/* Memory Thresholds */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Memory Warning Threshold (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={formData.thresholds.memory_warning}
                onChange={(e) => handleChange('thresholds', 'memory_warning', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Trigger warning when memory exceeds this value</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Memory Critical Threshold (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="1"
                value={formData.thresholds.memory_critical}
                onChange={(e) => handleChange('thresholds', 'memory_critical', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Trigger critical incident and auto-remediation</p>
            </div>
          </div>

          {/* Error Rate Threshold */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Error Rate Threshold (%)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                step="0.1"
                value={formData.thresholds.error_rate}
                onChange={(e) => handleChange('thresholds', 'error_rate', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Trigger incident when error rate exceeds this value</p>
            </div>
          </div>
        </div>
      </div>

      {/* Circuit Breaker Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-white">Circuit Breaker</h2>
          <p className="text-sm text-slate-400 mt-1">Prevent remediation action overload</p>
        </div>
        <div className="card-body space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Failure Threshold
              </label>
              <input
                type="number"
                min="1"
                max="20"
                step="1"
                value={formData.circuit_breaker.failure_threshold}
                onChange={(e) => handleChange('circuit_breaker', 'failure_threshold', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Number of failures before circuit opens</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Recovery Timeout (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="600"
                step="10"
                value={formData.circuit_breaker.recovery_timeout}
                onChange={(e) => handleChange('circuit_breaker', 'recovery_timeout', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Wait time before attempting to close circuit</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Success Threshold
              </label>
              <input
                type="number"
                min="1"
                max="10"
                step="1"
                value={formData.circuit_breaker.success_threshold}
                onChange={(e) => handleChange('circuit_breaker', 'success_threshold', e.target.value)}
                className="input w-full"
              />
              <p className="text-xs text-slate-500 mt-1">Consecutive successes needed to close circuit</p>
            </div>
          </div>

          {/* Circuit Breaker Info */}
          <div className="bg-primary-900/20 border border-primary-500/30 rounded p-4">
            <h4 className="text-sm font-semibold text-primary-400 mb-2">How Circuit Breaker Works</h4>
            <ul className="text-xs text-slate-300 space-y-1">
              <li>• <strong>Closed:</strong> Normal operation, remediation actions execute</li>
              <li>• <strong>Open:</strong> After {formData.circuit_breaker.failure_threshold} failures, blocks all actions</li>
              <li>• <strong>Half-Open:</strong> After {formData.circuit_breaker.recovery_timeout}s, tests with single action</li>
              <li>• <strong>Recovery:</strong> Needs {formData.circuit_breaker.success_threshold} successes to fully close</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end space-x-4 bg-slate-800 p-4 rounded-lg border border-slate-700">
        <button
          onClick={handleReset}
          disabled={!hasChanges || saving}
          className="btn btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RotateCcw className="h-4 w-4 mr-2" />
          Reset
        </button>
        <button
          onClick={handleSave}
          disabled={!hasChanges || saving}
          className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Save className="h-4 w-4 mr-2" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {/* Change Indicator */}
      {hasChanges && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-warning-900/90 border border-warning-500 rounded-lg px-4 py-2 shadow-lg">
          <p className="text-warning-400 text-sm font-medium">You have unsaved changes</p>
        </div>
      )}
    </div>
  );
}
