"""
ML Module for Auto-Remediation Platform

This module provides machine learning capabilities for:
- Real-time anomaly detection (Isolation Forest)
- Time series forecasting (Prophet)
- Failure prediction (LightGBM)
- LLM-powered incident analysis (Ollama/Hugging Face)

All models are designed to run on CPU without requiring GPU.
"""

__version__ = "1.0.0"
__author__ = "Auto-Remediation Team"

# Import main classes for easy access
try:
    from .anomaly_detector import AnomalyDetector
except ImportError:
    AnomalyDetector = None

try:
    from .forecaster import MetricForecaster
except ImportError:
    MetricForecaster = None

try:
    from .failure_predictor import FailurePredictor
except ImportError:
    FailurePredictor = None

try:
    from .llm_analyzer import LLMAnalyzer
except ImportError:
    LLMAnalyzer = None

try:
    from .synthetic_data_generator import SyntheticDataGenerator
except ImportError:
    SyntheticDataGenerator = None

__all__ = [
    'AnomalyDetector',
    'MetricForecaster',
    'FailurePredictor',
    'LLMAnalyzer',
    'SyntheticDataGenerator'
]
