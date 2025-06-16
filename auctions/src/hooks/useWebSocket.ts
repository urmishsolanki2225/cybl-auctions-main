// hooks/useWebSocket.js
import { useEffect, useRef, useState, useCallback } from 'react';

const useWebSocket = (lotId, token) => {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [lastMessage, setLastMessage] = useState(null);
  const [bidHistory, setBidHistory] = useState([]);
  const [lotStatus, setLotStatus] = useState(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!lotId || !token) return;

    try {
      
     
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${protocol}://192.168.201.35:8000/ws/lot/${lotId}/`;
      const newSocket = new WebSocket(wsUrl);
      
      // Add authorization header
      newSocket.onopen = () => {
        setConnectionStatus('Connected');
        reconnectAttemptsRef.current = 0;
        console.log('WebSocket connected');
        
        // Send token for authentication (if your consumer supports it)
        newSocket.send(JSON.stringify({
          type: 'auth',
          token: token
        }));
      };

      newSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        
        switch (data.type) {
          case 'bid_placed':
            setBidHistory(prev => [data.data, ...prev]);
            setLotStatus(prev => ({
              ...prev,
              current_bid: data.data.amount,
              next_required_bid: data.data.next_required_bid,
              high_bidder: data.data.bidder,
              reserve_met: data.data.reserve_met
            }));
            break;
            
          case 'reserve_met':
            // Show notification that reserve is met
            break;
            
          case 'lot_status':
            setLotStatus(data.data);
            break;
            
          case 'error':
            console.error('WebSocket error:', data.message);
            break;
        }
      };

      newSocket.onclose = (event) => {
        setConnectionStatus('Disconnected');
        setSocket(null);
        
        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const timeout = Math.pow(2, reconnectAttemptsRef.current) * 1000; // Exponential backoff
          
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`Attempting to reconnect... (${reconnectAttemptsRef.current}/${maxReconnectAttempts})`);
            connect();
          }, timeout);
        }
      };

      newSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('Error');
      };

      setSocket(newSocket);
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setConnectionStatus('Error');
    }
  }, [lotId, token]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (socket) {
      socket.close();
      setSocket(null);
    }
    
    setConnectionStatus('Disconnected');
  }, [socket]);

  const sendMessage = useCallback((message) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, [socket]);

  const placeBid = useCallback((bidAmount) => {
    sendMessage({
      type: 'place_bid',
      bid_amount: bidAmount
    });
  }, [sendMessage]);

  const getStatus = useCallback(() => {
    sendMessage({
      type: 'get_status'
    });
  }, [sendMessage]);

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    socket,
    connectionStatus,
    lastMessage,
    bidHistory,
    lotStatus,
    placeBid,
    getStatus,
    sendMessage,
    connect,
    disconnect
  };
};

export default useWebSocket;