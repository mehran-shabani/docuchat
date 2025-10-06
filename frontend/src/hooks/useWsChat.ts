import { useState, useCallback, useEffect, useRef } from 'react';
import type { Message, WebSocketMessage } from '@/types';

const WS_ENDPOINT = process.env.NEXT_PUBLIC_WS_ENDPOINT || 'ws://localhost:8000/ws/chat';
const WS_ENABLED = process.env.NEXT_PUBLIC_ENABLE_WS === 'true';

export const useWsChat = (fallbackToHttp?: () => void) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!WS_ENABLED) {
      console.log('WebSocket غیرفعال است، از HTTP استفاده می‌شود');
      return;
    }

    try {
      shouldReconnectRef.current = true;
      const ws = new WebSocket(WS_ENDPOINT);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket متصل شد');
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);

          if (data.type === 'token') {
            // Update streaming message
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.streaming) {
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    content: lastMessage.content + data.content,
                  },
                ];
              }
              return prev;
            });
          } else if (data.type === 'end') {
            // Mark message as complete
            setMessages(prev => {
              const lastMessage = prev[prev.length - 1];
              if (lastMessage && lastMessage.streaming) {
                return [
                  ...prev.slice(0, -1),
                  {
                    ...lastMessage,
                    streaming: false,
                  },
                ];
              }
              return prev;
            });
            setIsLoading(false);
          } else if (data.type === 'error') {
            setError(data.error);
            setIsLoading(false);
          }
        } catch (err) {
          console.error('خطا در پردازش پیام WebSocket:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('خطای WebSocket:', event);
        setError('خطا در اتصال WebSocket');
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket قطع شد');
        setIsConnected(false);
        
        // Auto reconnect only if not manually disconnected
        if (shouldReconnectRef.current) {
          reconnectTimeoutRef.current = setTimeout(() => {
            if (WS_ENABLED) {
              connect();
            }
          }, 3000);
        }
      };
    } catch (err) {
      console.error('خطا در ایجاد WebSocket:', err);
      setError('خطا در ایجاد اتصال');
      
      // Fallback to HTTP if WebSocket fails
      if (fallbackToHttp) {
        fallbackToHttp();
      }
    }
  }, [fallbackToHttp]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback(async (text: string, model?: string) => {
    if (!text.trim()) return;

    if (!isConnected || !wsRef.current) {
      setError('اتصال WebSocket برقرار نیست');
      if (fallbackToHttp) {
        fallbackToHttp();
      }
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    const streamingMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      streaming: true,
    };

    setMessages(prev => [...prev, userMessage, streamingMessage]);
    setIsLoading(true);
    setError(null);

    try {
      wsRef.current.send(JSON.stringify({
        message: text,
        model: model || process.env.NEXT_PUBLIC_OPENAI_MODEL || 'gpt-3.5-turbo',
      }));
    } catch (err) {
      setError('خطا در ارسال پیام');
      setIsLoading(false);
      if (fallbackToHttp) {
        fallbackToHttp();
      }
    }
  }, [isConnected, fallbackToHttp]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  useEffect(() => {
    if (WS_ENABLED) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    messages,
    isConnected,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    connect,
    disconnect,
  };
};
