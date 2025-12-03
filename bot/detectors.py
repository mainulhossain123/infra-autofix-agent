"""
Incident detectors for various failure scenarios.
Each detector analyzes metrics and returns incident details if threshold breached.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class IncidentDetector:
    """Base class for incident detectors"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        self.thresholds = thresholds
    
    def detect(self, health_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect incident from health data.
        Returns incident dict if detected, None otherwise.
        """
        raise NotImplementedError


class HealthCheckDetector(IncidentDetector):
    """Detects health check failures"""
    
    def detect(self, health_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if health check failed"""
        if health_data is None:
            return {
                'type': 'health_check_failed',
                'severity': 'CRITICAL',
                'details': {
                    'reason': 'health_endpoint_unreachable',
                    'message': 'Failed to connect to health endpoint'
                }
            }
        return None


class ErrorRateDetector(IncidentDetector):
    """Detects high error rates"""
    
    def detect(self, health_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not health_data or 'metrics' not in health_data:
            return None
        
        metrics = health_data['metrics']
        error_rate = metrics.get('error_rate', 0)
        threshold = self.thresholds.get('error_rate', 0.2)
        
        if error_rate > threshold:
            # Determine severity based on how much threshold is exceeded
            if error_rate > threshold * 3:
                severity = 'CRITICAL'
            elif error_rate > threshold * 1.5:
                severity = 'WARNING'
            else:
                severity = 'WARNING'
            
            return {
                'type': 'high_error_rate',
                'severity': severity,
                'details': {
                    'error_rate': error_rate,
                    'threshold': threshold,
                    'total_requests': metrics.get('total_requests', 0),
                    'total_errors': metrics.get('total_errors', 0)
                }
            }
        return None


class CPUSpikeDetector(IncidentDetector):
    """Detects CPU usage spikes"""
    
    def detect(self, health_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not health_data or 'metrics' not in health_data:
            return None
        
        metrics = health_data['metrics']
        cpu_percent = metrics.get('cpu_usage_percent', 0)
        threshold = self.thresholds.get('cpu_percent', 80)
        
        # Also check simulated CPU spike flag
        flags = health_data.get('flags', {})
        cpu_spike_flag = flags.get('cpu_spike', False)
        
        if cpu_percent > threshold or cpu_spike_flag:
            severity = 'CRITICAL' if cpu_percent > threshold * 1.2 else 'WARNING'
            
            return {
                'type': 'cpu_spike',
                'severity': severity,
                'details': {
                    'cpu_usage_percent': cpu_percent,
                    'threshold': threshold,
                    'simulated': cpu_spike_flag
                }
            }
        return None


class ResponseTimeDetector(IncidentDetector):
    """Detects high response times"""
    
    def detect(self, health_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not health_data or 'metrics' not in health_data:
            return None
        
        metrics = health_data['metrics']
        p95_ms = metrics.get('response_time_p95_ms')
        threshold = self.thresholds.get('response_time_ms', 500)
        
        if p95_ms and p95_ms > threshold:
            severity = 'CRITICAL' if p95_ms > threshold * 2 else 'WARNING'
            
            return {
                'type': 'high_response_time',
                'severity': severity,
                'details': {
                    'p95_response_time_ms': p95_ms,
                    'threshold': threshold,
                    'p50_ms': metrics.get('response_time_p50_ms'),
                    'p99_ms': metrics.get('response_time_p99_ms')
                }
            }
        return None


class DetectorManager:
    """Manages all incident detectors"""
    
    def __init__(self, thresholds: Dict[str, Any]):
        self.detectors = [
            HealthCheckDetector(thresholds),
            ErrorRateDetector(thresholds),
            CPUSpikeDetector(thresholds),
            ResponseTimeDetector(thresholds)
        ]
    
    def detect_all(self, health_data: Dict[str, Any]) -> list:
        """
        Run all detectors and return list of detected incidents.
        Returns list of incident dicts.
        """
        incidents = []
        
        for detector in self.detectors:
            try:
                incident = detector.detect(health_data)
                if incident:
                    incidents.append(incident)
            except Exception as e:
                logger.error(f"Error in detector {detector.__class__.__name__}: {e}")
        
        return incidents
    
    def update_thresholds(self, thresholds: Dict[str, Any]):
        """Update thresholds for all detectors"""
        for detector in self.detectors:
            detector.thresholds = thresholds
        logger.info(f"Updated thresholds: {thresholds}")
