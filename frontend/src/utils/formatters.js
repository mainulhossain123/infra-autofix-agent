import { format, formatDistanceToNow, parseISO } from 'date-fns';

/**
 * Format timestamp to readable date/time in UTC
 */
export const formatDateTime = (timestamp) => {
  if (!timestamp) return 'N/A';
  try {
    const date = typeof timestamp === 'string' ? parseISO(timestamp) : timestamp;
    return format(date, 'MMM dd, yyyy HH:mm:ss') + ' UTC';
  } catch (error) {
    return timestamp;
  }
};

/**
 * Format timestamp to relative time (e.g., "2 minutes ago")
 * NOTE: Now returns actual datetime instead of relative time
 */
export const formatRelativeTime = (timestamp) => {
  if (!timestamp) return 'N/A';
  try {
    const date = typeof timestamp === 'string' ? parseISO(timestamp) : timestamp;
    // Return actual datetime in UTC instead of relative time
    return format(date, 'MMM dd, yyyy HH:mm:ss') + ' UTC';
  } catch (error) {
    return timestamp;
  }
};

/**
 * Format seconds to human-readable duration
 */
export const formatDuration = (seconds) => {
  if (!seconds) return '0s';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
};

/**
 * Format bytes to human-readable size
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format number with commas
 */
export const formatNumber = (num) => {
  return num?.toLocaleString() || '0';
};

/**
 * Format percentage
 */
export const formatPercent = (value, decimals = 1) => {
  return `${parseFloat(value).toFixed(decimals)}%`;
};

/**
 * Get severity color class
 */
export const getSeverityColor = (severity) => {
  const colors = {
    'CRITICAL': 'text-danger-500 bg-danger-100',
    'WARNING': 'text-warning-600 bg-warning-100',
    'INFO': 'text-primary-600 bg-primary-100',
  };
  return colors[severity] || colors['INFO'];
};

/**
 * Get status color class
 */
export const getStatusColor = (status) => {
  const colors = {
    'ACTIVE': 'text-danger-600 bg-danger-100',
    'RESOLVED': 'text-success-600 bg-success-100',
    'ESCALATED': 'text-warning-600 bg-warning-100',
  };
  return colors[status] || 'text-slate-600 bg-slate-100';
};

/**
 * Get success/failure color
 */
export const getSuccessColor = (success) => {
  return success 
    ? 'text-success-600 bg-success-100' 
    : 'text-danger-600 bg-danger-100';
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text, maxLength = 50) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Parse error message from API response
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unknown error occurred';
};
