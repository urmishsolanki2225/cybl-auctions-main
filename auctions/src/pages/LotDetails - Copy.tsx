import { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { publicApi, protectedApi } from "../api/apiUtils"; // Import protectedApi
import useWebSocket from "../hooks/useWebSocket";
import "../styles/LotDetails.css";
import BASE_URL from "../api/endpoints";
import LiveTimer from "../components/LiveTimer";
import { toast } from "react-toastify";
import { useAuth } from "../context/AuthContext";
import LoginModal from "../components/LoginModal";
import WatchlistButton from "../components/WatchlistButton";
import SocialShare from "../components/SocialShare";

// Import Swiper React components
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/free-mode';
import 'swiper/css/navigation';
import 'swiper/css/thumbs';
import { FreeMode, Navigation, Thumbs } from 'swiper/modules';


const LotDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("description");
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState("");
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);

  const [selectedImage, setSelectedImage] = useState(0);
  const [lot, setLot] = useState(null);
  const [currentBid, setCurrentBid] = useState(0);
  const [bidHistory, setBidHistory] = useState([]);
  const [isPlacingBid, setIsPlacingBid] = useState(false);
  const [lotStatus, setLotStatus] = useState("unsold");

  const [winner, setWinner] = useState(null);
  const [winningAmount, setWinningAmount] = useState(null);
  const [showWinnerAnnouncement, setShowWinnerAnnouncement] = useState(false);
  const [winnerData, setWinnerData] = useState(null);

  const [showLoginModal, setShowLoginModal] = useState(false);
  const { isAuthenticated } = useAuth();

  const user = JSON.parse(localStorage.getItem("user"));

  const [thumbsSwiper, setThumbsSwiper] = useState(null);

  // Load comments when component mounts - ONLY ONCE on initial load
  useEffect(() => {
    if (isAuthenticated && id) {
      loadInitialComments();
    }
  }, [isAuthenticated, id]);

  const loadInitialComments = async () => {
    try {
      const commentsData = await protectedApi.getLotComments(id);
      setComments(commentsData);
    } catch (error) {
      console.error("Error loading initial comments:", error);
      // Don't show error toast for initial load failure
    }
  };

  // REMOVE the old handleCommentSubmit function and replace with WebSocket version
  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || !isAuthenticated) return;

    if (!user) {
      setShowLoginModal(true);
      return;
    }

    const socket = getSocket();
    if (socket && socket.readyState === WebSocket.OPEN) {
      setIsSubmittingComment(true);
      
      const message = {
        type: "post_comment",
        comment_text: newComment.trim(),
        user_id: user.id,
      };

      socket.send(JSON.stringify(message));
      console.log("📤 Comment sent via WebSocket:", message);
      
      // Clear the input immediately for better UX
      setNewComment("");
    } else {
      toast.error("Connection lost. Please refresh the page.");
    }
  };

  const handleMessage = useCallback(
    async (message) => {
      console.log("📩 Incoming message:", message);

      if (message.type === "lot_status") {
        setLot((prev) => ({
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

      // ADD NEW HANDLER FOR COMMENT POSTED
      if (message.type === "comment_posted") {
        console.log("💬 New comment received:", message.data);
        
        setComments((prevComments) => [message.data, ...prevComments]);
        
        // Reset submitting state
        setIsSubmittingComment(false);
        
        // Show success toast only for the user who posted
        if (message?.data?.user_id === user?.id) {
          toast.success("Comment posted successfully!");
        } else {
          // Optional: Show notification for new comments from others
          toast.info(`New comment from ${message?.data?.username}`);
        }
      }

      if (message.type === "bid_placed") {
        // Reset loading state when bid response is received
        setIsPlacingBid(false);

        const bidAmount = parseFloat(message.data?.amount || "0");
        const nextBid = parseFloat(message.data?.next_required_bid || "0");

        setLot((prev) => ({
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
        setLot((prev) => ({
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
          setLot((prev) => ({
            ...prev,
            lot_start_time: refreshedData.lot_start_time,
            lot_end_time: refreshedData.lot_end_time,
            startTime: refreshedData.lot_start_time,
            endTime: refreshedData.lot_end_time,
          }));

          if (message.data.trigger_lot_id !== parseInt(id)) {
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
        setIsSubmittingComment(false); // Reset comment loading state on error
        toast.error(message.message || "An error occurred");
        console.error("❌ WebSocket Error:", message.message);
      }
    },
    [id, user?.id]
  );

  const { getSocket } = useWebSocket({ lotId: id, onMessage: handleMessage });

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
                      : "../assets/default-avatar.png"
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
            {/*<div className="image-gallery">
              <div className="main-image">nnnnnnnnnnnnnnnn
                {lot?.media_items && lot.media_items?.length > 0 ? (
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
              {lot?.media_items && lot.media_items?.length > 1 && (
                <div className="thumbnail-list">
                  {lot.media_items.map((image, index) => (
                    <div
                      key={index}
                      className={`thumbnail ${
                        selectedImage === index ? "active" : ""
                      }`}
                      onClick={() => setSelectedImage(index)}
                    >
                      12333333333333333333333333<img
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
            </div>*/}
            <div className="image-gallery" style={{ width: '737px', height: '557px' }}>
              {lot?.media_items && lot.media_items.length > 0 ? (
                <>
                  {/* Main Image Swiper */}
                  <Swiper
                    style={{ width: '100%', height: '400px' }}
                    spaceBetween={10}
                    thumbs={{ swiper: thumbsSwiper }}
                    modules={[Thumbs, Navigation]} // ✅ Add Navigation here
                    navigation={true} // ✅ Enable arrows
                    className="main-image-swiper"
                  >
                    {lot.media_items.map((image, index) => (
                      <SwiperSlide key={index}>
                        <img
                          src={BASE_URL + `/media/` + image.path?.replace(/\\/g, "/")}
                          alt={lot?.title || `Image ${index + 1}`}
                          onError={(e) => {
                            e.target.src = "/placeholder-image.jpg";
                          }}
                          style={{ width: '500px', height: '500px', objectFit: 'cover' }}
                        />
                      </SwiperSlide>
                    ))}
                  </Swiper>

                  {/* Thumbnail Swiper */}
                  {lot.media_items.length > 1 && (
                    <Swiper
                      onSwiper={setThumbsSwiper}
                      spaceBetween={10}
                      slidesPerView={5}
                      watchSlidesProgress={true}
                      modules={[Thumbs]}
                      className="thumbnail-swiper"
                      style={{ marginTop: '10px' }}
                    >
                      {lot.media_items.map((image, index) => (
                        <SwiperSlide key={`thumb-${index}`}>
                          <img
                            src={BASE_URL + `/media/` + image.path?.replace(/\\/g, "/")}
                            alt={`Thumb ${index + 1}`}
                            onError={(e) => {
                              e.target.src = "/placeholder-image.jpg";
                            }}
                            style={{
                              width: '100px',
                              height: '100px',
                              objectFit: 'cover',
                              borderRadius: '8px',
                            }}
                          />
                        </SwiperSlide>
                      ))}
                    </Swiper>
                  )}
                </>
              ) : (
                <div className="no-image">No Image Available</div>
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
              <div className="tab-container">
                <div className="tab-buttons">
                  <button
                    className={`tab-button ${
                      activeTab === "description" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("description")}
                  >
                    Description
                  </button>
                  <button
                    className={`tab-button ${
                      activeTab === "bids" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("bids")}
                  >
                    Bid History
                  </button>
                  <button
                    className={`tab-button ${
                      activeTab === "comments" ? "active" : ""
                    }`}
                    onClick={() => setActiveTab("comments")}
                  >
                    Comments ({comments?.length})
                  </button>
                </div>

                <div className="tab-content">
                  {activeTab === "description" && (
                    <div className="description-text">
                      <div
                        className="description-content"
                        dangerouslySetInnerHTML={{ __html: lot?.description }}
                      />
                    </div>
                  )}

                  {activeTab === "bids" && (
                    <div className="bid-history-container">
                      {bidHistory && bidHistory?.length > 0 ? (
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
                                  BASE_URL + "../assets/default-avatar.png"
                                }
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
                                  <span className="bid-amount">
                                    ${bid.amount}
                                  </span>
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
                  )}

                  {activeTab === "comments" && (
                    <div className="comments-section">
                      {/* Comments list */}
                      {comments?.length > 0 ? (
                        <div className="comments-list">
                          {comments.map((comment) => (
                            <div key={comment?.id} className="comment-item">
                              <div className="comment-avatar-container">
                                <img
                                  src={
                                    comment?.profile_photo
                                      ? `${BASE_URL}${comment?.profile_photo}`
                                      : "../assets/default-avatar.png"
                                  }
                                  alt={comment?.username}
                                  className="comment-avatar"
                                />
                              </div>
                              <div className="comment-content">
                                <div className="comment-header">
                                  <span className="comment-username">
                                    {comment?.username}
                                    {comment?.user_id === user?.id && (
                                      <span className="you-tag"> (You)</span>
                                    )}
                                  </span>
                                  <span className="comment-time">
                                    {new Date(
                                      comment?.created_at
                                    ).toLocaleString([], {
                                      year: "numeric",
                                      month: "short",
                                      day: "numeric",
                                      hour: "2-digit",
                                      minute: "2-digit",
                                    })}
                                  </span>
                                </div>
                                <p className="comment-text">
                                  {comment?.content}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="no-comments">
                          <div className="no-comments-icon">💬</div>
                          <p>No comments yet</p>
                          <p>Be the first to comment!</p>
                        </div>
                      )}

                      {/* Comment form */}
                      {isAuthenticated ? (
                        <form
                          onSubmit={handleCommentSubmit}
                          className="comment-form"
                        >
                          <textarea
                            value={newComment}
                            onChange={(e) => setNewComment(e.target.value)}
                            placeholder="Share your thoughts about this lot..."
                            rows={4}
                            required
                            disabled={isSubmittingComment}
                          />
                          <div className="comment-form-footer">
                            <button
                              type="submit"
                              disabled={
                                isSubmittingComment || !newComment.trim()
                              }
                              className="submit-comment-btn"
                            >
                              {isSubmittingComment ? (
                                <>
                                  <span className="spinner"></span> Posting...
                                </>
                              ) : (
                                "Post Comment"
                              )}
                            </button>
                          </div>
                        </form>
                      ) : (
                        <div className="login-to-comment">
                          <button
                            onClick={() => setShowLoginModal(true)}
                            className="login-comment-btn"
                          >
                            <svg
                              width="20"
                              height="20"
                              viewBox="0 0 24 24"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <path
                                d="M12 12C14.7614 12 17 9.76142 17 7C17 4.23858 14.7614 2 12 2C9.23858 2 7 4.23858 7 7C7 9.76142 9.23858 12 12 12Z"
                                fill="currentColor"
                              />
                              <path
                                d="M12 14C7.58172 14 4 17.5817 4 22H20C20 17.5817 16.4183 14 12 14Z"
                                fill="currentColor"
                              />
                            </svg>
                            Login to comment
                          </button>
                        </div>
                      )}
                    </div>
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