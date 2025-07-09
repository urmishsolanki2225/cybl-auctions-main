import { useEffect, useState } from "react";
import "../styles/ActiveLots.css";
import BASE_URL from "../api/endpoints";
import WatchlistButton from './WatchlistButton';
import { useNavigate } from "react-router-dom";
import { publicApi } from "../api/apiUtils";

const ActiveLots = () => {
  const navigate = useNavigate();
  const [Activelot, setActivelot] = useState<[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAuctions = async () => {
      try {
        setLoading(true);        
        const lots = await publicApi.getActivelots();
        setActivelot(lots);
      } catch (err) {
        console.error("Failed to load bidding history", err);
        setError("Failed to load bidding history");
        setLoading(false);
      } finally {
        setLoading(false);
      }
    };

    fetchAuctions();
  }, []);

  const formatTimeRemaining = (timeString) => {
    if (!timeString) return "Time expired";
    
    const match = timeString.match(/(\d+)\s*days?,\s*(\d+):(\d+):(\d+)/);
    if (match) {
      const [, days, hours, minutes] = match;
      if (parseInt(days) > 0) {
        return `${days}d ${hours}h`;
      }
      return `${hours}:${minutes}`;
    }
    return timeString;
  };

  const getImageUrl = (mediaItem) => {
    if (mediaItem && mediaItem.path) {
      return `${BASE_URL}/media/${mediaItem.path}`;
    }
    return null;
  };

  const isReserveMet = (currentBid, reservePrice) => {
    return parseFloat(currentBid) >= parseFloat(reservePrice);
  };

 return loading ? (
    <div className="loading-state">Loading...</div>
  ) : (
    <div className="auctions-container">
      <h1 className="auctions-title">Running lots</h1>    
      <div className="lots-grid">
        {Activelot?.map((lot, index) => (
          <div key={lot.id || index} className="lot-cards">
            <div className="car-image-container">
            <div className="watchlist-button-container">
            <WatchlistButton
                inventoryId={lot?.id}
                size="small"
            />
            </div>
              {getImageUrl(lot.media_items) ? (
                <img 
                  src={getImageUrl(lot.media_items)} 
                  alt={lot.title}
                  className="car-image"
                />
              ) : (
                <div className="no-image-placeholder">
                  🚗
                </div>
              )}
              {lot.auction_details?.is_featured && (
                <div className="featured-badge">Featured</div>
              )}              
              <div className={`condition-badge ${lot.condition === 'new' ? 'condition-new' : 'condition-used'}`}>
                {lot.condition}
              </div>
              <div className="timer-overlay">
                <div className="timer-info">
                  <div className="timer-icon">⏱</div>
                  <div className="timer-text">{formatTimeRemaining(lot.time_remaining)}</div>
                </div>
                <div className="bid-info">
                  <div className="bid-label">Bid</div>
                  <div className="bid-amount">${parseFloat(lot.next_required_bid).toLocaleString()}</div>
                </div>
              </div>
            </div>
            <div className="card-content">
              <h2 className="car-title">{lot.title}</h2>              
              <div className="car-details">
                {/* <div className="car-detail">
                  <span>Category:</span>
                  <span>{lot.category_details?.category_name}</span>
                </div> */}
                {/* <div className="car-detail">
                  <span>Reserve:</span>
                  <span>${parseFloat(lot.reserve_price).toLocaleString()}</span>
                </div> */}
              </div>
              
              {/* <div className="car-spec">
                {lot.description?.replace(/<[^>]*>/g, '') || 'No description available'}
              </div> */}
              
              <div className="car-location">
                {lot.auction_details?.name}
              </div>
              <div className="bid-section">
                <div className="current-bid">
                  <div className="current-bid-label">Current Bid</div>
                  <div className="current-bid-amount">${parseFloat(lot.current_bid).toLocaleString()}</div>
                </div>
                <button className="place-bid-btn" onClick={()=> navigate(`/lot/${lot.id}`)}>
                  Place Bid
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ActiveLots;