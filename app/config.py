"""
Configuration management for the Flask application.
Loads settings from environment variables and database.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Application settings
    APP_PORT = int(os.getenv('APP_PORT', 5000))
    REPLICA = os.getenv('REPLICA', 'false').lower() == 'true'
    
    # Database settings
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://remediation_user:remediation_pass@postgres:5432/remediation_db'
    )
    
    # Thresholds (defaults - can be overridden from DB config table)
    ERROR_RATE_THRESHOLD = float(os.getenv('ERROR_RATE_THRESHOLD', 0.2))
    CPU_THRESHOLD = int(os.getenv('CPU_THRESHOLD', 80))
    RESPONSE_TIME_THRESHOLD_MS = int(os.getenv('RESPONSE_TIME_THRESHOLD_MS', 500))
    
    # Simulation settings
    ENABLE_SIMULATOR = os.getenv('ENABLE_SIMULATOR', 'true').lower() == 'true'
    RANDOM_ERROR_PROBABILITY = float(os.getenv('RANDOM_ERROR_PROBABILITY', 0.05))
    
    @staticmethod
    def get_service_name():
        """Get the service name based on REPLICA env var"""
        return 'ar_app_replica' if Config.REPLICA else 'ar_app'
