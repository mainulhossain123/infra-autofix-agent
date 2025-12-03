"""
Automatic cleanup of old incidents and remediation logs.
Removes records older than 6 months to prevent database bloat.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

logger = logging.getLogger(__name__)


class DataCleanup:
    """Handles automatic cleanup of old database records"""
    
    def __init__(self, retention_days: int = 180, database_url: str = None):
        """
        Initialize cleanup handler.
        
        Args:
            retention_days: Number of days to retain data (default: 180 = 6 months)
            database_url: Database connection URL
        """
        self.retention_days = retention_days
        
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://remediation_user:remediation_pass@postgres:5432/remediation_db'
            )
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Data cleanup initialized with {retention_days} day retention policy")
    
    def cleanup_old_records(self) -> Dict[str, int]:
        """
        Remove incidents and remediation actions older than retention period.
        
        IMPORTANT: Only deletes records OLDER than retention_days.
        For example, with 180 days retention:
        - KEEPS: All records from the last 6 months
        - DELETES: Only records created more than 6 months ago
        
        Returns:
            Dict with counts of deleted records
        """
        # Calculate cutoff date: records OLDER than this will be deleted
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        logger.info(f"Starting cleanup of records older than {cutoff_date.isoformat()}")
        
        session = self.SessionLocal()
        try:
            # Count records before deletion
            count_incidents_query = text("""
                SELECT COUNT(*) FROM incidents WHERE timestamp < :cutoff_date
            """)
            count_remediations_query = text("""
                SELECT COUNT(*) FROM remediation_actions WHERE timestamp < :cutoff_date
            """)
            
            old_incidents = session.execute(count_incidents_query, {'cutoff_date': cutoff_date}).scalar()
            old_remediations = session.execute(count_remediations_query, {'cutoff_date': cutoff_date}).scalar()
            
            if old_incidents == 0 and old_remediations == 0:
                logger.info("No old records found to clean up")
                return {'incidents': 0, 'remediation_actions': 0}
            
            logger.info(f"Found {old_incidents} incidents and {old_remediations} remediation actions to delete")
            
            # Delete old incidents (cascades to remediation_actions due to FK constraint)
            delete_incidents_query = text("""
                DELETE FROM incidents WHERE timestamp < :cutoff_date
            """)
            result_incidents = session.execute(delete_incidents_query, {'cutoff_date': cutoff_date})
            deleted_incidents = result_incidents.rowcount
            
            # Delete orphaned remediation actions (shouldn't exist due to cascade, but just in case)
            delete_remediations_query = text("""
                DELETE FROM remediation_actions WHERE timestamp < :cutoff_date
            """)
            result_remediations = session.execute(delete_remediations_query, {'cutoff_date': cutoff_date})
            deleted_remediations = result_remediations.rowcount
            
            session.commit()
            
            result = {
                'incidents': deleted_incidents,
                'remediation_actions': deleted_remediations
            }
            
            logger.info(f"Cleanup completed: {deleted_incidents} incidents and {deleted_remediations} remediation actions deleted")
            return result
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def get_database_stats(self) -> Dict[str, any]:
        """
        Get current database statistics.
        
        Returns:
            Dict with database statistics
        """
        session = self.SessionLocal()
        try:
            # Get total counts
            total_incidents = session.execute(text("SELECT COUNT(*) FROM incidents")).scalar()
            total_remediations = session.execute(text("SELECT COUNT(*) FROM remediation_actions")).scalar()
            
            # Get old record counts
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            old_incidents = session.execute(
                text("SELECT COUNT(*) FROM incidents WHERE timestamp < :cutoff_date"),
                {'cutoff_date': cutoff_date}
            ).scalar()
            old_remediations = session.execute(
                text("SELECT COUNT(*) FROM remediation_actions WHERE timestamp < :cutoff_date"),
                {'cutoff_date': cutoff_date}
            ).scalar()
            
            # Get oldest record
            oldest_result = session.execute(
                text("SELECT MIN(timestamp) FROM incidents")
            ).scalar()
            
            stats = {
                'total_incidents': total_incidents,
                'total_remediation_actions': total_remediations,
                'old_incidents': old_incidents,
                'old_remediation_actions': old_remediations,
                'oldest_record_date': oldest_result.isoformat() if oldest_result else None,
                'retention_days': self.retention_days,
                'cutoff_date': cutoff_date.isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}", exc_info=True)
            raise
        finally:
            session.close()


def run_cleanup(retention_days: int = 180):
    """
    Standalone function to run cleanup.
    
    Args:
        retention_days: Number of days to retain data
    """
    cleanup = DataCleanup(retention_days=retention_days)
    
    # Log current stats before cleanup
    stats_before = cleanup.get_database_stats()
    logger.info(f"Database stats before cleanup: {stats_before}")
    
    # Perform cleanup
    result = cleanup.cleanup_old_records()
    
    # Log stats after cleanup
    stats_after = cleanup.get_database_stats()
    logger.info(f"Database stats after cleanup: {stats_after}")
    
    return result


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run cleanup
    result = run_cleanup()
    print(f"Cleanup completed: {result}")
