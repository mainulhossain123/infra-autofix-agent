import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Health & Metrics
export const getHealth = () => api.get('/health');
export const getMetrics = () => api.get('/api/metrics');

// Incidents
export const getIncidents = (params = {}) => api.get('/api/incidents', { params });
export const getIncident = (id) => api.get(`/api/incidents/${id}`);
export const resolveIncident = (id) => api.post(`/api/incidents/${id}/resolve`);

// Remediation
export const getRemediationHistory = (params = {}) => api.get('/api/remediation/history', { params });
export const triggerManualRemediation = (data) => api.post('/api/remediation/manual', data);

// Configuration
export const getConfig = () => api.get('/api/config');
export const updateConfig = (data) => api.put('/api/config', data);

// Simulation (for testing)
export const triggerCrash = () => api.post('/api/crash');
export const triggerCPUSpike = (duration = 10) => api.post('/api/spike/cpu', { duration });
export const triggerErrorSpike = (duration = 15) => api.post('/api/spike/errors', { duration });

export default api;
