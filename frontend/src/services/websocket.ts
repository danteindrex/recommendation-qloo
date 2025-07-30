import { toast } from 'react-hot-toast'

export interface WebSocketMessage {
  type: string
  data?: any
  timestamp?: string
  user_id?: string
  message?: string
}

export type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectInterval: number = 5000
  private reconnectTimer: NodeJS.Timeout | null = null
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map()
  private userId: string | null = null
  private endpoint: string = ''
  private isReconnecting: boolean = false

  connect(endpoint: string, userId: string) {
    this.userId = userId
    this.endpoint = endpoint
    
    const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/api/ws/${endpoint}/${userId}`
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log(`WebSocket connected to ${endpoint}`)
        this.isReconnecting = false
        
        // Clear reconnect timer
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer)
          this.reconnectTimer = null
        }
        
        // Emit connection event
        this.emit('connection', { status: 'connected' })
      }
      
      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('WebSocket message received:', message)
          
          // Handle different message types
          this.handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        toast.error('Real-time connection error')
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.emit('connection', { status: 'disconnected' })
        
        // Attempt reconnection
        if (!this.isReconnecting) {
          this.isReconnecting = true
          this.scheduleReconnect()
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      toast.error('Failed to establish real-time connection')
    }
  }

  private handleMessage(message: WebSocketMessage) {
    // Handle system messages
    switch (message.type) {
      case 'connection_established':
      case 'analytics_connection_established':
        toast.success('Real-time updates connected')
        break
      
      case 'error':
        toast.error(message.message || 'WebSocket error')
        break
      
      case 'heartbeat':
        // Keep-alive, no action needed
        break
      
      case 'cultural_insight':
        this.emit('cultural_insight', message.data)
        break
      
      case 'notification':
        this.handleNotification(message.data)
        break
      
      case 'analytics_update':
        this.emit('analytics_update', message.data)
        break
      
      case 'subscription_confirmed':
        console.log('Subscription confirmed:', message)
        break
      
      default:
        // Emit to specific handlers
        this.emit(message.type, message.data || message)
    }
  }

  private handleNotification(notification: any) {
    // Show toast notification
    const { title, message, type = 'info' } = notification
    
    switch (type) {
      case 'success':
        toast.success(message || title)
        break
      case 'error':
        toast.error(message || title)
        break
      case 'warning':
        toast(message || title, { icon: '⚠️' })
        break
      default:
        toast(message || title)
    }
    
    // Also emit for components that want to handle notifications
    this.emit('notification', notification)
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
    }
    
    console.log(`Scheduling reconnection in ${this.reconnectInterval}ms`)
    
    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting to reconnect...')
      if (this.userId && this.endpoint) {
        this.connect(this.endpoint, this.userId)
      }
    }, this.reconnectInterval)
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.messageHandlers.clear()
    this.isReconnecting = false
  }

  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket is not connected')
      toast.error('Real-time connection not available')
    }
  }

  // Subscribe to WebSocket updates
  subscribe(subscription_type: string = 'all') {
    this.send({
      type: 'subscribe',
      subscription_type
    })
  }

  // Send ping to keep connection alive
  ping() {
    this.send({ type: 'ping' })
  }

  // Event emitter methods
  on(event: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(event)) {
      this.messageHandlers.set(event, new Set())
    }
    this.messageHandlers.get(event)!.add(handler)
  }

  off(event: string, handler: MessageHandler) {
    const handlers = this.messageHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
      if (handlers.size === 0) {
        this.messageHandlers.delete(event)
      }
    }
  }

  private emit(event: string, data: any) {
    const handlers = this.messageHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error)
        }
      })
    }
  }

  // Check if connected
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// Create singleton instances for different WebSocket endpoints
export const culturalWebSocket = new WebSocketService()
export const analyticsWebSocket = new WebSocketService()

// Helper hook for using WebSocket in React components
import { useEffect, useCallback } from 'react'

export function useWebSocket(
  service: WebSocketService,
  endpoint: string,
  userId: string | null,
  handlers: Record<string, MessageHandler> = {}
) {
  useEffect(() => {
    if (!userId) return

    // Connect WebSocket
    service.connect(endpoint, userId)

    // Register handlers
    Object.entries(handlers).forEach(([event, handler]) => {
      service.on(event, handler)
    })

    // Keep connection alive with periodic pings
    const pingInterval = setInterval(() => {
      if (service.isConnected()) {
        service.ping()
      }
    }, 30000) // Ping every 30 seconds

    // Cleanup
    return () => {
      clearInterval(pingInterval)
      
      // Unregister handlers
      Object.entries(handlers).forEach(([event, handler]) => {
        service.off(event, handler)
      })
      
      // Disconnect if no other handlers
      if (service['messageHandlers'].size === 0) {
        service.disconnect()
      }
    }
  }, [service, endpoint, userId])

  const send = useCallback((message: any) => {
    service.send(message)
  }, [service])

  const subscribe = useCallback((subscription_type?: string) => {
    service.subscribe(subscription_type)
  }, [service])

  return {
    send,
    subscribe,
    isConnected: service.isConnected()
  }
}