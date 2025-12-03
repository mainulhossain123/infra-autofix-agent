"""
WebSocket server for real-time metric streaming
"""
from flask_socketio import SocketIO, emit
from flask import request
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=False
    )
    
    @socketio.on('connect')
    def handle_connect():
        logger.info(f"Client connected: {request.sid}")
        emit('connection_established', {
            'status': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'message': 'WebSocket connection established'
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('subscribe_metrics')
    def handle_subscribe_metrics(data):
        logger.info(f"Client {request.sid} subscribed to metrics")
        emit('subscription_confirmed', {
            'channel': 'metrics',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @socketio.on('subscribe_incidents')
    def handle_subscribe_incidents(data):
        logger.info(f"Client {request.sid} subscribed to incidents")
        emit('subscription_confirmed', {
            'channel': 'incidents',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return socketio

def broadcast_metric_update(metrics):
    """Broadcast metric update to all connected clients"""
    if socketio:
        socketio.emit('metric_update', {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': metrics
        })

def broadcast_incident(incident):
    """Broadcast new incident to all connected clients"""
    if socketio:
        socketio.emit('incident_created', {
            'timestamp': datetime.utcnow().isoformat(),
            'incident': incident
        })

def broadcast_remediation(action):
    """Broadcast remediation action to all connected clients"""
    if socketio:
        socketio.emit('remediation_executed', {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action
        })

def broadcast_health_update(health_data):
    """Broadcast health status update"""
    if socketio:
        socketio.emit('health_update', {
            'timestamp': datetime.utcnow().isoformat(),
            'health': health_data
        })
