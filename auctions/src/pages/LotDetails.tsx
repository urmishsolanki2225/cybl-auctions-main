import { useEffect, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { publicApi } from "../api/apiUtils";
import useWebSocket from "../hooks/useWebSocket";
import "../styles/LotDetails.css";
import BASE_URL from "../api/endpoints";
import LiveTimer from "../components/LiveTimer";
import { toast } from "react-toastify";

const LotDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedImage, setSelectedImage] = useState(0);
  const [lot, setLot] = useState<any>(null);
  const [currentBid, setCurrentBid] = useState<number>(0);
  const user = JSON.parse(localStorage.getItem("user"));

  // const handleMessage = useCallback((message: any) => {
  //   console.log("📩 Incoming message:", message);

  //   if (message.type === "lot_status") {
  //     setLot((prev: any) => ({
  //       ...prev,
  //       ...message.data,
  //     }));

  //     if (typeof message.data?.current_bid === "number") {
  //       setCurrentBid(message.data.current_bid);
  //     }
  //   }

  //   if (message.type === "bid_placed") {
  //     const bidAmount = parseFloat(message.data?.amount || "0");
  //     const nextBid = parseFloat(message.data?.next_required_bid || "0");

  //     setLot((prev: any) => ({
  //       ...prev,
  //       next_required_bid: nextBid,
  //       reserve_met: message.data.reserve_met,
  //       lot_end_time: message.data.lot_end_time,
  //       endTime: message.data.lot_end_time,
  //     }));

  //     setCurrentBid(bidAmount);
  //     // Show success toast for the user who placed the bid
  //     if (message.data.user_id == user?.id) {
  //       let toastMessage = `Your bid of $${bidAmount} has been placed successfully!`;
  //       if (message.data.timer_extended) {
  //         toastMessage += ` Timer extended!`;
  //       }
  //       toast.success(toastMessage);
  //     } else {
  //       // Show info toast for other users
  //       let toastMessage = `New bid placed: $${bidAmount}`;
  //       if (message.data.timer_extended) {
  //         toastMessage += ` - Timer extended!`;
  //       }
  //       toast.info(toastMessage);
  //     }
  //   } else if (message.type === "reserve_met") {
  //     toast.success(`🎉 Reserve has been met!`);
  //   } else if (message.type === "timer_extended") {
  //     setLot((prev: any) => ({
  //       ...prev,
  //       lot_end_time: message.data.new_end_time,
  //       endTime: message.data.new_end_time,
  //     }));

  //     toast.info(
  //       `⏰ Timer extended by ${message.data.extended_by_seconds} seconds!`
  //     );
  //   } // Add this to the handleMessage callback:
  //   else if (message.type === "schedule_updated") {
  //     // Refresh lot data to get updated times
  //     const refreshedData = await publicApi.getLotDetails(id);
  //     setLot((prev: any) => ({
  //       ...prev,
  //       lot_start_time: refreshedData.lot_start_time,
  //       lot_end_time: refreshedData.lot_end_time,
  //       startTime: refreshedData.lot_start_time,
  //       endTime: refreshedData.lot_end_time,
  //     }));

  //     if (message.data.trigger_lot_id !== parseInt(id!)) {
  //       toast.info(`📅 Schedule updated due to extension in another lot`);
  //     }
  //   }
  // }, []);

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
      }

      if (message.type === "bid_placed") {
        const bidAmount = parseFloat(message.data?.amount || "0");
        const nextBid = parseFloat(message.data?.next_required_bid || "0");

        setLot((prev: any) => ({
          ...prev,
          next_required_bid: nextBid,
          reserve_met: message.data.reserve_met,
          lot_end_time: message.data.lot_end_time,
          endTime: message.data.lot_end_time,
        }));

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
      } catch (err) {
        console.error("Error loading lot:", err);
      }
    };

    fetchLot();
  }, [id]);

  if (!lot) return <p>Loading...</p>;

  const handlePlaceBid = () => {
    if (user) {
      const socket = getSocket();
      if (socket && socket.readyState === WebSocket.OPEN) {
        const bidAmount = lot.next_required_bid;

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

  return (
    <div className="lot-details-page">
      <div className="container">
        <div className="lot-header">
          <div className="breadcrumb">
            <span>Auctions</span> ---{" "}
            <span>{lot?.category?.name || "Category"}</span> ---{" "}
            <span>{lot?.title}</span>
          </div>
          <div className="lot-number">Lot #{lot?.lot_number || lot?.id}</div>
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
            </div>
          </div>
          <div className="lot-right">
            <div className="bidding-section">
              <div className="auction-timer">
                <LiveTimer endTime={lot?.lot_end_time || lot?.endTime} />
              </div>
              <div className="current-bid">
                {/* Reserve Status */}
                {lot?.reserve_price && (
                  <div>
                    <span
                      className={`reserve-badge ${
                        lot.reserve_met ? "met" : "not-met"
                      }`}
                    >
                      {lot.reserve_met ? "✓ Reserve Met" : "⚠ Reserve Not Met"}
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
              </div>
              <div className="next-bid-info">
                <span className="next-bid-label">Next Bid:</span>
                <span className="next-bid-amount">
                  ${lot?.next_required_bid?.toLocaleString() || "0"}
                </span>
              </div>
              <div>
                <button className="bid-btn primary" onClick={handlePlaceBid}>
                  Place ${lot.next_required_bid} Bid
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LotDetails;
