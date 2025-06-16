import { useNavigate, useParams } from 'react-router-dom';
import { useCallback, useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import useWebSocket from '../hooks/useWebSocket';
import LiveTimer from '../components/LiveTimer';
import './LotDetails.css';
import { publicApi, protectedApi } from '../api/apiUtils';
import BASE_URL from '../api/endpoints';

const LotDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(0);
  const [lot, setLot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bidAmount, setBidAmount] = useState('');
  const [isPlacingBid, setIsPlacingBid] = useState(false);
  const [showBidHistory, setShowBidHistory] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [timerKey, setTimerKey] = useState(0); 
  const [error, setError] = useState(null);

  const token = localStorage.getItem('authToken');
  
  // WebSocket hook for real-time updates
  const {
    connectionStatus,
    lastMessage,
    bidHistory,
    lotStatus,
    placeBid: placeBidWS,
    getStatus
  } = useWebSocket(id, token);

  useEffect(() => {
    const fetchLots = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await publicApi.getLotDetails(id);
        setLot(response || {});
      } catch (err) {
        console.error('Failed to load lot details', err);
        setError(err.message || 'Failed to load lot details');
      } finally {
        setLoading(false);
      }
    };
    fetchLots();
  }, [id, navigate]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage) {
      switch (lastMessage.type) {
        case 'bid_placed':
          const bidData = lastMessage.data;
          
          // Show bid notification
          toast.success(`New bid: ₹${bidData.amount} by ${bidData.bidder}`);
          
          // Update lot data with new bid info
          setLot(prev => ({
            ...prev,
            current_bid: bidData.amount,
            next_required_bid: bidData.next_required_bid,
            high_bidder: bidData.bidder,
            reserve_met: bidData.reserve_met,
            totalBids: (prev.totalBids || 0) + 1,
            // Update lot_end_time if it was extended
            lot_end_time: bidData.lot_end_time || prev.lot_end_time
          }));

          // Clear bid input if this user placed the bid
          if (bidData.bidder_id === JSON.parse(localStorage.getItem('user') || '{}').id) {
            setBidAmount('');
            toast.success('Your bid has been placed successfully!');
          }

          // If timer was extended, show notification and force timer re-render
          if (bidData.timer_extended) {
            toast.info('Timer extended by 5 minutes due to last-minute bid!', {
              autoClose: 5000,
              style: { backgroundColor: '#17a2b8', color: 'white' }
            });
            setTimerKey(prev => prev + 1);
          }
          break;
          
        case 'timer_extended':
          const extensionData = lastMessage.data;
          
          setLot(prev => ({
            ...prev,
            lot_end_time: extensionData.new_end_time
          }));
          
          toast.info(extensionData.message, {
            autoClose: 7000,
            style: { backgroundColor: '#17a2b8', color: 'white' }
          });
          
          setTimerKey(prev => prev + 1);
          break;
          
        case 'reserve_met':
          toast.info(`Reserve price of ₹${lastMessage.data.reserve_price} has been met!`, {
            autoClose: 5000,
            style: { backgroundColor: '#28a745', color: 'white' }
          });
          setLot(prev => ({
            ...prev,
            reserve_met: true
          }));
          break;
          
        case 'lot_status':
          const statusData = lastMessage.data;
          setLot(prev => ({
            ...prev,
            current_bid: statusData.current_bid,
            next_required_bid: statusData.next_required_bid,
            high_bidder: statusData.high_bidder,
            reserve_met: statusData.reserve_met,
            totalBids: statusData.total_bids || prev.totalBids,
            lot_end_time: statusData.lot_end_time || prev.lot_end_time
          }));
          break;
          
        case 'error':
          toast.error(lastMessage.message);
          setIsPlacingBid(false);
          break;
      }
    }
  }, [lastMessage]);

  // Update lot with WebSocket status
  useEffect(() => {
    if (lotStatus) {
      setLot(prev => ({
        ...prev,
        current_bid: lotStatus.current_bid,
        next_required_bid: lotStatus.next_required_bid,
        high_bidder: lotStatus.high_bidder,
        reserve_met: lotStatus.reserve_met,
        totalBids: lotStatus.total_bids || prev.totalBids,
        lot_end_time: lotStatus.lot_end_time || prev.lot_end_time
      }));
    }
  }, [lotStatus]);

  const handlePlaceBid = async () => {
    // Check if user is authenticated
    if (!token) {
      toast.error('Please log in to place a bid');
      return navigate('/login');
    }

    if (!bidAmount || isPlacingBid) return;

    const amount = parseFloat(bidAmount);
    
    // Validate bid amount
    if (isNaN(amount) || amount <= 0) {
      toast.error('Please enter a valid bid amount');
      return;
    }

    if (amount < lot?.next_required_bid) {
      toast.error(`Bid must be at least ₹${lot?.next_required_bid}`);
      return;
    }

    // Check if lot is still active
    if (lot?.status === 'closed' || lot?.status === 'completed') {
      toast.error('This auction has already ended');
      return;
    }

    setIsPlacingBid(true);

    try {
      // First try to place bid via WebSocket for real-time updates
      if (placeBidWS && connectionStatus === 'Connected') {
        placeBidWS(amount);
      } else {
        // Fallback to API call if WebSocket is not available
        const response = await protectedApi.placeBid(parseInt(id), amount);
        
        if (response.success) {
          toast.success('Bid placed successfully!');
          setBidAmount('');
          
          // Update lot data with response
          setLot(prev => ({
            ...prev,
            current_bid: response.current_bid,
            next_required_bid: response.next_required_bid,
            high_bidder: response.high_bidder,
            reserve_met: response.reserve_met,
            totalBids: (prev.totalBids || 0) + 1,
            lot_end_time: response.lot_end_time || prev.lot_end_time
          }));

          // Show timer extension notification if applicable
          if (response.timer_extended) {
            toast.info('Timer extended by 5 minutes due to last-minute bid!', {
              autoClose: 5000,
              style: { backgroundColor: '#17a2b8', color: 'white' }
            });
            setTimerKey(prev => prev + 1);
          }
        }
      }
    } catch (error) {
      console.error('Error placing bid:', error);
      
      // Handle specific error messages
      if (error.status === 400) {
        toast.error(error.message || 'Invalid bid amount');
      } else if (error.status === 401) {
        toast.error('Your session has expired. Please log in again.');
        localStorage.removeItem('authToken');
        navigate('/login');
      } else if (error.status === 403) {
        toast.error('You are not authorized to bid on this lot');
      } else if (error.status === 409) {
        toast.error('Someone else placed a higher bid. Please try again.');
        // Refresh lot data
        try {
          const response = await publicApi.getLotDetails(id);
          setLot(response);
        } catch (refreshError) {
          console.error('Error refreshing lot data:', refreshError);
        }
      } else {
        toast.error(error.message || 'Failed to place bid. Please try again.');
      }
    } finally {
      setIsPlacingBid(false);
    }
  };

  const handleQuickBid = () => {
    if (lot?.next_required_bid) {
      setBidAmount(lot.next_required_bid.toString());
    }
  };

  const toggleBidHistory = async () => {
    if (!showBidHistory && historyData.length === 0) {
      try {
        const history = await protectedApi.getLotBids(parseInt(id));
        setHistoryData(history.bids || []);
      } catch (error) {
        console.error('Error fetching bid history:', error);
        toast.error('Failed to load bid history');
      }
    }
    setShowBidHistory(!showBidHistory);
  };

  const formatBidAmount = (value) => {
    // Remove non-numeric characters except decimal point
    const numericValue = value.replace(/[^\d.]/g, '');
    
    // Ensure only one decimal point
    const parts = numericValue.split('.');
    if (parts.length > 2) {
      return parts[0] + '.' + parts.slice(1).join('');
    }
    
    return numericValue;
  };

  const handleBidAmountChange = (e) => {
    const formatted = formatBidAmount(e.target.value);
    setBidAmount(formatted);
  };

  // Check if auction has ended
  const isAuctionEnded = () => {
    if (!lot?.lot_end_time) return false;
    return new Date(lot.lot_end_time) < new Date();
  };

  if (loading) {
    return (
      <div className="lot-details-page">
        <div className="container">
          <div className="loading-spinner">
            <div className="spinner-border" role="status">
              <span className="sr-only">Loading...</span>
            </div>
            <p>Loading lot details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !lot) {
    return (
      <div className="lot-details-page">
        <div className="container">
          <div className="error-message">
            <h3>Error Loading Lot</h3>
            <p>{error || 'Lot not found'}</p>
            <button onClick={() => navigate('/auctions')} className="btn btn-primary">
              Back to Auctions
            </button>
          </div>
        </div>
      </div>
    );
  }

  const auctionEnded = isAuctionEnded();

  return (
    <div className="lot-details-page">
      <div className="container">
        <div className="lot-header">
          <div className="breadcrumb">
            <span>Auctions</span> --- <span>{lot?.category?.name || 'Category'}</span> --- <span>{lot?.title}</span>
          </div>
          <div className="lot-number">Lot #{lot?.lot_number || lot?.id}</div>
        </div>

        <div className="lot-main">
          <div className="lot-left">
            <div className="image-gallery">
              <div className="main-image">
                {lot?.media_items && lot.media_items.length > 0 ? (
                  <img 
                    src={BASE_URL + `/media/` + lot.media_items[selectedImage]?.path?.replace(/\\/g, '/')} 
                    alt={lot?.title}
                    onError={(e) => {
                      e.target.src = '/placeholder-image.jpg'; // Add a placeholder image
                    }}
                  />
                ) : (
                  <div className="no-image">No Image Available</div>
                )}
              </div>
              {lot?.media_items && lot.media_items.length > 1 && (
                <div className="thumbnail-list">
                  {lot.media_items.map((image, index) => (
                    <div 
                      key={index} 
                      className={`thumbnail ${selectedImage === index ? 'active' : ''}`}
                      onClick={() => setSelectedImage(index)}
                    >
                      <img 
                        src={BASE_URL + `/media/` + image.path?.replace(/\\/g, '/')} 
                        alt={`View ${index + 1}`}
                        onError={(e) => {
                          e.target.src = '/placeholder-image.jpg';
                        }}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="lot-description">
              <h1 className="lot-title">{lot?.title}</h1>
              <div className="lot-meta">
                <span className="category">{lot?.category?.name}</span>
                {lot?.condition && <span className="condition">Condition: {lot.condition}</span>}
              </div>
              
              <div className="description-text">
                <div
                  className="description-content"
                  dangerouslySetInnerHTML={{ __html: lot?.description }}
                />
              </div>

              {/* Reserve Status */}
              {lot?.reserve_price && (
                <div className="reserve-status">
                  <span className={`reserve-badge ${lot.reserve_met ? 'met' : 'not-met'}`}>
                    {lot.reserve_met ? '✓ Reserve Met' : '⚠ Reserve Not Met'}
                  </span>
                  {!lot.reserve_met && (
                    <small>Reserve: ₹{lot.reserve_price.toLocaleString()}</small>
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="lot-right">
            <div className="bidding-section">
              <div className="current-bid-info">
                <div className="current-bid">
                  <span className="label">Current Bid</span>
                  <span className="amount">₹{lot?.current_bid?.toLocaleString() || '0'}</span>
                </div>
                {lot?.high_bidder && (
                  <div className="high-bidder">
                    <small>High Bidder: {lot.high_bidder}</small>
                  </div>
                )}
              </div>

              <div className="next-bid-info">
                <span className="next-bid-label">Next Bid:</span>
                <span className="next-bid-amount">₹{lot?.next_required_bid?.toLocaleString() || '0'}</span>
              </div>

              {!auctionEnded && (
                <>
                  <div className="input-group">
                    <span className="input-group-text">₹</span>
                    <input
                      type="text"
                      id="bidAmount"
                      className="form-control"
                      value={bidAmount}
                      onChange={handleBidAmountChange}
                      placeholder="Enter your bid amount"
                      disabled={isPlacingBid}
                    />
                  </div>
                  <small className="form-text text-muted">
                    Minimum bid: ₹{lot?.next_required_bid?.toLocaleString() || '0'}
                  </small>

                  <div className="bid-actions">
                    <button 
                      className="bid-btn primary"
                      onClick={handlePlaceBid}
                      disabled={isPlacingBid || !bidAmount || parseFloat(bidAmount) < lot?.next_required_bid}
                    >
                      {isPlacingBid ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Placing Bid...
                        </>
                      ) : (
                        'Place Bid'
                      )}
                    </button>
                    <button 
                      className="bid-btn secondary"
                      onClick={handleQuickBid}
                      disabled={isPlacingBid}
                    >
                      Quick Bid (₹{lot?.next_required_bid?.toLocaleString()})
                    </button>
                  </div>
                </>
              )}

              <div className="auction-timer">
                <LiveTimer 
                  key={timerKey}
                  endTime={lot?.lot_end_time || lot?.endTime} 
                />
              </div>

              {auctionEnded && (
                <div className="auction-ended">
                  <h3>Auction Ended</h3>
                  {lot?.high_bidder && (
                    <p>Winning Bid: ₹{lot.current_bid?.toLocaleString()} by {lot.high_bidder}</p>
                  )}
                </div>
              )}

              <div className="auction-stats">
                <div className="stat">
                  <span className="stat-number">{lot?.totalBids || 0}</span>
                  <span className="stat-label">Bids</span>
                </div>
                <div className="stat">
                  <span className="stat-number">{lot?.watchers || 0}</span>
                  <span className="stat-label">Watchers</span>
                </div>
                <div className="stat">
                  <span className="stat-number">₹{lot?.starting_bid?.toLocaleString() || '0'}</span>
                  <span className="stat-label">Starting Bid</span>
                </div>
              </div>

              <div className="watch-actions">
                <button className="watch-btn">👁️ Watch This Lot</button>
                <button className="share-btn">📤 Share</button>
                <button className="history-btn" onClick={toggleBidHistory}>
                  📊 {showBidHistory ? 'Hide' : 'Show'} Bid History
                </button>
              </div>

              {/* Bid History */}
              {showBidHistory && (
                <div className="bid-history">
                  <h4>Bid History</h4>
                  {historyData.length > 0 ? (
                    <div className="history-list">
                      {historyData.map((bid, index) => (
                        <div key={index} className="history-item">
                          <span className="bid-amount">₹{bid.amount.toLocaleString()}</span>
                          <span className="bid-time">{new Date(bid.created_at).toLocaleString()}</span>
                          <span className="bidder-name">{bid.bidder_name}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No bids yet</p>
                  )}
                </div>
              )}

              {/* WebSocket Connection Status */}
              {connectionStatus && (
                <div className={`connection-status ${connectionStatus.toLowerCase()}`}>
                  <small>Live Updates: {connectionStatus}</small>
                </div>
              )}
            </div>

            <div className="similar-lots">
              <h3>Similar Lots</h3>
              <div className="similar-item">
                <img src="https://via.placeholder.com/80x80" alt="Similar item" />
                <div className="similar-info">
                  <div className="similar-title">Similar Item 1</div>
                  <div className="similar-price">₹1,200</div>
                </div>
              </div>
              <div className="similar-item">
                <img src="https://via.placeholder.com/80x80" alt="Similar item" />
                <div className="similar-info">
                  <div className="similar-title">Similar Item 2</div>
                  <div className="similar-price">₹850</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LotDetails;