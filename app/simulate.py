"""
Background simulator to create realistic failure scenarios.
Simulates CPU spikes, error rate increases, and other incidents.
"""
import time
import random
import threading
import logging
from metrics import SIMULATED_CPU_SPIKE, SIMULATED_ERROR_SPIKE, CPU_USAGE

logger = logging.getLogger(__name__)


def cpu_burn(duration_sec=10):
    """
    Simulate CPU spike by burning CPU cycles.
    Runs in a separate thread to avoid blocking the main application.
    """
    logger.info(f"[simulator] Starting CPU burn for {duration_sec}s")
    SIMULATED_CPU_SPIKE.set(1)
    
    end = time.time() + duration_sec
    while time.time() < end:
        # Intensive computation to spike CPU
        x = 0
        for i in range(100000):
            x += i * i
            x = x % 1000000
    
    logger.info("[simulator] CPU burn finished")
    SIMULATED_CPU_SPIKE.set(0)


def error_spike(duration_sec=15, metrics_dict=None):
    """
    Simulate error spike by temporarily increasing error probability.
    """
    if metrics_dict is None:
        logger.warning("[simulator] No metrics dict provided for error spike")
        return
    
    logger.info(f"[simulator] Starting error spike for {duration_sec}s")
    SIMULATED_ERROR_SPIKE.set(1)
    
    # Temporarily increase error probability
    original_prob = metrics_dict.get('error_probability', 0.05)
    metrics_dict['error_probability'] = 0.3  # 30% error rate
    
    time.sleep(duration_sec)
    
    # Restore original probability
    metrics_dict['error_probability'] = original_prob
    logger.info("[simulator] Error spike finished")
    SIMULATED_ERROR_SPIKE.set(0)


def start_simulator(metrics_dict):
    """
    Start the background simulator thread.
    Periodically triggers different failure scenarios.
    
    Args:
        metrics_dict: Shared dictionary with application metrics
    """
    logger.info("[simulator] Background simulator started")
    
    while True:
        # Wait random interval between events (10-30 seconds)
        sleep_time = random.randint(10, 30)
        time.sleep(sleep_time)
        
        # Randomly choose what to simulate
        event_type = random.choice(['cpu', 'errors', 'nothing', 'nothing'])  # 'nothing' twice to make it less frequent
        
        if event_type == 'cpu':
            # Spawn CPU spike in separate thread
            threading.Thread(target=cpu_burn, args=(random.randint(8, 15),), daemon=True).start()
            
        elif event_type == 'errors':
            # Spawn error spike in separate thread
            threading.Thread(target=error_spike, args=(random.randint(10, 20), metrics_dict), daemon=True).start()
            
        else:
            logger.debug("[simulator] Idle cycle - no events triggered")
