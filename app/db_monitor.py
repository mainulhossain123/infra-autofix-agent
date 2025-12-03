"""
PostgreSQL Database Monitoring Module
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Monitor PostgreSQL database health and performance"""
    
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv('DATABASE_URL')
        
    def get_connection_stats(self):
        """Get connection pool statistics"""
        query = """
        SELECT 
            count(*) as total_connections,
            count(*) FILTER (WHERE state = 'active') as active,
            count(*) FILTER (WHERE state = 'idle') as idle,
            count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
            (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
            (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') - count(*) as available
        FROM pg_stat_activity;
        """
        return self._execute_query(query)
    
    def get_database_size(self):
        """Get database size in MB"""
        query = """
        SELECT 
            current_database() as database_name,
            pg_size_pretty(pg_database_size(current_database())) as size_pretty,
            round(pg_database_size(current_database())::numeric / 1024 / 1024, 2) as size_mb
        """
        return self._execute_query(query)
    
    def get_cache_hit_ratio(self):
        """Get buffer cache hit ratio"""
        query = """
        SELECT 
            sum(heap_blks_read) as heap_read,
            sum(heap_blks_hit) as heap_hit,
            CASE 
                WHEN sum(heap_blks_hit) + sum(heap_blks_read) = 0 THEN 100.0
                ELSE round((sum(heap_blks_hit)::numeric / (sum(heap_blks_hit) + sum(heap_blks_read))) * 100, 2)
            END as cache_hit_ratio
        FROM pg_statio_user_tables;
        """
        result = self._execute_query(query)
        return result if result else {'cache_hit_ratio': 100.0, 'heap_read': 0, 'heap_hit': 0}
    
    def get_transaction_stats(self):
        """Get transaction statistics"""
        query = """
        SELECT 
            xact_commit as commits,
            xact_rollback as rollbacks,
            CASE 
                WHEN xact_commit + xact_rollback = 0 THEN 0.0
                ELSE round((xact_rollback::numeric / (xact_commit + xact_rollback)) * 100, 2)
            END as rollback_ratio,
            deadlocks
        FROM pg_stat_database
        WHERE datname = current_database();
        """
        return self._execute_query(query)
    
    def check_health(self):
        """Comprehensive health check"""
        try:
            conn_stats = self.get_connection_stats()
            cache_ratio = self.get_cache_hit_ratio()
            db_size = self.get_database_size()
            trans_stats = self.get_transaction_stats()
            
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'connections': {
                    'total': conn_stats['total_connections'],
                    'active': conn_stats['active'],
                    'idle': conn_stats['idle'],
                    'max': conn_stats['max_connections'],
                    'available': conn_stats['available'],
                    'utilization_percent': round((conn_stats['total_connections'] / conn_stats['max_connections']) * 100, 2)
                },
                'cache': {
                    'hit_ratio': cache_ratio['cache_hit_ratio'],
                    'heap_read': cache_ratio['heap_read'],
                    'heap_hit': cache_ratio['heap_hit']
                },
                'size': {
                    'database_mb': db_size['size_mb'],
                    'database_pretty': db_size['size_pretty']
                },
                'transactions': {
                    'commits': trans_stats['commits'],
                    'rollbacks': trans_stats['rollbacks'],
                    'rollback_ratio': trans_stats['rollback_ratio'],
                    'deadlocks': trans_stats['deadlocks']
                },
                'issues': []
            }
            
            # Health checks
            if conn_stats['available'] < 10:
                health['issues'].append({
                    'severity': 'critical',
                    'type': 'connection_pool_exhaustion',
                    'message': f"Only {conn_stats['available']} connections available"
                })
                health['status'] = 'critical'
            elif conn_stats['utilization_percent'] > 80:
                health['issues'].append({
                    'severity': 'warning',
                    'type': 'high_connection_usage',
                    'message': f"Connection pool {conn_stats['utilization_percent']}% utilized"
                })
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            
            if cache_ratio['cache_hit_ratio'] < 95:
                health['issues'].append({
                    'severity': 'warning',
                    'type': 'low_cache_hit_ratio',
                    'message': f"Cache hit ratio: {cache_ratio['cache_hit_ratio']:.2f}% (should be >95%)"
                })
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            
            if trans_stats['rollback_ratio'] > 5:
                health['issues'].append({
                    'severity': 'warning',
                    'type': 'high_rollback_ratio',
                    'message': f"Rollback ratio: {trans_stats['rollback_ratio']}% (should be <5%)"
                })
                if health['status'] == 'healthy':
                    health['status'] = 'warning'
            
            if trans_stats['deadlocks'] > 0:
                health['issues'].append({
                    'severity': 'critical',
                    'type': 'deadlocks_detected',
                    'message': f"{trans_stats['deadlocks']} deadlocks detected"
                })
                health['status'] = 'critical'
            
            return health
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'issues': [{
                    'severity': 'critical',
                    'type': 'health_check_failed',
                    'message': f"Failed to check database health: {str(e)}"
                }]
            }
    
    def _execute_query(self, query, fetch_all=False):
        """Execute SQL query and return results"""
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            
            if fetch_all:
                result = cursor.fetchall()
                return [dict(row) for row in result] if result else []
            else:
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return [] if fetch_all else None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
