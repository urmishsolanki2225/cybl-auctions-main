import { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { publicApi } from "../api/apiUtils";
import useWebSocket from "../hooks/useWebSocket";
import "../styles/LotDetails.css";
import BASE_URL from "../api/endpoints";
import LiveTimer from "../components/LiveTimer";
import { toast } from "react-toastify";
import { useAuth } from "../context/AuthContext";
import LoginModal from "../components/LoginModal";
import WatchlistButton from "../components/WatchlistButton";
import SocialShare from "../components/SocialShare";

const LotDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(0);
  const [lot, setLot] = useState<any>(null);
  const [currentBid, setCurrentBid] = useState<number>(0);
  const [bidHistory, setBidHistory] = useState<any[]>(lot?.bid_history || []);
  const [isPlacingBid, setIsPlacingBid] = useState(false);
  const [lotStatus, setLotStatus] = useState<string>("unsold");

  const [winner, setWinner] = useState(null);
  const [winningAmount, setWinningAmount] = useState(null);
  const [showWinnerAnnouncement, setShowWinnerAnnouncement] = useState(false);
  const [winnerData, setWinnerData] = useState(null);

  // Inside the LotDetails component, add these state variables
  const [showLoginModal, setShowLoginModal] = useState(false);
  const { isAuthenticated } = useAuth();

  const user = JSON.parse(localStorage.getItem("user"));

  const handleMessage = useCallback(
    async (message: any) => {
      console.log("📩 Incoming message:", message);

      if (message.type === "lot_status") {
        setLot((prev: any) => ({
          ...prev,
          ...message.data,
        }));

        if (typeof message.data?.current_bid === "number") {
          setCurrentBid(message.data.current_bid);
        }

        if (message.data?.bid_history) {
          setBidHistory(message.data.bid_history);
        }
      }

      if (message.type === "bid_placed") {
        // Reset loading state when bid response is received
        setIsPlacingBid(false);

        const bidAmount = parseFloat(message.data?.amount || "0");
        const nextBid = parseFloat(message.data?.next_required_bid || "0");

        setLot((prev: any) => ({
          ...prev,
          next_required_bid: nextBid,
          reserve_met: message.data.reserve_met,
          lot_end_time: message.data.lot_end_time,
          endTime: message.data.lot_end_time,
        }));

        // Update bid history if included in message
        if (message.data.bid_history) {
          setBidHistory(message.data.bid_history);
        }

        setCurrentBid(bidAmount);
        // Show success toast for the user who placed the bid
        if (message.data.user_id == user?.id) {
          let toastMessage = `Your bid of $${bidAmount} has been placed successfully!`;
          if (message.data.timer_extended) {
            toastMessage += ` Timer extended!`;
          }
          toast.success(toastMessage);
        } else {
          // Show info toast for other users
          let toastMessage = `New bid placed: $${bidAmount}`;
          if (message.data.timer_extended) {
            toastMessage += ` - Timer extended!`;
          }
          toast.info(toastMessage);
        }
      } else if (message.type === "reserve_met") {
        toast.success(`🎉 Reserve has been met!`);
      } else if (message.type === "timer_extended") {
        setLot((prev: any) => ({
          ...prev,
          lot_end_time: message.data.new_end_time,
          endTime: message.data.new_end_time,
        }));

        toast.info(
          `⏰ Timer extended by ${message.data.extended_by_seconds} seconds!`
        );
      } else if (message.type === "schedule_updated") {
        try {
          // Refresh lot data to get updated times
          const refreshedData = await publicApi.getLotDetails(id);
          setLot((prev: any) => ({
            ...prev,
            lot_start_time: refreshedData.lot_start_time,
            lot_end_time: refreshedData.lot_end_time,
            startTime: refreshedData.lot_start_time,
            endTime: refreshedData.lot_end_time,
          }));

          if (message.data.trigger_lot_id !== parseInt(id!)) {
            toast.info(`📅 Schedule updated due to extension in another lot`);
          }
        } catch (error) {
          console.error("Error refreshing lot data:", error);
        }
      } else if (message.type === "lot_ended") {
        console.log("🏆 Lot ended with winner data:", message.data);

        const { winner } = message.data;
        setWinnerData(winner);
        setShowWinnerAnnouncement(true);

        // Update lot status
        setLotStatus(winner.status);

        if (winner.status === "sold") {
          setWinner(winner.username);
          setWinningAmount(winner.winning_amount);

          // Show different toasts based on whether the user won
          if (winner.user_id === user?.id) {
            toast.success(
              `🎉 Congratulations! You won this lot for $${winner.winning_amount}!`,
              {
                autoClose: 8000,
              }
            );
          } else {
            toast.info(
              `🏆 Lot sold to ${winner.username} for $${winner.winning_amount}`,
              {
                autoClose: 5000,
              }
            );
          }
        } else {
          toast.warning(`❌ Lot ended without a sale. ${winner.reason || ""}`, {
            autoClose: 5000,
          });
        }

        // Auto-hide winner announcement after 10 seconds
        setTimeout(() => {
          setShowWinnerAnnouncement(false);
        }, 10000);
      } else if (message.type === "error") {
        setIsPlacingBid(false); // Reset loading state on error
        toast.error(message.message || "An error occurred");
        console.error("❌ WebSocket Error:", message.message);
      }
    },
    [id, user?.id]
  );

  const { getSocket } = useWebSocket({ lotId: id!, onMessage: handleMessage });

  useEffect(() => {
    const fetchLot = async () => {
      try {
        const data = await publicApi.getLotDetails(id);
        setLot(data);
        setCurrentBid(data.current_bid || data.starting_price || 0);
        setBidHistory(data.bid_history || []);
        setLotStatus(data.status || "");
        setWinner(data.winner || null);
        setWinningAmount(data.winning_amount || null);
      } catch (err) {
        console.error("Error loading lot:", err);
      }
    };

    fetchLot();
  }, [id]);

  if (!lot) return <p>Loading...</p>;

  const handlePlaceBid = () => {
    if (!isAuthenticated) {
      setShowLoginModal(true);
      return;
    }

    if (user) {
      const socket = getSocket();
      if (socket && socket.readyState === WebSocket.OPEN) {
        const bidAmount = lot.next_required_bid;

        // Set loading state
        setIsPlacingBid(true);

        const message = {
          type: "place_bid",
          bid_amount: bidAmount,
          user_id: user.id,
        };

        socket.send(JSON.stringify(message));
        console.log("📤 Bid sent:", message);
      } else {
        console.warn("🚫 WebSocket not connected.");
      }
    } else {
      navigate("/login");
    }
  };

  // Fix the WinnerAnnouncement component positioning
  const WinnerAnnouncement = ({ winnerData, onClose }) => {
    if (!winnerData || !showWinnerAnnouncement) return null;

    return (
      <div className="winner-announcement-overlay">
        <div className="winner-announcement-modal">
          <button className="close-announcement" onClick={onClose}>
            ×
          </button>

          {winnerData.status === "sold" ? (
            <div className="winner-content">
              <div className="winner-crown">👑</div>
              <h2>Auction Ended!</h2>

              <div className="winner-profile">
                <img
                  src={
                    winnerData.profile_photo
                      ? BASE_URL + winnerData.profile_photo
                      : "/default-avatar.png"
                  }
                  alt={winnerData.username}
                  className="winner-avatar"
                />
                <div className="winner-info">
                  <h3>{winnerData.username}</h3>
                  {winnerData.user_id === user?.id && (
                    <span className="you-won-badge">🎉 You Won!</span>
                  )}
                </div>
              </div>

              <div className="winning-amount">
                <span className="amount-label">Winning Bid:</span>
                <span className="amount">${winnerData.winning_amount}</span>
              </div>

              {winnerData.user_id === user?.id && (
                <div className="next-steps">
                  <p>Congratulations! Please proceed to payment.</p>
                  <button className="proceed-payment-btn">
                    Proceed to Payment
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="unsold-content">
              <div className="unsold-icon">❌</div>
              <h2>Auction Ended</h2>
              <p>This lot was not sold</p>
              <p className="reason">{winnerData.reason}</p>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="lot-details-page">
      <div className="container">
        <div className="lot-details-header">
            <WinnerAnnouncement 
              winnerData={winnerData} 
              onClose={() => setShowWinnerAnnouncement(false)} 
            />
          <div className="breadcrumb">
            <strong>{lot?.title} --- </strong>
            <span>{lot?.category?.name || "Category"}</span>
          </div>
          <div className="">
            <WatchlistButton inventoryId={lot.id} size="small" />
          </div>
        </div>

        <div className="lot-main">
          <div className="lot-left">
            <div className="image-gallery">
              <div className="main-image">
                {lot?.media_items && lot.media_items.length > 0 ? (
                  <img
                    src={
                      BASE_URL +
                      `/media/` +
                      lot.media_items[selectedImage]?.path?.replace(/\\/g, "/")
                    }
                    alt={lot?.title}
                    onError={(e) => {
                      e.target.src = "/placeholder-image.jpg"; // Add a placeholder image
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
                      className={`thumbnail ${
                        selectedImage === index ? "active" : ""
                      }`}
                      onClick={() => setSelectedImage(index)}
                    >
                      <img
                        src={
                          BASE_URL + `/media/` + image.path?.replace(/\\/g, "/")
                        }
                        alt={`View ${index + 1}`}
                        onError={(e) => {
                          e.target.src = "/placeholder-image.jpg";
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
                {lot?.condition && (
                  <span className="condition">Condition: {lot.condition}</span>
                )}
              </div>

              <div className="description-text">
                <div
                  className="description-content"
                  dangerouslySetInnerHTML={{ __html: lot?.description }}
                />
              </div>
              <div className="bid-history-section">
                <h3 className="section-title">Bid History</h3>
                <div className="bid-history-container">
                  {bidHistory && bidHistory.length > 0 ? (
                    <div className="bid-history-list">
                      {bidHistory.map((bid, index) => (
                        <div
                          className={`bid-history-item ${
                            bid.user_id === user?.id ? "your-bid" : ""
                          }`}
                          key={bid.id || index}
                        >
                          <img
                            src={
                              BASE_URL + bid.profile ||
                              BASE_URL + "/default-avatar.png"
                            } // fallback image
                            alt={bid.bidder}
                            className="bidder-avatar"
                          />
                          <div className="bid-info">
                            <div className="bidder-name">
                              {bid.bidder}
                              {bid.user_id === user?.id && (
                                <span className="you-tag"> (You)</span>
                              )}
                            </div>
                            <div className="bid-meta">
                              <span className="bid-amount">${bid.amount}</span>
                              <span className="bid-time">
                                {new Date(bid.timestamp).toLocaleString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="no-bids">No bids placed yet</div>
                  )}
                </div>
              </div>
            </div>
          </div>
          <div className="lot-right">
            <div className="bidding-section">
              <div className="auction-timer">
                <LiveTimer endTime={lot?.lot_end_time || lot?.endTime} />
              </div>
              <div>
                <div className="current-bid">
                  {/* Reserve Status */}
                  {lot?.reserve_price && (
                    <div>
                      <span
                        className={`reserve-badge ${
                          lot.reserve_met ? "met" : "not-met"
                        }`}
                      >
                        {lot.reserve_met
                          ? "✓ Reserve Met"
                          : "⚠ Reserve Not Met"}
                      </span>
                      <div>
                        {!lot.reserve_met && (
                          <span className="label">
                            Reserve: ${lot.reserve_price.toLocaleString()}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                <div className="current-bid-info">
                  <div className="current-bid">
                    <span className="label">Starting bid</span>
                    <span className="amount">${lot.starting_bid || "0"}</span>
                  </div>
                  <div className="current-bid">
                    <span className="label">Current Bid</span>
                    <span className="amount">${currentBid || "0"}</span>
                  </div>
                  <div>
                    <SocialShare
                      title={lot?.title}
                      currentBid={currentBid}
                      nextBid={lot?.next_required_bid}
                      imageUrl={
                        BASE_URL +
                        `/media/` +
                        (lot?.media_items?.[0]?.path?.replace(/\\/g, "/") || "")
                      }
                      itemUrl={window.location.href}
                    />
                  </div>
                </div>
                <div className="next-bid-info">
                  <span className="next-bid-label">Next Bid:</span>
                  <span className="next-bid-amount">
                    ${lot?.next_required_bid?.toLocaleString() || "0"}
                  </span>
                </div>
                <div>
                  <button
                    className="bid-btn primary"
                    onClick={handlePlaceBid}
                    disabled={isPlacingBid}
                  >
                    {isPlacingBid
                      ? "Placing Bid..."
                      : `Place $${lot.next_required_bid} Bid`}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          onLoginSuccess={() => {
            setShowLoginModal(false);
            // Optionally automatically place the bid after login
            // handlePlaceBid();
          }}
        />
      )}
    </div>
  );
};

export default LotDetails;
