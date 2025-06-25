// WatchlistPage.tsx
import React, { useEffect, useState } from 'react';
import { protectedApi } from '../api/apiUtils';
import '../styles/WatchlistPage.css';
import { useWatchlist } from '../context/WatchlistContext';
import BASE_URL from "../api/endpoints";
import { useNavigate } from 'react-router-dom';
import { FaTrash, FaGavel } from 'react-icons/fa';

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
  current_bid?: number;
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
        setLoading(true);
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
  }, [watchlist]);

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

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
      <div className="watchlist-grid">
        {items.map((item) => (
          <div key={item.id} className="watchlist-card">
            <div className="card-image">
              {item.inventory_details.image_url ? (
                <img 
                  src={`${BASE_URL}/media/${item.inventory_details.image_url}`} 
                  alt={item.inventory_details.title}
                  loading="lazy"
                />
              ) : (
                <div className="image-placeholder">No Image</div>
              )}
            </div>
            
            <div className="card-content">
              <h3>{item.inventory_details.title}</h3>
              
              <div className="price-info">
                <span className="label">Current Bid:</span>
                <span className="value">${item.current_bid || item.inventory_details.starting_bid}</span>
              </div>
              
              <div className="time-info">
                <span className="label">Ends:</span>
                <span className="value">{formatDate(item.inventory_details.lot_end_time)}</span>
              </div>
              
              <div className="card-actions">
                <button
                  onClick={() => removeFromWatchlist(item.inventory)}
                  className="remove-btn"
                >
                  <FaTrash /> Remove
                </button>
                <button 
                  onClick={() => navigate(`/lot/${item.inventory_details.id}`)}
                  className="bid-btn"
                >
                  <FaGavel /> Place Bid
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WatchlistPage;