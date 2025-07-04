import React from 'react';
import "../styles/ActiveLots.css";
import BASE_URL from "../api/endpoints";
import WatchlistButton from './WatchlistButton';
import { useNavigate } from "react-router-dom";


const ActiveLots = ({ lots }) => {
  const navigate = useNavigate();
  // Function to format time remaining
  const formatTimeRemaining = (timeString) => {
    if (!timeString) return "Time expired";
    
    // Extract days and hours from the time string
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

  // Function to get image URL or placeholder
  const getImageUrl = (mediaItem) => {
    if (mediaItem && mediaItem.path) {
      // Assuming you have a base URL for images
      return `${BASE_URL}/media/${mediaItem.path}`;
    }
    return null;
  };

  // Function to determine if reserve is met
  const isReserveMet = (currentBid, reservePrice) => {
    return parseFloat(currentBid) >= parseFloat(reservePrice);
  };

  return (
    <div className="auctions-container">
      <h1 className="auctions-title">Auctions</h1>    
      {/* Lots grid */}
      <div className="lots-grid">
        {lots?.map((lot, index) => (
          <div key={lot.id || index} className="lot-cards">
            {/* Car Image Section */}
            <div className="car-image-container">
            <div className="watchlist-button-container">
            <WatchlistButton
                inventoryId={lot?.id}
                size="small"
                //onWatchlistChange={handleWatchlistChange}
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
              
              {/* Featured badge */}
              {lot.auction_details?.is_featured && (
                <div className="featured-badge">Featured</div>
              )}
              
              {/* Condition badge */}
              <div className={`condition-badge ${lot.condition === 'new' ? 'condition-new' : 'condition-used'}`}>
                {lot.condition}
              </div>
              {/* Timer overlay */}
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

            {/* Card Content */}
            <div className="card-content">
              <h2 className="car-title">{lot.title}</h2>
              
              {/* Car details */}
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

              {/* Bid section */}
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