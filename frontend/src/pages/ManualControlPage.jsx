import { useState } from 'react';
import { triggerManualRemediation, triggerCPUSpike, triggerErrorSpike, triggerCrash } from '../services/api';
import { PlayCircle, RotateCw, Server, AlertTriangle, Cpu, Bug, Skull, CheckCircle, XCircle } from 'lucide-react';
import { getErrorMessage } from '../utils/formatters';

export default function ManualControlPage() {
  const [showConfirm, setShowConfirm] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const actions = [
    {
      id: 'restart_app',
      name: 'Restart Application',
      description: 'Restart the main application container',
      icon: RotateCw,
      color: 'warning',
      action: () => triggerManualRemediation({
        action_type: 'restart_container',
        target: 'ar_app',
        reason: 'Manual restart via dashboard'
      }),
    },
  ];

  const simulations = [
    {
      id: 'cpu_spike',
      name: 'Trigger CPU Spike',
      description: 'Simulate high CPU usage (10 seconds)',
      icon: Cpu,
      color: 'warning',
      action: () => triggerCPUSpike(10),
    },
    {
      id: 'error_spike',
      name: 'Trigger Error Spike',
      description: 'Simulate increased error rate (15 seconds)',
      icon: Bug,
      color: 'danger',
      action: () => triggerErrorSpike(15),
    },
    {
      id: 'crash',
      name: 'Trigger Crash',
      description: '⚠️ Crash the application (1 second delay)',
      icon: Skull,
      color: 'danger',
      action: () => triggerCrash(),
    },
  ];

  const handleActionClick = (actionItem) => {
    setSelectedAction(actionItem);
    setShowConfirm(true);
    setResult(null);
  };

  const executeAction = async () => {
    setLoading(true);
    setResult(null);
    
    try {
      const response = await selectedAction.action();
      setResult({
        success: true,
        message: response.data.message || 'Action executed successfully',
        data: response.data,
      });
    } catch (error) {
      setResult({
        success: false,
        message: getErrorMessage(error),
        error: error.response?.data,
      });
    } finally {
      setLoading(false);
      setTimeout(() => {
        setShowConfirm(false);
        setSelectedAction(null);
      }, 3000);
    }
  };

  const cancelAction = () => {
    setShowConfirm(false);
    setSelectedAction(null);
    setResult(null);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Manual Control</h1>
        <p className="text-slate-400 mt-1">Trigger remediation actions and test simulations</p>
      </div>

      {/* Warning Banner */}
      <div className="bg-warning-900/20 border border-warning-500 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="h-5 w-5 text-warning-500 mt-0.5" />
          <div>
            <h3 className="text-warning-500 font-semibold">Caution</h3>
            <p className="text-slate-300 text-sm mt-1">
              These actions directly affect the running system. Use simulation actions for testing the auto-remediation bot.
            </p>
          </div>
        </div>
      </div>

      {/* Remediation Actions */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <PlayCircle className="h-6 w-6 mr-2 text-primary-500" />
          Remediation Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {actions.map((item) => (
            <div key={item.id} className="card hover:border-primary-500/50 transition-all cursor-pointer group">
              <div className="card-body">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`p-3 rounded-lg bg-${item.color}-500/10`}>
                      <item.icon className={`h-6 w-6 text-${item.color}-500`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white group-hover:text-primary-400 transition-colors">
                        {item.name}
                      </h3>
                      <p className="text-sm text-slate-400 mt-1">{item.description}</p>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => handleActionClick(item)}
                  className={`btn btn-${item.color} w-full mt-4`}
                >
                  Execute Action
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Simulation Actions */}
      <div>
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <Bug className="h-6 w-6 mr-2 text-warning-500" />
          Test Simulations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {simulations.map((item) => (
            <div key={item.id} className="card hover:border-warning-500/50 transition-all cursor-pointer group">
              <div className="card-body">
                <div className={`p-3 rounded-lg bg-${item.color}-500/10 w-fit mb-3`}>
                  <item.icon className={`h-8 w-8 text-${item.color}-500`} />
                </div>
                <h3 className="text-lg font-semibold text-white group-hover:text-warning-400 transition-colors">
                  {item.name}
                </h3>
                <p className="text-sm text-slate-400 mt-2">{item.description}</p>
                <button
                  onClick={() => handleActionClick(item)}
                  className={`btn btn-${item.color} w-full mt-4`}
                >
                  Trigger
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirm && selectedAction && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="card max-w-md w-full">
            <div className="card-header">
              <h3 className="text-xl font-semibold text-white">Confirm Action</h3>
            </div>
            <div className="card-body space-y-4">
              {!result ? (
                <>
                  <div className="flex items-start space-x-3">
                    <div className={`p-3 rounded-lg bg-${selectedAction.color}-500/10`}>
                      <selectedAction.icon className={`h-6 w-6 text-${selectedAction.color}-500`} />
                    </div>
                    <div>
                      <p className="text-white font-semibold">{selectedAction.name}</p>
                      <p className="text-sm text-slate-400 mt-1">{selectedAction.description}</p>
                    </div>
                  </div>

                  <div className="bg-warning-900/20 border border-warning-500/30 rounded p-3">
                    <p className="text-sm text-warning-400">
                      Are you sure you want to execute this action? This will affect the running system.
                    </p>
                  </div>

                  <div className="flex space-x-3">
                    <button
                      onClick={executeAction}
                      disabled={loading}
                      className={`btn btn-${selectedAction.color} flex-1 disabled:opacity-50`}
                    >
                      {loading ? 'Executing...' : 'Confirm'}
                    </button>
                    <button
                      onClick={cancelAction}
                      disabled={loading}
                      className="btn btn-secondary flex-1 disabled:opacity-50"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className={`flex items-center space-x-3 p-4 rounded-lg ${
                    result.success 
                      ? 'bg-success-900/20 border border-success-500' 
                      : 'bg-danger-900/20 border border-danger-500'
                  }`}>
                    {result.success ? (
                      <CheckCircle className="h-8 w-8 text-success-500" />
                    ) : (
                      <XCircle className="h-8 w-8 text-danger-500" />
                    )}
                    <div>
                      <p className={`font-semibold ${result.success ? 'text-success-500' : 'text-danger-500'}`}>
                        {result.success ? 'Action Successful' : 'Action Failed'}
                      </p>
                      <p className="text-sm text-slate-300 mt-1">{result.message}</p>
                    </div>
                  </div>

                  {result.data && (
                    <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-x-auto">
                      {JSON.stringify(result.data, null, 2)}
                    </pre>
                  )}

                  <p className="text-xs text-slate-400 text-center">This dialog will close automatically...</p>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
