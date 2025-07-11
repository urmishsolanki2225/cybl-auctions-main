// useWebSocket.ts

import { useEffect, useRef } from 'react';

interface MessageEvent {
  type: string;
  data?: any;
}

interface WebSocketOptions {
  onMessage: (message: MessageEvent) => void;
  lotId: string | number;
}

export default function useWebSocket({ lotId, onMessage }: WebSocketOptions) {
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let isMounted = true;

    const ws = new WebSocket(`ws://auction.cyblance.com:8000/ws/lot/${lotId}/`);
    socketRef.current = ws;

    ws.onopen = () => {
      if (!isMounted) return;
      console.log('✅ WebSocket connected');
    };

    ws.onmessage = (event) => {
      if (!isMounted) return;
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error('❌ Invalid JSON:', event.data);
      }
    };

    ws.onerror = (err) => {
      if (!isMounted) return;
      console.error('❌ WebSocket error:', err);
    };

    ws.onclose = () => {
      if (!isMounted) return;
      console.warn('🔌 WebSocket disconnected');
    };

    return () => {
      isMounted = false;
      ws.close();
    };
  }, [lotId]);

  // ✅ Return a function that fetches the latest socket
  return {
    getSocket: () => socketRef.current,
  };
}
