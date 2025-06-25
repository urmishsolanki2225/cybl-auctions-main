// contexts/WatchlistContext.tsx
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { protectedApi } from '../api/apiUtils';
import { toast } from 'react-toastify';

interface WatchlistContextType {
  watchlist: number[]; // Array of inventory IDs
  loading: boolean;
  isInitialized: boolean; // NEW: Track if initial load is complete
  addToWatchlist: (inventoryId: number) => Promise<void>;
  removeFromWatchlist: (inventoryId: number) => Promise<void>;
  refreshWatchlist: () => Promise<void>;
}

const WatchlistContext = createContext<WatchlistContextType | undefined>(undefined);

export const WatchlistProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);

  const refreshWatchlist = useCallback(async () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      setWatchlist([]);
      setIsInitialized(true);
      return;
    }

    try {
      setLoading(true);
      const response = await protectedApi.getWatchlist();
      
      // Handle both paginated and non-paginated responses
      const inventoryIds = response.map((item: any) => item.inventory_details.id);
      
      setWatchlist(inventoryIds);
      console.log("Watchlist loaded:", inventoryIds); // Debug log
    } catch (err) {
      console.error("Failed to fetch watchlist", err);
      setWatchlist([]); // Reset on error
      
      // Only show error if it's not a 401 (unauthorized)
      if (err.response?.status !== 401) {
        toast.error("Failed to load watchlist");
      }
    } finally {
      setLoading(false);
      setIsInitialized(true);
    }
  }, []);

  const addToWatchlist = async (inventoryId: number) => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      toast.warning("Please login to manage your watchlist");
      return;
    }

    // Optimistically update UI
    setWatchlist(prev => [...prev, inventoryId]);
    
    try {
      await protectedApi.addToWatchlist(inventoryId);
      toast.success("Added to watchlist");
    } catch (err) {
      // Revert optimistic update on error
      setWatchlist(prev => prev.filter(id => id !== inventoryId));
      console.error("Failed to add to watchlist", err);
      
      if (err.response?.status === 400 && err.response?.data?.error?.includes("already in watchlist")) {
        toast.info("Item is already in your watchlist");
        // Refresh to get current state
        refreshWatchlist();
      } else {
        toast.error("Failed to add to watchlist");
      }
      throw err;
    }
  };

  const removeFromWatchlist = async (inventoryId: number) => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      toast.warning("Please login to manage your watchlist");
      return;
    }

    // Optimistically update UI
    const previousWatchlist = watchlist;
    setWatchlist(prev => prev.filter(id => id !== inventoryId));
    
    try {
      await protectedApi.removeFromWatchlist(inventoryId);
      toast.success("Removed from watchlist");
    } catch (err) {
      // Revert optimistic update on error
      setWatchlist(previousWatchlist);
      console.error("Failed to remove from watchlist", err);
      toast.error("Failed to remove from watchlist");
      throw err;
    }
  };

  // Initial load and token change detection
  useEffect(() => {
    refreshWatchlist();
  }, [refreshWatchlist]);

  // Listen for auth token changes (login/logout)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'authToken') {
        refreshWatchlist();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [refreshWatchlist]);

  // Refresh watchlist every 30 seconds to keep it in sync
  useEffect(() => {
    const interval = setInterval(() => {
      if (localStorage.getItem("authToken")) {
        refreshWatchlist();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [refreshWatchlist]);

  return (
    <WatchlistContext.Provider value={{ 
      watchlist, 
      loading, 
      isInitialized,
      addToWatchlist, 
      removeFromWatchlist, 
      refreshWatchlist 
    }}>
      {children}
    </WatchlistContext.Provider>
  );
};

export const useWatchlist = () => {
  const context = useContext(WatchlistContext);
  if (!context) {
    throw new Error('useWatchlist must be used within a WatchlistProvider');
  }
  return context;
};