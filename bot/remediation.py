"""
Remediation actions for handling incidents.
Interacts with Docker to restart containers, start replicas, etc.
"""
import time
import logging
import docker
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class RemediationExecutor:
    """Executes remediation actions on Docker containers"""
    
    def __init__(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
    
    def _get_container(self, container_name: str) -> Optional[Any]:
        """Get container by name"""
        if not self.docker_client:
            logger.error("Docker client not initialized")
            return None
        
        try:
            return self.docker_client.containers.get(container_name)
        except docker.errors.NotFound:
            logger.warning(f"Container '{container_name}' not found")
            return None
        except Exception as e:
            logger.error(f"Error getting container '{container_name}': {e}")
            return None
    
    def restart_container(self, container_name: str) -> Tuple[bool, Optional[str], int]:
        """
        Restart a Docker container.
        
        Args:
            container_name: Name of the container to restart
        
        Returns:
            (success: bool, error_message: Optional[str], execution_time_ms: int)
        """
        start_time = time.time()
        
        try:
            container = self._get_container(container_name)
            if not container:
                return False, f"Container '{container_name}' not found", 0
            
            logger.info(f"Restarting container: {container_name}")
            container.restart(timeout=10)
            
            # Wait a moment and verify container is running
            time.sleep(2)
            container.reload()
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            if container.status == 'running':
                logger.info(f"Container '{container_name}' restarted successfully")
                return True, None, execution_time_ms
            else:
                error = f"Container '{container_name}' not running after restart (status: {container.status})"
                logger.error(error)
                return False, error, execution_time_ms
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error = f"Failed to restart container '{container_name}': {str(e)}"
            logger.error(error)
            return False, error, execution_time_ms
    
    def start_replica(self, replica_name: str = 'ar_app_replica') -> Tuple[bool, Optional[str], int]:
        """
        Start a replica container.
        
        Args:
            replica_name: Name of the replica container
        
        Returns:
            (success: bool, error_message: Optional[str], execution_time_ms: int)
        """
        start_time = time.time()
        
        try:
            container = self._get_container(replica_name)
            
            if container:
                # Container exists, check status
                if container.status == 'running':
                    logger.info(f"Replica '{replica_name}' already running")
                    execution_time_ms = int((time.time() - start_time) * 1000)
                    return True, None, execution_time_ms
                else:
                    # Start existing container
                    logger.info(f"Starting existing replica: {replica_name}")
                    container.start()
            else:
                # Container doesn't exist, try to create it
                logger.info(f"Replica '{replica_name}' not found, attempting to create")
                
                # Note: In production, this would create from the same image as the main app
                # For now, we assume the container exists but is stopped
                return False, f"Replica container '{replica_name}' does not exist", 0
            
            # Wait and verify
            time.sleep(2)
            container.reload()
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            if container.status == 'running':
                logger.info(f"Replica '{replica_name}' started successfully")
                return True, None, execution_time_ms
            else:
                error = f"Replica '{replica_name}' not running after start (status: {container.status})"
                logger.error(error)
                return False, error, execution_time_ms
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error = f"Failed to start replica '{replica_name}': {str(e)}"
            logger.error(error)
            return False, error, execution_time_ms
    
    def stop_replica(self, replica_name: str = 'ar_app_replica') -> Tuple[bool, Optional[str], int]:
        """
        Stop a replica container.
        
        Args:
            replica_name: Name of the replica container
        
        Returns:
            (success: bool, error_message: Optional[str], execution_time_ms: int)
        """
        start_time = time.time()
        
        try:
            container = self._get_container(replica_name)
            
            if not container:
                return False, f"Replica '{replica_name}' not found", 0
            
            if container.status != 'running':
                logger.info(f"Replica '{replica_name}' already stopped")
                execution_time_ms = int((time.time() - start_time) * 1000)
                return True, None, execution_time_ms
            
            logger.info(f"Stopping replica: {replica_name}")
            container.stop(timeout=10)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Replica '{replica_name}' stopped successfully")
            return True, None, execution_time_ms
        
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error = f"Failed to stop replica '{replica_name}': {str(e)}"
            logger.error(error)
            return False, error, execution_time_ms
    
    def get_container_status(self, container_name: str) -> Optional[str]:
        """Get current status of a container"""
        container = self._get_container(container_name)
        return container.status if container else None
    
    def scale_replicas(self, count: int) -> Tuple[bool, Optional[str], int]:
        """
        Scale replica containers to specified count.
        
        Note: This is a placeholder for future implementation.
        In production, this would work with Docker Compose or Kubernetes.
        """
        logger.warning(f"scale_replicas({count}) not fully implemented yet")
        return False, "Scaling not implemented", 0


class RemediationStrategy:
    """
    Determines which remediation action to take based on incident type and history.
    Implements graduated response and correlation logic.
    """
    
    def __init__(self):
        self.executor = RemediationExecutor()
    
    def get_action_for_incident(self, incident: Dict[str, Any], incident_history: list = None) -> Optional[Dict[str, str]]:
        """
        Determine which remediation action to take for an incident.
        
        Args:
            incident: Incident dictionary
            incident_history: List of recent incidents for the same service
        
        Returns:
            Action dict with 'action_type' and 'target', or None if no action needed
        """
        incident_type = incident.get('type')
        severity = incident.get('severity')
        details = incident.get('details', {})
        
        # Graduated response based on incident type and severity
        
        if incident_type == 'health_check_failed':
            # CRITICAL: Immediate restart
            return {
                'action_type': 'restart_container',
                'target': 'ar_app',
                'reason': 'Health check failed - app unresponsive'
            }
        
        elif incident_type == 'high_error_rate':
            error_rate = details.get('error_rate', 0)
            
            # Any error rate issue: restart app to clear errors
            return {
                'action_type': 'restart_container',
                'target': 'ar_app',
                'reason': f'High error rate: {error_rate:.2%} - restarting to recover'
            }
        
        elif incident_type == 'cpu_spike':
            cpu_percent = details.get('cpu_usage_percent', 0)
            
            if cpu_percent > 95:
                # Extreme CPU: restart app
                return {
                    'action_type': 'restart_container',
                    'target': 'ar_app',
                    'reason': f'Extreme CPU usage: {cpu_percent}% - forcing restart'
                }
            else:
                # High CPU: restart to clear any hung processes
                return {
                    'action_type': 'restart_container',
                    'target': 'ar_app',
                    'reason': f'CPU spike detected: {cpu_percent}% - restarting to recover'
                }
        
        elif incident_type == 'high_response_time':
            p95_ms = details.get('p95_response_time_ms', 0)
            
            # High response time: restart to improve performance
            return {
                'action_type': 'restart_container',
                'target': 'ar_app',
                'reason': f'High response time: P95={p95_ms}ms - restarting'
            }
        
        # Unknown incident type or no action needed
        logger.warning(f"No remediation action defined for incident type: {incident_type}")
        return None
    
    def execute_action(self, action: Dict[str, str]) -> Tuple[bool, Optional[str], int]:
        """
        Execute a remediation action.
        
        Returns:
            (success: bool, error_message: Optional[str], execution_time_ms: int)
        """
        action_type = action.get('action_type')
        target = action.get('target')
        
        if action_type == 'restart_container':
            return self.executor.restart_container(target)
        elif action_type == 'start_replica':
            return self.executor.start_replica(target)
        elif action_type == 'stop_replica':
            return self.executor.stop_replica(target)
        elif action_type == 'scale_replicas':
            count = action.get('count', 1)
            return self.executor.scale_replicas(count)
        else:
            error = f"Unknown action type: {action_type}"
            logger.error(error)
            return False, error, 0
