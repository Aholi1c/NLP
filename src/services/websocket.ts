import { WebSocketMessage } from '../types';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnected = false;
  private clientId: string;
  private messageHandlers: Map<string, (data: any) => void> = new Map();
  private connectionCallbacks: ((connected: boolean) => void)[] = [];

  constructor(clientId?: string) {
    this.clientId = clientId || this.generateClientId();
  }

  private generateClientId(): string {
    return `client_${Math.random().toString(36).substr(2, 9)}_${Date.now()}`;
  }

  connect(url?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = url || `${this.getWebSocketUrl()}/ws/${this.clientId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.notifyConnectionCallbacks(true);
          console.log('WebSocket connected');
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.notifyConnectionCallbacks(false);
          console.log('WebSocket disconnected');
          this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.notifyConnectionCallbacks(false);
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.REACT_APP_WS_URL || window.location.host;
    return `${protocol}//${host}`;
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect().catch(() => {
          // Continue trying to reconnect
        });
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1));
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message.data);
    } else {
      console.warn(`No handler registered for message type: ${message.type}`);
    }
  }

  // Send a message through WebSocket
  send(type: string, data: any): void {
    if (this.ws && this.isConnected) {
      const message: WebSocketMessage = {
        type,
        data,
        timestamp: new Date().toISOString(),
      };
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  // Register a message handler
  onMessage(type: string, handler: (data: any) => void): void {
    this.messageHandlers.set(type, handler);
  }

  // Remove a message handler
  offMessage(type: string): void {
    this.messageHandlers.delete(type);
  }

  // Register connection callback
  onConnection(callback: (connected: boolean) => void): void {
    this.connectionCallbacks.push(callback);
  }

  // Remove connection callback
  offConnection(callback: (connected: boolean) => void): void {
    const index = this.connectionCallbacks.indexOf(callback);
    if (index > -1) {
      this.connectionCallbacks.splice(index, 1);
    }
  }

  private notifyConnectionCallbacks(connected: boolean): void {
    this.connectionCallbacks.forEach(callback => callback(connected));
  }

  // Check if connected
  connected(): boolean {
    return this.isConnected;
  }

  // Get client ID
  getClientId(): string {
    return this.clientId;
  }

  // Send a chat message
  sendChatMessage(message: string, conversationId?: number, model = 'gpt-3.5-turbo'): void {
    this.send('chat', {
      message,
      conversation_id: conversationId,
      model,
    });
  }

  // Send audio for transcription
  sendAudioForTranscription(audioUrl: string, language?: string): void {
    this.send('transcribe', {
      audio_url: audioUrl,
      language,
    });
  }

  // Send image for analysis
  sendImageForAnalysis(imageUrl: string, prompt?: string): void {
    this.send('analyze_image', {
      image_url: imageUrl,
      prompt,
    });
  }

  // Send ping to keep connection alive
  ping(): void {
    this.send('ping', {});
  }

  // Start periodic ping
  startPeriodicPing(interval = 30000): void {
    setInterval(() => {
      if (this.isConnected) {
        this.ping();
      }
    }, interval);
  }
}

// Create a global WebSocket service instance
export const websocketService = new WebSocketService();