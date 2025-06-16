import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import BASE_URL from '../../api/endpoints';

interface Lot {
  id: number;
  title: string;
  image: string;
  estimate: string;
}

interface LotsCarouselProps {
  lots: Lot[];
  auctionId: number;
}

const LotsCarousel: React.FC<LotsCarouselProps> = ({ lots, auctionId }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto-rotate carousel every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % lots?.length);
    }, 4000);

    return () => clearInterval(interval);
  }, [lots?.length]);

  // Show 4 lots at a time, cycling through
  const getVisibleLots = () => {
    const visible = [];
    for (let i = 0; i < 4; i++) {
      const index = (currentIndex + i) % lots?.length;
      visible.push(lots?.[index]);
    }
    return visible;
  };

  const handlePrevious = () => {
    setCurrentIndex((prevIndex) => 
      prevIndex === 0 ? lots.length - 1 : prevIndex - 1
    );
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % lots?.length);
  };

  const visibleLots = getVisibleLots();

  return (
    <div className="lots-carousel">
      <div className="carousel-header">
        <h4 className="section-title">Featured Lots</h4>
        <div className="carousel-controls">
          <button 
            onClick={handlePrevious}
            className="carousel-btn carousel-btn-prev"
            aria-label="Previous lots"
          >
            <ChevronLeft size={20} />
          </button>
          <button 
            onClick={handleNext}
            className="carousel-btn carousel-btn-next"
            aria-label="Next lots"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
      
      <div className="lots-grid">
        {visibleLots.map((lot, index) => (
          <Link 
            key={`${lot?.id}-${currentIndex}-${index}`}
            to={`lot/${lot?.id}`}
            className="lot-item"
          >
            <img  
              src={ BASE_URL + '/media/' +lot?.media_items[0]?.path || 'https://demofree.sirv.com/nope-not-here.jpg'} 
              alt={lot?.title}
              className="lot-image"
              onError={(e) => {
                e.currentTarget.src = 'https://demofree.sirv.com/nope-not-here.jpg';
              }}
            />
          </Link>
        ))}
      </div>

      {/* Dots indicator */}
      <div className="carousel-dots">
        {lots?.map((_, index) => (
          <button
            key={index}
            className={`carousel-dot ${index === currentIndex ? 'active' : ''}`}
            onClick={() => setCurrentIndex(index)}
            aria-label={`Go to lot ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
};

export default LotsCarousel;