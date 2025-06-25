// WatchlistPage.tsx
import React, { useEffect, useState } from 'react';
import { protectedApi } from '../api/apiUtils';
import '../styles/WatchlistPage.css';
import { useWatchlist } from '../context/WatchlistContext';
import BASE_URL from "../api/endpoints";
import { useNavigate } from 'react-router-dom';

interface WatchlistItem {
  id: number;
  inventory: number;
  inventory_details: {
    id: number;
    title: string;
    image_url: string | null;
    starting_bid: number;
    lot_end_time: string;
    status: string;
  };
  created_at: string;
}

const WatchlistPage: React.FC = () => {
  const navigate = useNavigate();

  const { watchlist, removeFromWatchlist } = useWatchlist();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWatchlistItems = async () => {
      try {
        const data = await protectedApi.getWatchlist();
        setItems(data);
      } catch (err) {
        setError('Failed to load watchlist');
        console.error('Error fetching watchlist:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchWatchlistItems();
  }, [watchlist]); // Refresh when watchlist changes

  if (loading) {
    return <div className="loading-container">Loading your watchlist...</div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (items.length === 0) {
    return <div className="empty-watchlist">Your watchlist is empty</div>;
  }

  return (
    <div className="watchlist-container">
      <h1>Your Watchlist</h1>
      <div className="watchlist-items">
        {items.map((item) => (
          <div key={item.id} className="watchlist-item">
            <div className="item-image">
              {item.inventory_details.image_url ? (
                <img 
                  src={BASE_URL + '/media/' +item.inventory_details.image_url} 
                  alt={item.inventory_details.title}
                />
              ) : (
                <div className="image-placeholder">No Image</div>
              )}
            </div>
            <div className="item-details">
              <h3>{item.inventory_details.title}</h3>
              <p>Starting Bid: ${item.inventory_details.starting_bid}</p>
              <p>Ends: {new Date(item.inventory_details.lot_end_time).toLocaleString()}</p>
              <p>Curreny bid: {item.current_bid}</p>
            </div>
            <button
              onClick={() => removeFromWatchlist(item.inventory)}
              className="remove-button"
            >
              Remove
            </button>
            <button  onClick={() => navigate(`/lot/${item.inventory_details.id}`)}>Place bid</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WatchlistPage;