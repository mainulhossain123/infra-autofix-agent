"""
Circuit breaker implementation to prevent remediation flapping.
Prevents infinite restart loops and implements cooldown periods.
"""
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Circuit breaker pattern for remediation actions.
    
    States:
        - CLOSED: Normal operation, actions allowed
        - OPEN: Circuit breaker tripped, actions blocked
        - HALF_OPEN: Testing if service recovered
    """
    
    def __init__(self, max_failures: int = 3, window_seconds: int = 300, cooldown_seconds: int = 120):
        """
        Initialize circuit breaker.
        
        Args:
            max_failures: Maximum failures allowed in time window before opening circuit
            window_seconds: Time window for counting failures (default 5 minutes)
            cooldown_seconds: How long to keep circuit open before trying again (default 2 minutes)
        """
        self.max_failures = max_failures
        self.window_seconds = window_seconds
        self.cooldown_seconds = cooldown_seconds
        
        # Track action history per service+action_type
        # Key: (service_name, action_type), Value: deque of timestamps
        self.action_history: Dict[tuple, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Track circuit state per service
        # Key: service_name, Value: {'state': str, 'opened_at': float, 'last_attempt': float}
        self.circuit_state: Dict[str, Dict] = defaultdict(lambda: {
            'state': 'CLOSED',
            'opened_at': None,
            'last_attempt': None,
            'failure_count': 0
        })
    
    def can_execute(self, service_name: str, action_type: str) -> tuple[bool, Optional[str]]:
        """
        Check if action can be executed.
        
        Returns:
            (can_execute: bool, reason: Optional[str])
        """
        key = (service_name, action_type)
        state = self.circuit_state[service_name]
        current_time = time.time()
        
        # Check if circuit is OPEN
        if state['state'] == 'OPEN':
            time_since_opened = current_time - state['opened_at']
            
            # Check if cooldown period has passed
            if time_since_opened < self.cooldown_seconds:
                remaining = int(self.cooldown_seconds - time_since_opened)
                reason = f"Circuit OPEN for {service_name}. Cooldown: {remaining}s remaining"
                logger.warning(reason)
                return False, reason
            else:
                # Transition to HALF_OPEN
                state['state'] = 'HALF_OPEN'
                logger.info(f"Circuit transitioning to HALF_OPEN for {service_name}")
        
        # Check action count in sliding window
        action_times = self.action_history[key]
        
        # Remove actions outside the time window
        cutoff_time = current_time - self.window_seconds
        while action_times and action_times[0] < cutoff_time:
            action_times.popleft()
        
        # Check if we've exceeded max actions in window
        if len(action_times) >= self.max_failures:
            # Open the circuit
            state['state'] = 'OPEN'
            state['opened_at'] = current_time
            state['failure_count'] = len(action_times)
            
            reason = (
                f"Circuit OPEN for {service_name}: "
                f"{len(action_times)} {action_type} actions in last {self.window_seconds}s "
                f"(max: {self.max_failures})"
            )
            logger.warning(reason)
            return False, reason
        
        # Action is allowed
        return True, None
    
    def record_action(self, service_name: str, action_type: str, success: bool):
        """
        Record an action attempt.
        
        Args:
            service_name: Name of the service
            action_type: Type of action (restart_container, start_replica, etc.)
            success: Whether the action succeeded
        """
        key = (service_name, action_type)
        current_time = time.time()
        state = self.circuit_state[service_name]
        
        # Record the action timestamp
        self.action_history[key].append(current_time)
        state['last_attempt'] = current_time
        
        # Update circuit state based on success
        if success and state['state'] == 'HALF_OPEN':
            # Success in HALF_OPEN state -> close circuit
            state['state'] = 'CLOSED'
            state['opened_at'] = None
            state['failure_count'] = 0
            logger.info(f"Circuit CLOSED for {service_name} after successful action")
        elif not success:
            state['failure_count'] += 1
    
    def get_state(self, service_name: str) -> Dict:
        """Get current circuit breaker state for a service"""
        state = self.circuit_state[service_name]
        current_time = time.time()
        
        result = {
            'state': state['state'],
            'failure_count': state['failure_count'],
            'last_attempt': None,
            'opened_at': None,
            'cooldown_remaining_seconds': None
        }
        
        if state['last_attempt']:
            result['last_attempt'] = datetime.fromtimestamp(state['last_attempt']).isoformat()
        
        if state['opened_at']:
            result['opened_at'] = datetime.fromtimestamp(state['opened_at']).isoformat()
            time_since_opened = current_time - state['opened_at']
            result['cooldown_remaining_seconds'] = max(0, int(self.cooldown_seconds - time_since_opened))
        
        return result
    
    def reset(self, service_name: str):
        """Reset circuit breaker for a service"""
        if service_name in self.circuit_state:
            self.circuit_state[service_name] = {
                'state': 'CLOSED',
                'opened_at': None,
                'last_attempt': None,
                'failure_count': 0
            }
            logger.info(f"Circuit breaker reset for {service_name}")
    
    def get_all_states(self) -> Dict[str, Dict]:
        """Get circuit breaker states for all services"""
        return {
            service: self.get_state(service)
            for service in self.circuit_state.keys()
        }
