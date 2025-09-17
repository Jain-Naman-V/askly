import { io } from 'socket.io-client';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.messageHandlers = new Map();
    this.connectionHandlers = [];
  }

  connect() {
    try {
      this.socket = io(WS_URL, {
        transports: ['websocket'],
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
      });

      this.setupEventHandlers();
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }

  setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.notifyConnectionHandlers('connected');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
      this.notifyConnectionHandlers('disconnected');
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.isConnected = false;
      this.notifyConnectionHandlers('error');
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log(`WebSocket reconnected after ${attemptNumber} attempts`);
      this.isConnected = true;
      this.notifyConnectionHandlers('reconnected');
    });

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
      this.isConnected = false;
      this.notifyConnectionHandlers('failed');
    });

    // Handle incoming messages
    this.socket.onAny((eventName, data) => {
      this.handleMessage(eventName, data);
    });
  }

  handleMessage(type, data) {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in message handler for ${type}:`, error);
        }
      });
    }
  }

  notifyConnectionHandlers(status) {
    this.connectionHandlers.forEach(handler => {
      try {
        handler(status);
      } catch (error) {
        console.error('Error in connection handler:', error);
      }
    });
  }

  // Send message
  send(type, data) {
    if (this.isConnected && this.socket) {
      this.socket.emit(type, data);
    } else {
      console.warn('WebSocket not connected, message not sent:', { type, data });
    }
  }

  // Subscribe to message type
  subscribe(type, handler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type).push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index !== -1) {
          handlers.splice(index, 1);
        }
      }
    };
  }

  // Subscribe to connection status changes
  onConnectionChange(handler) {
    this.connectionHandlers.push(handler);

    // Return unsubscribe function
    return () => {
      const index = this.connectionHandlers.indexOf(handler);
      if (index !== -1) {
        this.connectionHandlers.splice(index, 1);
      }
    };
  }

  // Search methods
  streamSearch(query) {
    this.send('search', { query, type: 'search' });
  }

  // AI Chat methods
  sendChatMessage(message) {
    this.send('chat', { message, type: 'chat' });
  }

  // Disconnect
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  // Get connection status
  getConnectionStatus() {
    return {
      isConnected: this.isConnected,
      socket: this.socket,
    };
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;