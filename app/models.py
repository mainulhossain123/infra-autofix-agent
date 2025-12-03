"""
Database models using SQLAlchemy ORM.
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DECIMAL, TIMESTAMP, ForeignKey, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import Config

Base = declarative_base()
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Incident(Base):
    """Incident model"""
    __tablename__ = 'incidents'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    details = Column(JSON, default={})
    status = Column(String(20), default='ACTIVE')
    resolved_at = Column(TIMESTAMP)
    resolution_time_seconds = Column(Integer)
    affected_service = Column(String(100))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    remediation_actions = relationship("RemediationAction", back_populates="incident", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'type': self.type,
            'severity': self.severity,
            'details': self.details,
            'status': self.status,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolution_time_seconds': self.resolution_time_seconds,
            'affected_service': self.affected_service,
            'remediation_count': len(self.remediation_actions) if self.remediation_actions else 0
        }


class RemediationAction(Base):
    """Remediation action model"""
    __tablename__ = 'remediation_actions'
    
    id = Column(Integer, primary_key=True)
    incident_id = Column(Integer, ForeignKey('incidents.id', ondelete='CASCADE'))
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    action_type = Column(String(50), nullable=False)
    target = Column(String(100), nullable=False)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    triggered_by = Column(String(50), default='bot')
    action_metadata = Column('metadata', JSON, default={})  # Renamed to avoid SQLAlchemy conflict
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationship
    incident = relationship("Incident", back_populates="remediation_actions")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'action_type': self.action_type,
            'target': self.target,
            'success': self.success,
            'error_message': self.error_message,
            'execution_time_ms': self.execution_time_ms,
            'triggered_by': self.triggered_by,
            'metadata': self.action_metadata  # Use the renamed attribute
        }


class MetricsSnapshot(Base):
    """Metrics snapshot model"""
    __tablename__ = 'metrics_snapshots'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    service_name = Column(String(100), default='ar_app')
    total_requests = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    error_rate = Column(DECIMAL(5, 4), default=0.0)
    cpu_usage_percent = Column(DECIMAL(5, 2), default=0.0)
    memory_usage_mb = Column(Integer, default=0)
    response_time_p50_ms = Column(Integer)
    response_time_p95_ms = Column(Integer)
    response_time_p99_ms = Column(Integer)
    active_connections = Column(Integer, default=0)
    uptime_seconds = Column(Integer, default=0)
    snapshot_metadata = Column('metadata', JSON, default={})  # Renamed to avoid SQLAlchemy conflict
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'service_name': self.service_name,
            'total_requests': self.total_requests,
            'total_errors': self.total_errors,
            'error_rate': float(self.error_rate) if self.error_rate else 0.0,
            'cpu_usage_percent': float(self.cpu_usage_percent) if self.cpu_usage_percent else 0.0,
            'memory_usage_mb': self.memory_usage_mb,
            'response_time_p50_ms': self.response_time_p50_ms,
            'response_time_p95_ms': self.response_time_p95_ms,
            'response_time_p99_ms': self.response_time_p99_ms,
            'active_connections': self.active_connections,
            'uptime_seconds': self.uptime_seconds,
            'metadata': self.snapshot_metadata  # Use the renamed attribute
        }


class ConfigEntry(Base):
    """Configuration entry model"""
    __tablename__ = 'config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(100), default='system')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'updated_by': self.updated_by
        }


class ActionHistory(Base):
    """Action history for rate limiting"""
    __tablename__ = 'action_history'
    
    id = Column(Integer, primary_key=True)
    service_name = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    success = Column(Boolean, nullable=False)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(engine)


def get_db_session():
    """Get a new database session"""
    return SessionLocal()
