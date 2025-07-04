import React, { useState, useEffect } from 'react';
import BASE_URL from "../api/endpoints";
import "../styles/nexttoclose.css";

const NextToClose = ({ auctions }) => {
  const [timeLeft, setTimeLeft] = useState({});

  console.log(auctions);

  // Function to calculate time remaining
  const calculateTimeLeft = (endDate) => {
    const difference = new Date(endDate) - new Date();
    
    if (difference > 0) {
      return {
        days: Math.floor(difference / (1000 * 60 * 60 * 24)),
        hours: Math.floor((difference / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((difference / 1000 / 60) % 60),
        seconds: Math.floor((difference / 1000) % 60)
      };
    }
    return null;
  };

  // Update countdown every second
  useEffect(() => {
    const timer = setInterval(() => {
      const newTimeLeft = {};
      auctions?.forEach(auction => {
        newTimeLeft[auction.id] = calculateTimeLeft(auction.end_date);
      });
      setTimeLeft(newTimeLeft);
    }, 1000);

    return () => clearInterval(timer);
  }, [auctions]);

  // Function to get image URL or placeholder
  const getImageUrl = (auction) => {
    if (auction?.location_details?.company_logo) {
      return `${BASE_URL}${auction.location_details.company_logo}`;
    }
    return 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop&crop=center';
  };

  // Function to format countdown
  const formatCountdown = (time) => {
    if (!time) return "Auction Ended";
    
    if (time.days > 0) {
      return `${time.days}d ${time.hours}h ${time.minutes}m`;
    } else if (time.hours > 0) {
      return `${time.hours}h ${time.minutes}m ${time.seconds}s`;
    } else {
      return `${time.minutes}m ${time.seconds}s`;
    }
  };

  // Function to get status class
  const getStatusClass = (time) => {
    if (!time) return "status-ended";
    if (time.days === 0 && time.hours < 1) return "status-urgent";
    if (time.days === 0 && time.hours < 24) return "status-warning";
    return "status-active";
  };

  return (
    <div className="next-to-close-container">
      <h1 className="auctions-title">Closing soon</h1>
      
      <div className="auctions-grid">
        {auctions?.map((auction, index) => (
          <div key={auction.id || index} className="auction-cards">
            {/* Card Image */}
            <div className="card-image" style={{ position: "relative" }}>
              <img 
                src={getImageUrl(auction)} 
                alt={auction.name}
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400&h=300&fit=crop&crop=center';
                }}
              />
              <div className="image-overlay"></div>
              
              {/* Lot Count Badge */}
             <div className="lot-count-badge">
                {auction.lot_count} Lots
              </div>
              
              {/* Featured Badge */}
              {auction.is_featured && (
                <div className="featured-badge">
                  Featured
                </div>
              )}             
              
            </div>

            {/* Card Content */}
            <div className="card-content">
              {/* Auction Name */}
              <h2 className="auction-name">{auction.name}</h2>
              
              {/* Company Section */}
              <div className="company-section">
                <div className="company-name">
                  {auction.location_details?.name || 'Company Name'}
                </div>
                <div className="company-address">
                  <span className="address-icon"></span>
                  {auction.location_details?.address && (
                    <>
                      {auction.location_details.address}<br />
                      {auction.location_details.city}, {auction.location_details.state} {auction.location_details.zipcode}<br />
                      {auction.location_details.country}
                    </>
                  )}
                  {auction.location_details?.phone_no && (
                    <div>{auction.location_details.phone_no}</div>
                  )}
                </div>
              </div>

              {/* <div className={`countdown-overlay ${getStatusClass(timeLeft[auction.id])}`}>
                <span className="countdown-icon">Ends in:</span>
                <span className="countdown-time">
                  {formatCountdown(timeLeft[auction.id])}
                </span>
              </div> */}
           
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {(!auctions || auctions.length === 0) && (
        <div className="empty-state">
          <h3>No Auctions Available</h3>
          <p>There are currently no auctions ending soon.</p>
        </div>
      )}
    </div>
  );
};

export default NextToClose;