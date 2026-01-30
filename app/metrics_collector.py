"""
Metrics Collector for ML Training Data

Collects system and application metrics every minute and stores them
in the database for ML model training. This runs automatically when
the Flask app starts.
"""

import time
import logging
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects metrics for ML training data.
    Runs continuously in the background.
    """
    
    def __init__(self, db_session_factory, app_state: Dict, interval_seconds: int = 60):
        """
        Initialize metrics collector.
        
        Args:
            db_session_factory: Function that returns database session
            app_state: Application state dictionary with request/error counts
            interval_seconds: Collection interval (default 60 seconds)
        """
        self.get_db_session = db_session_factory
        self.app_state = app_state
        self.interval_seconds = interval_seconds
        self.running = False
        self.thread = None
        self._lock = threading.Lock()
        self.previous_metrics = {}  # For calculating rates of change
        
    def start(self):
        """Start the metrics collector in background thread"""
        if self.running:
            logger.warning("Metrics collector already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.thread.start()
        logger.info(f"Metrics collector started (interval: {self.interval_seconds}s)")
    
    def stop(self):
        """Stop the metrics collector"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Metrics collector stopped")
    
    def _collection_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                metrics = self.collect_metrics()
                self.store_metrics(metrics)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}", exc_info=True)
            
            time.sleep(self.interval_seconds)
    
    def collect_metrics(self) -> Dict:
        """
        Collect current system and application metrics.
        
        Returns:
            Dictionary of metrics with timestamp
        """
        timestamp = datetime.utcnow()
        
        # System metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / (1024 * 1024)
            
            try:
                disk = psutil.disk_usage('/')
                disk_usage_percent = disk.percent
            except:
                disk_usage_percent = None
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            cpu_percent = 0
            memory_percent = 0
            memory_mb = 0
            disk_usage_percent = None
        
        # Application metrics
        with self._lock:
            request_count = self.app_state.get('requests', 0)
            error_count = self.app_state.get('errors', 0)
            error_rate = error_count / request_count if request_count > 0 else 0.0
            active_connections = self.app_state.get('active_connections', 0)
            response_times = self.app_state.get('response_times', [])
        
        # Calculate response time percentiles
        if response_times and len(response_times) > 0:
            response_times_array = np.array(response_times[-1000:])  # Last 1000 requests
            response_time_p50 = float(np.percentile(response_times_array, 50))
            response_time_p95 = float(np.percentile(response_times_array, 95))
            response_time_p99 = float(np.percentile(response_times_array, 99))
            response_time_avg = float(np.mean(response_times_array))
        else:
            response_time_p50 = None
            response_time_p95 = None
            response_time_p99 = None
            response_time_avg = None
        
        # Calculate rates of change (derived features for ML)
        cpu_rate_of_change = None
        memory_rate_of_change = None
        error_rate_trend = None
        
        if self.previous_metrics:
            prev_cpu = self.previous_metrics.get('cpu_percent')
            prev_memory = self.previous_metrics.get('memory_percent')
            prev_error_rate = self.previous_metrics.get('error_rate')
            
            if prev_cpu is not None:
                cpu_rate_of_change = cpu_percent - prev_cpu
            if prev_memory is not None:
                memory_rate_of_change = memory_percent - prev_memory
            if prev_error_rate is not None:
                error_rate_trend = error_rate - prev_error_rate
        
        metrics = {
            'timestamp': timestamp,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_mb': memory_mb,
            'disk_usage_percent': disk_usage_percent,
            'request_count': request_count,
            'error_count': error_count,
            'error_rate': error_rate,
            'active_connections': active_connections,
            'response_time_p50': response_time_p50,
            'response_time_p95': response_time_p95,
            'response_time_p99': response_time_p99,
            'response_time_avg': response_time_avg,
            'cpu_rate_of_change': cpu_rate_of_change,
            'memory_rate_of_change': memory_rate_of_change,
            'error_rate_trend': error_rate_trend
        }
        
        # Store for next iteration
        self.previous_metrics = metrics.copy()
        
        return metrics
    
    def store_metrics(self, metrics: Dict):
        """
        Store metrics in database.
        
        Args:
            metrics: Dictionary of metrics to store
        """
        db = self.get_db_session()
        try:
            db.execute("""
                INSERT INTO metrics_history (
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    memory_mb,
                    disk_usage_percent,
                    request_count,
                    error_count,
                    error_rate,
                    active_connections,
                    response_time_p50,
                    response_time_p95,
                    response_time_p99,
                    response_time_avg,
                    cpu_rate_of_change,
                    memory_rate_of_change,
                    error_rate_trend
                ) VALUES (
                    :timestamp,
                    :cpu_percent,
                    :memory_percent,
                    :memory_mb,
                    :disk_usage_percent,
                    :request_count,
                    :error_count,
                    :error_rate,
                    :active_connections,
                    :response_time_p50,
                    :response_time_p95,
                    :response_time_p99,
                    :response_time_avg,
                    :cpu_rate_of_change,
                    :memory_rate_of_change,
                    :error_rate_trend
                )
            """, metrics)
            db.commit()
            
            logger.debug(f"Stored metrics: CPU={metrics['cpu_percent']:.1f}%, "
                        f"Memory={metrics['memory_percent']:.1f}%, "
                        f"ErrorRate={metrics['error_rate']:.3f}")
        except Exception as e:
            logger.error(f"Error storing metrics: {e}", exc_info=True)
            db.rollback()
        finally:
            db.close()
    
    def get_recent_metrics(self, hours: int = 24) -> List[Dict]:
        """
        Get recent metrics from database.
        
        Args:
            hours: Number of hours to retrieve
            
        Returns:
            List of metric dictionaries
        """
        db = self.get_db_session()
        try:
            result = db.execute("""
                SELECT 
                    timestamp,
                    cpu_percent,
                    memory_percent,
                    error_rate,
                    response_time_p95,
                    active_connections
                FROM metrics_history
                WHERE timestamp > NOW() - INTERVAL ':hours hours'
                ORDER BY timestamp DESC
            """, {'hours': hours})
            
            metrics = []
            for row in result:
                metrics.append({
                    'timestamp': row[0],
                    'cpu_percent': row[1],
                    'memory_percent': row[2],
                    'error_rate': row[3],
                    'response_time_p95': row[4],
                    'active_connections': row[5]
                })
            
            return metrics
        except Exception as e:
            logger.error(f"Error retrieving metrics: {e}")
            return []
        finally:
            db.close()
    
    def cleanup_old_data(self, retention_days: int = 90):
        """
        Clean up old metrics data to save space.
        
        Args:
            retention_days: Number of days to retain (default 90)
        """
        db = self.get_db_session()
        try:
            result = db.execute(
                "SELECT cleanup_old_metrics(:retention_days)",
                {'retention_days': retention_days}
            )
            deleted_count = result.fetchone()[0]
            db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old metric records (retention: {retention_days} days)")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up metrics: {e}")
            db.rollback()
            return 0
        finally:
            db.close()


# Global collector instance (initialized in app.py)
_collector_instance: Optional[MetricsCollector] = None


def initialize_collector(db_session_factory, app_state: Dict, interval_seconds: int = 60):
    """
    Initialize the global metrics collector.
    
    Args:
        db_session_factory: Function that returns database session
        app_state: Application state dictionary
        interval_seconds: Collection interval
    """
    global _collector_instance
    
    if _collector_instance is not None:
        logger.warning("Metrics collector already initialized")
        return _collector_instance
    
    _collector_instance = MetricsCollector(db_session_factory, app_state, interval_seconds)
    _collector_instance.start()
    
    return _collector_instance


def get_collector() -> Optional[MetricsCollector]:
    """Get the global metrics collector instance"""
    return _collector_instance
