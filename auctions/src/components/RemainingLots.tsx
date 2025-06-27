import React from 'react';
import { Link } from 'react-router-dom';
import BASE_URL from "../api/endpoints";

// Import Swiper
import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/pagination';
import { Navigation, Pagination } from 'swiper/modules';

const RemainingLots = ({ lots }) => {
  if (!lots || lots.length === 0) return null;

  return (
    <div className="remaining-lots-section">
      <h3 className="section-title">Next Lots</h3>
      
      {/* Swiper Slider */}
      <Swiper
        slidesPerView={1}
        spaceBetween={20}
        navigation={true}
        pagination={{ clickable: true }}
        breakpoints={{
          640: { slidesPerView: 2 },
          768: { slidesPerView: 3 },
          1024: { slidesPerView: 4 },
        }}
        modules={[Navigation, Pagination]}
        className="remaining-lots-swiper"
      >
        {lots.map((lot) => (
          <SwiperSlide key={lot.id}>
            <Link to={`/lot/${lot.id}`} className="remaining-lot-card">
              <div className="lot-image-container-next-lot">
                {lot.thumbnail ? (
                  <img 
                    src={`${BASE_URL}/media/${lot.thumbnail.replace(/\\/g, "/")}`} 
                    alt={lot.title}
                    className="lot-thumbnail"
                    onError={(e) => {
                      e.target.src = "/placeholder-image.jpg";
                    }}
                  />
                ) : (
                  <div className="lot-thumbnail-placeholder">
                    <span>No Image</span>
                  </div>
                )}
              </div>
              <div className="lot-info">
                <h4 className="lot-title">{lot.title}</h4>
                <div className="lot-meta">
                  <span className="current-bid">${lot.current_bid}</span>
                  <span className="lot-end-time">
                    Ends: {new Date(lot.lot_end_time).toLocaleString()}
                  </span>
                </div>
              </div>
            </Link>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default RemainingLots;