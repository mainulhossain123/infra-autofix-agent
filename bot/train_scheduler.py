#!/usr/bin/env python3
"""
ML Training Scheduler
Keeps the ML trainer container running and provides scheduled training capabilities.
"""
import time
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Keep the container running and log status."""
    logger.info("ML Training Scheduler started")
    logger.info(f"ML_ENABLED: {os.getenv('ML_ENABLED', 'false')}")
    logger.info(f"ML_TRAINING_MODE: {os.getenv('ML_TRAINING_MODE', 'manual')}")
    logger.info(f"ML_RETRAIN_INTERVAL: {os.getenv('ML_RETRAIN_INTERVAL', 'weekly')}")
    logger.info(f"OLLAMA_HOST: {os.getenv('OLLAMA_HOST', 'http://ollama:11434')}")
    logger.info(f"OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'llama3.2:3b')}")
    
    logger.info("Trainer container is ready. Waiting for manual training triggers or scheduled events.")
    logger.info("To run training manually, execute: docker exec ar_ml_trainer python train_models.py")
    
    # Keep the container running
    while True:
        time.sleep(3600)  # Sleep for 1 hour
        logger.info(f"ML Trainer health check - {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
