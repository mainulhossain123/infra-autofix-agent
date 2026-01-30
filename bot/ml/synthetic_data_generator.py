"""
Synthetic Data Generator for ML Training

Generates realistic training data when no historical data exists.
Creates various scenarios: normal operation, CPU spikes, memory leaks, error storms.
"""

import argparse
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """
    Generates synthetic training data for ML models.
    Simulates realistic infrastructure metrics and incident patterns.
    """
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize generator with random seed for reproducibility.
        
        Args:
            random_seed: Random seed for numpy
        """
        np.random.seed(random_seed)
        self.random_seed = random_seed
    
    def generate_normal_operation(self, days: int = 30, interval_minutes: int = 1) -> pd.DataFrame:
        """
        Generate metrics for normal system operation.
        Includes daily and weekly seasonality patterns.
        
        Args:
            days: Number of days to generate
            interval_minutes: Sampling interval in minutes
            
        Returns:
            DataFrame with normal operation metrics
        """
        logger.info(f"Generating {days} days of normal operation data...")
        
        total_samples = days * 24 * (60 // interval_minutes)
        data = []
        
        start_time = datetime.now() - timedelta(days=days)
        
        for i in range(total_samples):
            timestamp = start_time + timedelta(minutes=i * interval_minutes)
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # Base patterns with daily seasonality
            # CPU: Higher during business hours (9 AM - 6 PM)
            base_cpu = 25 + 15 * np.sin((hour - 6) * np.pi / 12)
            if 9 <= hour <= 18:
                base_cpu += 10  # Business hours boost
            
            # Memory: Gradual increase throughout the day, reset at night
            base_memory = 35 + (hour / 24) * 20
            if hour < 6:
                base_memory -= 10  # Lower during night
            
            # Request rate: Higher during business hours
            base_requests = 100 + 200 * np.sin((hour - 6) * np.pi / 12)
            if 9 <= hour <= 18:
                base_requests += 150
            
            # Weekly patterns (lower on weekends)
            if day_of_week >= 5:  # Saturday, Sunday
                base_cpu *= 0.7
                base_memory *= 0.8
                base_requests *= 0.5
            
            # Add realistic noise
            cpu = max(5, min(100, base_cpu + np.random.normal(0, 5)))
            memory = max(10, min(95, base_memory + np.random.normal(0, 3)))
            requests = max(10, int(base_requests + np.random.normal(0, 30)))
            
            # Error rate: normally low, occasional small spikes
            error_rate = max(0, min(0.05, np.random.exponential(0.01)))
            errors = int(requests * error_rate)
            
            # Response times: normally fast, occasional slow requests
            response_p50 = max(5, np.random.gamma(3, 5))  # ~15ms median
            response_p95 = response_p50 + np.random.gamma(5, 10)  # ~65ms p95
            response_p99 = response_p95 + np.random.gamma(3, 20)  # ~125ms p99
            
            data.append({
                'timestamp': timestamp,
                'cpu_percent': round(cpu, 2),
                'memory_percent': round(memory, 2),
                'memory_mb': round(memory * 40, 2),  # Assume 4GB total = 4000MB
                'disk_usage_percent': round(45 + np.random.uniform(-2, 2), 2),
                'request_count': requests,
                'error_count': errors,
                'error_rate': round(error_rate, 4),
                'active_connections': max(0, int(requests * 0.1 + np.random.normal(0, 5))),
                'response_time_p50': round(response_p50, 2),
                'response_time_p95': round(response_p95, 2),
                'response_time_p99': round(response_p99, 2),
                'response_time_avg': round((response_p50 + response_p95) / 2, 2),
                'label': 'normal'
            })
        
        logger.info(f"Generated {len(data)} normal operation samples")
        return pd.DataFrame(data)
    
    def generate_cpu_spike_scenarios(self, count: int = 50) -> pd.DataFrame:
        """
        Generate CPU spike incident scenarios.
        Each scenario includes: build-up → spike → remediation → recovery
        
        Args:
            count: Number of CPU spike scenarios to generate
            
        Returns:
            DataFrame with CPU spike scenarios
        """
        logger.info(f"Generating {count} CPU spike scenarios...")
        
        all_data = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            # Random time for incident
            incident_start = base_time + timedelta(
                days=np.random.randint(0, 30),
                hours=np.random.randint(8, 20),
                minutes=np.random.randint(0, 60)
            )
            
            # Phase 1: Build-up (60 minutes before spike)
            for minute in range(-60, 0):
                timestamp = incident_start + timedelta(minutes=minute)
                progress = (minute + 60) / 60  # 0 to 1
                
                cpu = 30 + (progress * 50) + np.random.normal(0, 5)
                memory = 40 + (progress * 20) + np.random.normal(0, 3)
                error_rate = 0.01 + (progress * 0.05)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='cpu_spike_buildup'
                ))
            
            # Phase 2: CPU Spike (10-15 minutes)
            spike_duration = np.random.randint(10, 16)
            for minute in range(spike_duration):
                timestamp = incident_start + timedelta(minutes=minute)
                
                cpu = np.random.uniform(85, 98)
                memory = np.random.uniform(60, 80)
                error_rate = np.random.uniform(0.10, 0.25)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='cpu_spike_active'
                ))
            
            # Phase 3: Remediation triggered (2 minutes)
            remediation_start = incident_start + timedelta(minutes=spike_duration)
            for minute in range(2):
                timestamp = remediation_start + timedelta(minutes=minute)
                
                cpu = np.random.uniform(40, 60)
                memory = np.random.uniform(50, 65)
                error_rate = np.random.uniform(0.08, 0.15)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='cpu_spike_remediation'
                ))
            
            # Phase 4: Recovery (30 minutes)
            recovery_start = remediation_start + timedelta(minutes=2)
            for minute in range(30):
                timestamp = recovery_start + timedelta(minutes=minute)
                progress = minute / 30  # 0 to 1
                
                cpu = 50 - (progress * 20) + np.random.normal(0, 3)
                memory = 60 - (progress * 15) + np.random.normal(0, 2)
                error_rate = 0.10 - (progress * 0.09)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='cpu_spike_recovery'
                ))
        
        logger.info(f"Generated {len(all_data)} CPU spike samples across {count} incidents")
        return pd.DataFrame(all_data)
    
    def generate_memory_leak_scenarios(self, count: int = 25) -> pd.DataFrame:
        """
        Generate memory leak scenarios.
        Gradual memory increase over hours until remediation.
        
        Args:
            count: Number of memory leak scenarios
            
        Returns:
            DataFrame with memory leak scenarios
        """
        logger.info(f"Generating {count} memory leak scenarios...")
        
        all_data = []
        base_time = datetime.now() - timedelta(days=25)
        
        for i in range(count):
            leak_start = base_time + timedelta(
                days=np.random.randint(0, 25),
                hours=np.random.randint(0, 24)
            )
            
            # Gradual memory increase (6-12 hours)
            leak_duration_hours = np.random.randint(6, 13)
            for minute in range(leak_duration_hours * 60):
                timestamp = leak_start + timedelta(minutes=minute)
                progress = minute / (leak_duration_hours * 60)
                
                cpu = 35 + np.random.normal(0, 5)
                memory = 40 + (progress * 55)  # 40% to 95%
                error_rate = 0.01 + (progress * 0.10)
                
                label = 'memory_leak_active' if memory > 80 else 'memory_leak_buildup'
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label=label
                ))
            
            # Remediation (restart) - sudden drop
            remediation_time = leak_start + timedelta(hours=leak_duration_hours)
            for minute in range(5):
                timestamp = remediation_time + timedelta(minutes=minute)
                
                cpu = 25 + np.random.normal(0, 3)
                memory = 30 + np.random.normal(0, 2)
                error_rate = 0.02
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='memory_leak_remediated'
                ))
        
        logger.info(f"Generated {len(all_data)} memory leak samples across {count} incidents")
        return pd.DataFrame(all_data)
    
    def generate_error_storm_scenarios(self, count: int = 25) -> pd.DataFrame:
        """
        Generate error storm scenarios (sudden spike in errors).
        
        Args:
            count: Number of error storm scenarios
            
        Returns:
            DataFrame with error storm scenarios
        """
        logger.info(f"Generating {count} error storm scenarios...")
        
        all_data = []
        base_time = datetime.now() - timedelta(days=20)
        
        for i in range(count):
            storm_start = base_time + timedelta(
                days=np.random.randint(0, 20),
                hours=np.random.randint(8, 20)
            )
            
            # Error storm (5-10 minutes)
            storm_duration = np.random.randint(5, 11)
            for minute in range(storm_duration):
                timestamp = storm_start + timedelta(minutes=minute)
                
                cpu = 40 + np.random.normal(0, 10)
                memory = 50 + np.random.normal(0, 5)
                error_rate = np.random.uniform(0.30, 0.60)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='error_storm_active'
                ))
            
            # Recovery (15 minutes)
            recovery_start = storm_start + timedelta(minutes=storm_duration)
            for minute in range(15):
                timestamp = recovery_start + timedelta(minutes=minute)
                progress = minute / 15
                
                cpu = 40 - (progress * 10) + np.random.normal(0, 3)
                memory = 50 - (progress * 10) + np.random.normal(0, 2)
                error_rate = 0.40 - (progress * 0.38)
                
                all_data.append(self._create_sample(
                    timestamp, cpu, memory, error_rate, label='error_storm_recovery'
                ))
        
        logger.info(f"Generated {len(all_data)} error storm samples across {count} incidents")
        return pd.DataFrame(all_data)
    
    def _create_sample(self, timestamp: datetime, cpu: float, memory: float, 
                       error_rate: float, label: str = 'normal') -> Dict:
        """Helper to create a consistent sample dictionary"""
        requests = max(50, int(200 + np.random.normal(0, 50)))
        errors = int(requests * error_rate)
        
        return {
            'timestamp': timestamp,
            'cpu_percent': round(max(0, min(100, cpu)), 2),
            'memory_percent': round(max(0, min(100, memory)), 2),
            'memory_mb': round(memory * 40, 2),
            'disk_usage_percent': round(45 + np.random.uniform(-2, 2), 2),
            'request_count': requests,
            'error_count': errors,
            'error_rate': round(max(0, min(1, error_rate)), 4),
            'active_connections': max(0, int(requests * 0.1 + np.random.normal(0, 5))),
            'response_time_p50': round(max(5, 15 + (error_rate * 100) + np.random.normal(0, 5)), 2),
            'response_time_p95': round(max(20, 50 + (error_rate * 300) + np.random.normal(0, 20)), 2),
            'response_time_p99': round(max(50, 100 + (error_rate * 500) + np.random.normal(0, 50)), 2),
            'response_time_avg': round(max(10, 30 + (error_rate * 200)), 2),
            'label': label
        }
    
    def generate_full_training_set(self, normal_days: int = 30) -> pd.DataFrame:
        """
        Generate complete synthetic dataset with mix of normal and anomalous data.
        
        Distribution:
        - 85% normal operation
        - 7.5% CPU spikes
        - 4% memory leaks
        - 3.5% error storms
        
        Args:
            normal_days: Days of normal operation to generate
            
        Returns:
            Complete training dataset
        """
        logger.info("Generating full training dataset...")
        
        # Generate all scenarios
        normal = self.generate_normal_operation(days=normal_days)
        cpu_spikes = self.generate_cpu_spike_scenarios(count=50)
        memory_leaks = self.generate_memory_leak_scenarios(count=25)
        error_storms = self.generate_error_storm_scenarios(count=25)
        
        # Combine all data
        full_dataset = pd.concat([normal, cpu_spikes, memory_leaks, error_storms], ignore_index=True)
        
        # Sort by timestamp
        full_dataset = full_dataset.sort_values('timestamp').reset_index(drop=True)
        
        # Add derived features
        full_dataset = self._add_derived_features(full_dataset)
        
        logger.info(f"Generated complete dataset: {len(full_dataset)} samples")
        logger.info(f"Label distribution:\n{full_dataset['label'].value_counts()}")
        
        return full_dataset
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rate-of-change features"""
        df = df.copy()
        
        # Calculate rates of change
        df['cpu_rate_of_change'] = df['cpu_percent'].diff().fillna(0)
        df['memory_rate_of_change'] = df['memory_percent'].diff().fillna(0)
        df['error_rate_trend'] = df['error_rate'].diff().fillna(0)
        
        return df
    
    def save_to_csv(self, data: pd.DataFrame, filepath: str):
        """Save generated data to CSV file"""
        data.to_csv(filepath, index=False)
        logger.info(f"Saved {len(data)} samples to {filepath}")
    
    def save_to_database(self, data: pd.DataFrame, db_connection):
        """Save generated data directly to database"""
        try:
            # Remove 'label' column for database insert
            db_data = data.drop(columns=['label'])
            
            db_data.to_sql(
                'metrics_history',
                db_connection,
                if_exists='append',
                index=False
            )
            logger.info(f"Inserted {len(db_data)} synthetic samples into database")
        except Exception as e:
            logger.error(f"Error inserting to database: {e}")
            raise


def main():
    """CLI for generating synthetic data"""
    parser = argparse.ArgumentParser(description='Generate synthetic training data for ML')
    parser.add_argument('--days', type=int, default=30, help='Days of normal operation')
    parser.add_argument('--output', type=str, default='data/synthetic_training.csv', 
                       help='Output CSV file path')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Generate data
    generator = SyntheticDataGenerator(random_seed=args.seed)
    data = generator.generate_full_training_set(normal_days=args.days)
    
    # Save to file
    generator.save_to_csv(data, args.output)
    
    print(f"\n✅ Successfully generated {len(data)} training samples!")
    print(f"📁 Saved to: {args.output}")
    print(f"\nLabel distribution:")
    print(data['label'].value_counts())
    print(f"\nData shape: {data.shape}")
    print(f"Date range: {data['timestamp'].min()} to {data['timestamp'].max()}")


if __name__ == '__main__':
    main()
