// WatchlistButton.tsx
import React, { useState, useEffect } from "react";
import { Heart } from "lucide-react";
import { protectedApi } from "../api/apiUtils";
import "../styles/WatchlistButton.css";

interface WatchlistButtonProps {
  inventoryId: number;
  size?: "small" | "medium" | "large";
  showText?: boolean;
  className?: string;
  onWatchlistChange?: (inventoryId: number, isInWatchlist: boolean) => void;
}

const WatchlistButton: React.FC<WatchlistButtonProps> = ({
  inventoryId,
  size = "medium",
  showText = false,
  className = "",
  onWatchlistChange = null,
}) => {
  const [isInWatchlist, setIsInWatchlist] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkWatchlistStatus();
  }, [inventoryId]);

  const checkWatchlistStatus = async () => {
    try {
      const watchlist = await protectedApi.getWatchlist();
      const isItemInWatchlist = watchlist.some(
        (item: any) => item.inventory_details.id === inventoryId
      );
      setIsInWatchlist(isItemInWatchlist);
    } catch (err: any) {
      if (err.status !== 401) {
        console.error("Error checking watchlist status:", err);
      }
    }
  };

  const handleWatchlistToggle = async () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      alert("Please login to add items to your watchlist");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (isInWatchlist) {
        await protectedApi.removeFromWatchlist(inventoryId);
        if (showText) alert("Item removed from watchlist");
      } else {
        await protectedApi.addToWatchlist(inventoryId);
        if (showText) alert("Item added to watchlist");
      }

      // Refresh the watchlist status after the operation
      await checkWatchlistStatus();

      // Call the callback with the new state (we get this from checkWatchlistStatus)
      if (onWatchlistChange) {
        onWatchlistChange(inventoryId, isInWatchlist);
      }
    } catch (err: any) {
      console.error("Watchlist operation failed:", err);
      if (err.status === 401) {
        setError("Please login to manage your watchlist");
        alert("Please login to manage your watchlist");
      } else {
        setError(err.message || "Failed to update watchlist");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getSizeClass = () => {
    switch (size) {
      case "small":
        return "watchlist-btn-small";
      case "large":
        return "watchlist-btn-large";
      default:
        return "watchlist-btn-medium";
    }
  };

  return (
    <button
      onClick={handleWatchlistToggle}
      disabled={isLoading}
      className={`watchlist-button ${getSizeClass()} ${
        isInWatchlist ? "active" : ""
      } ${className}`}
      title={isInWatchlist ? "Remove from watchlist" : "Add to watchlist"}
      aria-label={isInWatchlist ? "Remove from watchlist" : "Add to watchlist"}
    >
      <Heart
        className={`heart-icon ${isInWatchlist ? "filled" : ""}`}
        fill={isInWatchlist ? "currentColor" : "none"}
      />

      {showText && (
        <span className="watchlist-text">
          {isLoading
            ? "Loading..."
            : isInWatchlist
            ? "Remove from Watchlist"
            : "Add to Watchlist"}
        </span>
      )}

      {isLoading && <span className="loading-spinner"></span>}
    </button>
  );
};

export default WatchlistButton;
