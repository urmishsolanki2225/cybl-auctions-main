import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import BASE_URL from "../../api/endpoints";
import WatchlistButton from "../WatchlistButton";

interface Lot {
  id: number;
  title: string;
  media_items: Array<{ path: string }>;
  estimate?: string;
}

interface LotsCarouselProps {
  lots: Lot[];
  auctionId: number;
}

const LotsCarousel: React.FC<LotsCarouselProps> = ({ lots, auctionId }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  const itemsToShow = 4;

  useEffect(() => {
    const interval = setInterval(() => {
      if (!isHovered && lots?.length > itemsToShow) {
        setCurrentIndex((prev) => (prev + 1) % lots.length);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [isHovered, lots?.length]);

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? lots.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % lots.length);
  };

  const getVisibleLots = () => {
    const visible = [];
    for (let i = 0; i < itemsToShow; i++) {
      const index = (currentIndex + i) % lots?.length;
      visible.push(lots?.[index]);
    }
    return visible;
  };

  const visibleLots = getVisibleLots();

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        maxWidth: "1200px",
        margin: "0 auto",
        padding: "20px 0",
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header without controls */}
      <div style={{ padding: "0 20px", marginBottom: "20px" }}>
        <h3 style={{ fontSize: "1.5rem", fontWeight: "600", color: "#333" }}>
          Featured Lots
        </h3>
      </div>

      {/* Carousel container with navigation arrows */}
      <div style={{ position: "relative" }}>
        {/* Previous button - positioned on left side */}
        <button
          onClick={handlePrevious}
          style={{
            position: "absolute",
            left: "10px",
            top: "50%",
            transform: "translateY(-50%)",
            background: "rgba(255,255,255,0.8)",
            border: "none",
            borderRadius: "50%",
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
            zIndex: 10,
            transition: "all 0.3s ease",
            ":hover": {
              background: "rgba(255,255,255,1)",
            },
          }}
          aria-label="Previous lots"
        >
          <ChevronLeft size={24} color="#333" />
        </button>

        {/* Lots grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${itemsToShow}, 1fr)`,
            gap: "20px",
            padding: "0 20px",
            overflow: "hidden",
          }}
        >
          {visibleLots.map((lot, index) => (
            <Link
              key={`${lot?.id}-${index}`}
              to={`lot/${lot?.id}`}
              style={{
                position: "relative",
                borderRadius: "8px",
                overflow: "hidden",
                aspectRatio: "1/1",
                transition: "transform 0.3s ease",
                ":hover": {
                  transform: "translateY(-5px)",
                },
              }}
            >
              <img
                src={
                  lot?.media_items?.[0]?.path
                    ? `${BASE_URL}/media/${lot.media_items[0].path}`
                    : "https://demofree.sirv.com/nope-not-here.jpg"
                }
                alt={lot?.title || "Auction lot"}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  borderRadius: "8px",
                }}
                onError={(e) => {
                  e.currentTarget.src =
                    "https://demofree.sirv.com/nope-not-here.jpg";
                }}
              />
              <div className="watchlist-button-container">
                <WatchlistButton
                  inventoryId={lot.id}
                  size="small"
                  //onWatchlistChange={handleWatchlistChange}
                />
              </div>
              {lot?.title && (
                <div
                  style={{
                    position: "absolute",
                    bottom: "0",
                    left: "0",
                    right: "0",
                    background: "linear-gradient(transparent, rgba(0,0,0,0.7))",
                    padding: "15px 10px",
                    color: "white",
                  }}
                >
                  <h4
                    style={{
                      margin: "0",
                      fontSize: "0.9rem",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {lot.title}
                  </h4>
                  {lot.estimate && (
                    <p
                      style={{
                        margin: "5px 0 0",
                        fontSize: "0.8rem",
                        opacity: "0.9",
                      }}
                    >
                      Estimate: {lot.estimate}
                    </p>
                  )}
                </div>
              )}
            </Link>
          ))}
        </div>

        {/* Next button - positioned on right side */}
        <button
          onClick={handleNext}
          style={{
            position: "absolute",
            right: "10px",
            top: "50%",
            transform: "translateY(-50%)",
            background: "rgba(255,255,255,0.8)",
            border: "none",
            borderRadius: "50%",
            width: "40px",
            height: "40px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            cursor: "pointer",
            boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
            zIndex: 10,
            transition: "all 0.3s ease",
            ":hover": {
              background: "rgba(255,255,255,1)",
            },
          }}
          aria-label="Next lots"
        >
          <ChevronRight size={24} color="#333" />
        </button>
      </div>

      {/* Dots indicator */}
      {lots?.length > itemsToShow && (
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "8px",
            marginTop: "20px",
          }}
        >
          {lots?.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              style={{
                width: "10px",
                height: "10px",
                borderRadius: "50%",
                border: "none",
                background: index === currentIndex ? "#333" : "#ddd",
                cursor: "pointer",
                transition: "background 0.3s ease",
              }}
              aria-label={`Go to lot ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default LotsCarousel;
