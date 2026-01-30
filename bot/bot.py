"""
Auto-Remediation Bot - Main monitoring loop.
Monitors application health and performs automated remediation actions.
"""
import os
import sys
import time
import logging
import requests
from datetime import datetime
from urllib.parse import urljoin
from dotenv import load_dotenv

# Import bot components
from detectors import DetectorManager
from remediation import RemediationStrategy
from circuit_breaker import CircuitBreaker
from notifications import NotificationManager
from cleanup import DataCleanup

# Database imports (shared with app)
sys.path.append('/usr/src/bot')
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    
    # Define minimal models for bot (to avoid full import from app)
    class BotDB:
        def __init__(self, database_url):
            self.engine = create_engine(database_url, echo=False)
            self.SessionLocal = sessionmaker(bind=self.engine)
        
        def get_session(self):
            return self.SessionLocal()
        
        def log_incident(self, session, incident_data, affected_service):
            """Log incident to database"""
            try:
                import json
                query = text("""
                INSERT INTO incidents (timestamp, type, severity, details, status, affected_service)
                VALUES (NOW(), :type, :severity, CAST(:details AS jsonb), 'ACTIVE', :service)
                RETURNING id
                """)
                result = session.execute(query, {
                    'type': incident_data['type'],
                    'severity': incident_data['severity'],
                    'details': json.dumps(incident_data['details']),
                    'service': affected_service
                })
                session.commit()
                incident_id = result.fetchone()[0]
                return incident_id
            except Exception as e:
                session.rollback()
                logging.error(f"Failed to log incident: {e}")
                return None
        
        def log_remediation_action(self, session, incident_id, action_type, target, success, error_msg, exec_time_ms):
            """Log remediation action to database"""
            try:
                query = text("""
                INSERT INTO remediation_actions 
                (incident_id, timestamp, action_type, target, success, error_message, execution_time_ms, triggered_by)
                VALUES (:incident_id, NOW(), :action_type, :target, :success, :error_msg, :exec_time, 'bot')
                """)
                session.execute(query, {
                    'incident_id': incident_id,
                    'action_type': action_type,
                    'target': target,
                    'success': success,
                    'error_msg': error_msg,
                    'exec_time': exec_time_ms
                })
                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(f"Failed to log remediation action: {e}")
        
        def update_incident_resolved(self, session, incident_id):
            """Mark incident as resolved"""
            try:
                query = text("""
                UPDATE incidents
                SET status = 'RESOLVED',
                    resolved_at = NOW(),
                    resolution_time_seconds = EXTRACT(EPOCH FROM (NOW() - timestamp))::INTEGER
                WHERE id = :incident_id
                """)
                session.execute(query, {'incident_id': incident_id})
                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(f"Failed to update incident: {e}")
        
        def get_thresholds(self, session):
            """Get thresholds from config table"""
            try:
                query = text("SELECT value FROM config WHERE key = 'thresholds'")
                result = session.execute(query)
                row = result.fetchone()
                if row:
                    import json
                    return json.loads(row[0]) if isinstance(row[0], str) else row[0]
            except Exception as e:
                logging.error(f"Failed to get thresholds: {e}")
            
            # Return defaults
            return {
                'error_rate': 0.2,
                'cpu_percent': 80,
                'response_time_ms': 500
            }
    
    DB_AVAILABLE = True
except Exception as e:
    logging.warning(f"Database imports failed: {e}. Running without DB persistence.")
    DB_AVAILABLE = False
    BotDB = None

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutoRemediationBot:
    """Main auto-remediation bot"""
    
    def __init__(self):
        """Initialize the bot"""
        # Configuration
        self.app_host = os.getenv('APP_HOST', 'http://app:5000')
        self.poll_seconds = int(os.getenv('BOT_POLL_SECONDS', 5))
        
        # Get thresholds from environment (can be overridden from DB)
        self.thresholds = {
            'error_rate': float(os.getenv('ERROR_RATE_THRESHOLD', 0.2)),
            'cpu_percent': int(os.getenv('CPU_THRESHOLD', 80)),
            'response_time_ms': int(os.getenv('RESPONSE_TIME_THRESHOLD_MS', 500))
        }
        
        # Circuit breaker settings
        max_restarts = int(os.getenv('MAX_RESTARTS_PER_5MIN', 3))
        cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', 120))
        
        # Initialize components
        self.detector_manager = DetectorManager(self.thresholds)
        self.remediation_strategy = RemediationStrategy()
        self.circuit_breaker = CircuitBreaker(
            max_failures=max_restarts,
            window_seconds=300,
            cooldown_seconds=cooldown_seconds
        )
        self.notification_manager = NotificationManager(
            slack_webhook=os.getenv('SLACK_WEBHOOK_URL'),
            enable_console=True
        )
        
        # Database
        self.db = None
        if DB_AVAILABLE:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://remediation_user:remediation_pass@postgres:5432/remediation_db'
            )
            try:
                self.db = BotDB(database_url)
                logger.info("Database connection initialized")
            except Exception as e:
                logger.error(f"Failed to initialize database: {e}")
        
        # State
        self.last_incident_time = {}  # Track last incident time per type for deduplication
        self.incident_dedupe_window = 60  # Don't log duplicate incidents within 60 seconds
        
        # Cleanup manager
        retention_days = int(os.getenv('DATA_RETENTION_DAYS', 180))  # Default: 6 months
        self.cleanup_manager = DataCleanup(retention_days=retention_days)
        self.last_cleanup_time = None
        self.cleanup_interval_hours = int(os.getenv('CLEANUP_INTERVAL_HOURS', 24))  # Default: daily
        
        # Failure prediction (Phase 5)
        self.failure_predictor = None
        self.failure_prediction_enabled = os.getenv('ENABLE_FAILURE_PREDICTION', 'true').lower() == 'true'
        self.failure_check_interval = int(os.getenv('FAILURE_CHECK_INTERVAL', 300))  # Check every 5 minutes
        self.last_failure_check_time = None
        
        if self.failure_prediction_enabled:
            try:
                from ml.failure_predictor import FailurePredictor
                if self.db:
                    session = self.db.get_session()
                    self.failure_predictor = FailurePredictor(session.connection())
                    logger.info("Failure predictor initialized")
                else:
                    logger.warning("Failure predictor disabled - no database connection")
            except ImportError:
                logger.warning("Failure predictor not available - install lightgbm")
            except Exception as e:
                logger.warning(f"Failed to initialize failure predictor: {e}")
        
        logger.info("Auto-Remediation Bot initialized")
        logger.info(f"Monitoring: {self.app_host}")
        logger.info(f"Poll interval: {self.poll_seconds}s")
        logger.info(f"Thresholds: {self.thresholds}")
        logger.info(f"Circuit breaker: max {max_restarts} actions per 5min, cooldown {cooldown_seconds}s")
        logger.info(f"Data cleanup: retention {retention_days} days, runs every {self.cleanup_interval_hours} hours")
    
    def _trigger_llm_analysis(self, incident_id: int, incident: dict):
        """
        Trigger LLM analysis for incident (non-blocking)
        
        Args:
            incident_id: Database incident ID
            incident: Incident dictionary
        """
        try:
            # Import LLM analyzer
            try:
                from ml.llm_analyzer import LLMAnalyzer
                
                analyzer = LLMAnalyzer()
                if not analyzer.is_available:
                    logger.debug("LLM service not available, skipping analysis")
                    return
                
                # Analyze incident
                analysis = analyzer.analyze_incident(incident)
                
                # Store in database
                if self.db:
                    session = self.db.get_session()
                    try:
                        query = text("""
                            INSERT INTO llm_analyses (incident_id, root_cause, suggested_actions,
                                                     explanation, confidence, model_used, analyzed_at)
                            VALUES (:incident_id, :root_cause, :suggestions, :explanation,
                                   :confidence, :model, NOW())
                        """)
                        session.execute(query, {
                            'incident_id': incident_id,
                            'root_cause': analysis.get('root_cause', ''),
                            'suggestions': str(analysis.get('suggestions', [])),
                            'explanation': analysis.get('explanation', ''),
                            'confidence': analysis.get('confidence', 'medium'),
                            'model': analysis.get('model', 'llama3.2:3b')
                        })
                        session.commit()
                        logger.info(f"LLM analysis stored for incident {incident_id}: {analysis.get('root_cause', '')[:100]}")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Failed to store LLM analysis: {e}")
                    finally:
                        session.close()
                        
            except ImportError:
                logger.debug("LLM analyzer not available (ml module not installed)")
                return
                
        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}", exc_info=True)
    
    def _check_failure_prediction(self):
        """
        Check failure prediction and create proactive incidents if high risk detected.
        Runs periodically based on failure_check_interval.
        """
        current_time = time.time()
        
        # Check if we should run prediction
        if self.last_failure_check_time:
            time_since_last_check = current_time - self.last_failure_check_time
            if time_since_last_check < self.failure_check_interval:
                return  # Not time yet
        
        self.last_failure_check_time = current_time
        
        if not self.failure_predictor:
            return
        
        try:
            # Get prediction for next hour
            prediction = self.failure_predictor.predict(lookback_hours=1)
            
            if prediction.get('status') != 'success':
                logger.debug(f"Failure prediction not available: {prediction.get('message')}")
                return
            
            probability = prediction['probability']
            risk_level = prediction['risk_level']
            
            logger.info(f"Failure prediction: {probability:.2%} probability, {risk_level} risk")
            
            # Create proactive incident for high/medium risk
            if risk_level in ['high', 'medium']:
                # Check if we already alerted recently (avoid spam)
                incident_key = f"predicted_failure_{risk_level}"
                now = datetime.now().timestamp()
                
                if incident_key in self.last_incident_time:
                    time_since = now - self.last_incident_time[incident_key]
                    if time_since < 600:  # Don't alert more than once per 10 minutes
                        return
                
                self.last_incident_time[incident_key] = now
                
                # Log proactive incident
                if self.db:
                    session = self.db.get_session()
                    try:
                        incident_data = {
                            'type': 'predicted_failure',
                            'severity': 'HIGH' if risk_level == 'high' else 'MEDIUM',
                            'details': {
                                'probability': probability,
                                'risk_level': risk_level,
                                'message': prediction['message'],
                                'top_features': prediction.get('top_contributing_features', [])
                            }
                        }
                        
                        incident_id = self.db.log_incident(
                            session, 
                            incident_data,
                            'infrastructure'
                        )
                        session.commit()
                        
                        # Send notification
                        severity_emoji = "🔴" if risk_level == 'high' else "🟡"
                        self.notification_manager.send_notification(
                            f"{severity_emoji} Predicted Failure: {probability:.0%} chance of system failure in the next hour",
                            incident_data['severity']
                        )
                        
                        logger.warning(f"Proactive failure incident created: {probability:.0%} risk")
                        
                    except Exception as e:
                        logger.error(f"Error logging predicted failure incident: {e}", exc_info=True)
                        session.rollback()
                    finally:
                        session.close()
                        
        except Exception as e:
            logger.error(f"Error checking failure prediction: {e}", exc_info=True)
    
    def get_health(self):
        """
        Get health status from application.
        
        Returns:
            (health_data: dict, error: str)
        """
        try:
            url = urljoin(self.app_host, '/api/health')
            response = requests.get(url, timeout=3)
            
            if response.status_code != 200:
                return None, f"HTTP {response.status_code}"
            
            return response.json(), None
        
        except requests.exceptions.ConnectionError:
            return None, "connection_refused"
        except requests.exceptions.Timeout:
            return None, "timeout"
        except Exception as e:
            return None, str(e)
    
    def should_deduplicate_incident(self, incident_type: str) -> bool:
        """Check if we should skip this incident due to recent duplicate"""
        current_time = time.time()
        last_time = self.last_incident_time.get(incident_type, 0)
        
        if current_time - last_time < self.incident_dedupe_window:
            logger.debug(f"Deduplicating incident: {incident_type} (seen {int(current_time - last_time)}s ago)")
            return True
        
        self.last_incident_time[incident_type] = current_time
        return False
    
    def handle_incidents(self, incidents: list, health_data: dict):
        """
        Handle detected incidents.
        
        Args:
            incidents: List of incident dictionaries
            health_data: Current health data from app
        """
        service_name = health_data.get('service', 'ar_app') if health_data else 'ar_app'
        
        for incident in incidents:
            incident_type = incident['type']
            severity = incident['severity']
            
            # Deduplicate incidents
            if self.should_deduplicate_incident(incident_type):
                continue
            
            logger.warning(f"Incident detected: {incident_type} ({severity})")
            
            # Notify about incident
            self.notification_manager.notify_incident_detected(incident, service_name)
            
            # Log incident to database
            incident_id = None
            if self.db:
                session = self.db.get_session()
                try:
                    incident_id = self.db.log_incident(session, incident, service_name)
                    
                    # Trigger LLM analysis asynchronously
                    if incident_id:
                        self._trigger_llm_analysis(incident_id, incident)
                        
                except Exception as e:
                    logger.error(f"Failed to log incident: {e}")
                finally:
                    session.close()
            
            # Determine remediation action
            action = self.remediation_strategy.get_action_for_incident(incident)
            
            if not action:
                logger.info(f"No remediation action defined for {incident_type}")
                continue
            
            action_type = action['action_type']
            target = action['target']
            reason = action.get('reason', 'No reason provided')
            
            # Check circuit breaker
            can_execute, cb_reason = self.circuit_breaker.can_execute(target, action_type)
            
            if not can_execute:
                logger.warning(f"Circuit breaker blocked action: {cb_reason}")
                self.notification_manager.notify_circuit_breaker_opened(target, cb_reason)
                
                # Consider escalation if circuit is open
                self.notification_manager.notify_escalation(
                    target,
                    f"Circuit breaker open, auto-remediation blocked: {cb_reason}"
                )
                continue
            
            # Execute remediation
            logger.info(f"Executing remediation: {action_type} on {target}")
            self.notification_manager.notify_remediation_started(action_type, target, reason)
            
            success, error_message, execution_time_ms = self.remediation_strategy.execute_action(action)
            
            # Record action in circuit breaker
            self.circuit_breaker.record_action(target, action_type, success)
            
            # Log remediation action to database
            if self.db and incident_id:
                session = self.db.get_session()
                try:
                    self.db.log_remediation_action(
                        session, incident_id, action_type, target,
                        success, error_message, execution_time_ms
                    )
                    
                    # Mark incident as resolved if action succeeded
                    if success:
                        self.db.update_incident_resolved(session, incident_id)
                except Exception as e:
                    logger.error(f"Failed to log remediation: {e}")
                finally:
                    session.close()
            
            # Notify about result
            if success:
                logger.info(f"Remediation successful: {action_type} on {target} ({execution_time_ms}ms)")
                self.notification_manager.notify_remediation_success(action_type, target, execution_time_ms)
            else:
                logger.error(f"Remediation failed: {action_type} on {target} - {error_message}")
                self.notification_manager.notify_remediation_failure(action_type, target, error_message)
                
                # Escalate if remediation failed
                self.notification_manager.notify_escalation(
                    target,
                    f"Remediation action failed: {error_message}"
                )
    
    def update_thresholds_from_db(self):
        """Update thresholds from database config"""
        if not self.db:
            return
        
        try:
            session = self.db.get_session()
            thresholds = self.db.get_thresholds(session)
            session.close()
            
            if thresholds and thresholds != self.thresholds:
                logger.info(f"Updating thresholds from database: {thresholds}")
                self.thresholds = thresholds
                self.detector_manager.update_thresholds(thresholds)
        except Exception as e:
            logger.error(f"Failed to update thresholds from DB: {e}")
    
    def run_cleanup_if_needed(self):
        """Run database cleanup if interval has passed"""
        from datetime import datetime, timedelta
        
        now = datetime.utcnow()
        
        # Run cleanup if:
        # 1. Never run before (first time)
        # 2. Interval has passed since last cleanup
        should_cleanup = (
            self.last_cleanup_time is None or
            (now - self.last_cleanup_time).total_seconds() >= (self.cleanup_interval_hours * 3600)
        )
        
        if should_cleanup:
            try:
                logger.info("Running scheduled database cleanup...")
                stats_before = self.cleanup_manager.get_database_stats()
                logger.info(f"Database stats before cleanup: {stats_before}")
                
                result = self.cleanup_manager.cleanup_old_records()
                
                if result['incidents'] > 0 or result['remediation_actions'] > 0:
                    logger.info(f"Cleanup completed: Deleted {result['incidents']} incidents and {result['remediation_actions']} remediation actions")
                    self.notification_manager.send_notification(
                        f"🗑️ Database cleanup completed: Removed {result['incidents']} old incidents and {result['remediation_actions']} remediation actions (older than {self.cleanup_manager.retention_days} days)",
                        "INFO"
                    )
                else:
                    logger.info("Cleanup completed: No old records to delete")
                
                self.last_cleanup_time = now
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)
                self.notification_manager.send_notification(
                    f"⚠️ Database cleanup failed: {str(e)}",
                    "WARNING"
                )
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop...")
        
        # Update thresholds from DB on startup
        self.update_thresholds_from_db()
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Periodically update thresholds from DB (every 10 iterations)
                if iteration % 10 == 0:
                    self.update_thresholds_from_db()
                
                # Run cleanup if needed (checks interval internally)
                self.run_cleanup_if_needed()
                
                # Check failure prediction (Phase 5)
                if self.failure_prediction_enabled and self.failure_predictor:
                    self._check_failure_prediction()
                
                # Get health status
                health_data, error = self.get_health()
                
                if error:
                    logger.warning(f"Health check failed: {error}")
                    # Treat health check failure as an incident
                    incidents = [{
                        'type': 'health_check_failed',
                        'severity': 'CRITICAL',
                        'details': {'error': error}
                    }]
                else:
                    # Detect incidents from health data
                    incidents = self.detector_manager.detect_all(health_data)
                
                # Handle any detected incidents
                if incidents:
                    self.handle_incidents(incidents, health_data)
                else:
                    logger.debug("No incidents detected - system healthy")
                
                # Sleep until next poll
                time.sleep(self.poll_seconds)
            
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(self.poll_seconds)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Auto-Remediation Bot v1.0")
    logger.info("=" * 60)
    
    # Wait for app to be ready
    logger.info("Waiting for application to be ready...")
    time.sleep(10)
    
    # Create and run bot
    bot = AutoRemediationBot()
    bot.run()


if __name__ == '__main__':
    main()
