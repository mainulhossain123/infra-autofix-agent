import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = {
      metrics: [],
      incidents: [],
      health: [],
      connect: [],
      disconnect: []
    };
  }

  connect(url = 'http://localhost:5000') {
    if (this.socket?.connected) {
      console.log('WebSocket already connected');
      return;
    }

    this.socket = io(url, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: Infinity
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.listeners.connect.forEach(cb => cb());
      
      // Subscribe to metrics and incidents
      this.socket.emit('subscribe_metrics');
      this.socket.emit('subscribe_incidents');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.listeners.disconnect.forEach(cb => cb());
    });

    this.socket.on('metric_update', (data) => {
      this.listeners.metrics.forEach(cb => cb(data));
    });

    this.socket.on('incident_created', (data) => {
      this.listeners.incidents.forEach(cb => cb(data));
    });

    this.socket.on('health_update', (data) => {
      this.listeners.health.forEach(cb => cb(data));
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
    });

    return this.socket;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  onMetrics(callback) {
    this.listeners.metrics.push(callback);
    return () => {
      this.listeners.metrics = this.listeners.metrics.filter(cb => cb !== callback);
    };
  }

  onIncidents(callback) {
    this.listeners.incidents.push(callback);
    return () => {
      this.listeners.incidents = this.listeners.incidents.filter(cb => cb !== callback);
    };
  }

  onHealth(callback) {
    this.listeners.health.push(callback);
    return () => {
      this.listeners.health = this.listeners.health.filter(cb => cb !== callback);
    };
  }

  onConnect(callback) {
    this.listeners.connect.push(callback);
    return () => {
      this.listeners.connect = this.listeners.connect.filter(cb => cb !== callback);
    };
  }

  onDisconnect(callback) {
    this.listeners.disconnect.push(callback);
    return () => {
      this.listeners.disconnect = this.listeners.disconnect.filter(cb => cb !== callback);
    };
  }

  isConnected() {
    return this.socket?.connected || false;
  }
}

// Export singleton instance
const websocketService = new WebSocketService();
export default websocketService;
