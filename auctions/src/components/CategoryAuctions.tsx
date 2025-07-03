import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/free-mode";
import "swiper/css/navigation";
import { FreeMode, Navigation } from "swiper/modules";
import { useNavigate } from "react-router-dom";
import BASE_URL from "../api/endpoints";

const CategoryAuctions = ({ categories }) => {
  const navigate = useNavigate();
 {console.log("Urmsih", categories)}
  return (
    <div className="category-auctions-container">
      <h2>Auctions by Category</h2>
      
      <Swiper
        slidesPerView={3}
        spaceBetween={20}
        freeMode={true}
        navigation={true}
        modules={[FreeMode, Navigation]}
        className="category-swiper"
        breakpoints={{
          640: {
            slidesPerView: 2,
          },
          768: {
            slidesPerView: 3,
          },
          1024: {
            slidesPerView: 4,
          },
        }}
      >
        {categories.map((category) => (
          <SwiperSlide key={category.id}>
            <div 
              className="category-card"
              onClick={() => navigate(`/category/${category.id}`)}
            >
              <div className="category-image-container">
               
                  <img 
                    src={ BASE_URL + category.image} 
                    alt={category.name} 
                    className="category-image"
                  />
              </div>
              <div className="category-content">
                <h3 className="category-title">{category.name}</h3>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
};

export default CategoryAuctions;