// useWebSocket.js
import { useEffect, useRef, useState } from 'react';

export const useWebSocket = (jobId) => {
  console.log('WebSocket jobId:', jobId, typeof jobId);
  
  // Add safety check
  if (!jobId || typeof jobId !== 'string') {
    console.error('Invalid jobId for WebSocket:', jobId);
    return { jobUpdate: null, isConnected: false };
  }

  const [jobUpdate, setJobUpdate] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const maxReconnectAttempts = 5;
  const reconnectAttempts = useRef(0);

  const connectWebSocket = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    console.log(`[WebSocket] Attempting connection for job: ${jobId}, attempt: ${reconnectAttempts.current + 1}`);
    
    const ws = new WebSocket(`ws://localhost:8000/ws/jobs/${jobId}`);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`[WebSocket] Connection established for job: ${jobId}`);
      setIsConnected(true);
      reconnectAttempts.current = 0; // Reset on successful connection
    };

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      console.log(`[WebSocket] Update received for job ${jobId}:`, update);
      setJobUpdate(update);
    };

    ws.onerror = (error) => {
      console.log(`[WebSocket] Error for job ${jobId}:`, error);
      setIsConnected(false);
    };

    ws.onclose = (event) => {
      console.log(`[WebSocket] Connection closed for job ${jobId}:`, event.code);
      setIsConnected(false);
      
      // Only retry if it wasn't a normal closure and we haven't exceeded max attempts
      if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 5000); // Exponential backoff, max 5s
        console.log(`[WebSocket] Reconnecting in ${delay}ms...`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++;
          connectWebSocket();
        }, delay);
      }
    };
  };

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000); // Normal closure
      }
    };
  }, [jobId]);

  return { jobUpdate, isConnected };
};