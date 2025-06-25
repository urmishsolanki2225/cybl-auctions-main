// WatchlistButton.tsx
import React from "react";
import { Heart } from "lucide-react";
import { toast } from "react-toastify"; // ADD THIS MISSING IMPORT
import "../styles/WatchlistButton.css";
import { useWatchlist } from "../context/WatchlistContext";

interface WatchlistButtonProps {
  inventoryId: number;
  size?: "small" | "medium" | "large";
  showText?: boolean;
  className?: string;
}

const WatchlistButton: React.FC<WatchlistButtonProps> = ({
  inventoryId,
  size = "medium",
  showText = false,
  className = "",
}) => {
  const { watchlist, loading, addToWatchlist, removeFromWatchlist, isInitialized } = useWatchlist();
  const [isLoading, setIsLoading] = React.useState(false);

  const isInWatchlist = watchlist.includes(inventoryId);

  const handleWatchlistToggle = async (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation if button is inside a link
    e.stopPropagation(); // Prevent event bubbling
    
    const token = localStorage.getItem("authToken");
    if (!token) {
      toast.warning("Please login to manage your watchlist");
      return;
    }

    setIsLoading(true);
    try {
      if (isInWatchlist) {
        await removeFromWatchlist(inventoryId);
      } else {
        await addToWatchlist(inventoryId);
      }
    } catch (err) {
      console.error("Watchlist operation failed:", err);
      toast.error("Failed to update watchlist. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const getSizeClass = () => {
    switch (size) {
      case "small": return "watchlist-btn-small";
      case "large": return "watchlist-btn-large";
      default: return "watchlist-btn-medium";
    }
  };

  // Don't render until watchlist is initialized
  if (!isInitialized) {
    return (
      <button
        className={`watchlist-button ${getSizeClass()} ${className}`}
        disabled
      >
        <Heart className="heart-icon" fill="none" />
      </button>
    );
  }

  return (
    <button
      onClick={handleWatchlistToggle}
      disabled={loading || isLoading}
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

      {(loading || isLoading) && <span className="loading-spinner"></span>}
    </button>
  );
};

export default WatchlistButton;