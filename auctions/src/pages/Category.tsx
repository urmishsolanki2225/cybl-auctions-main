import { useParams } from 'react-router-dom';
import '../styles/Category.css';

const Category = () => {
  const { categoryId } = useParams();
  
  const categoryData = {
    art: {
      title: "Art & Collectibles",
      description: "Discover rare artworks, vintage collectibles, and unique pieces from renowned artists and collectors worldwide.",
      icon: "🎨"
    },
    jewelry: {
      title: "Jewelry & Watches",
      description: "Exquisite jewelry pieces, luxury timepieces, and precious gemstones from top brands and designers.",
      icon: "💎"
    },
    electronics: {
      title: "Electronics",
      description: "Cutting-edge gadgets, vintage electronics, and rare tech collectibles for enthusiasts and collectors.",
      icon: "📱"
    },
    vehicles: {
      title: "Vehicles",
      description: "Classic cars, vintage motorcycles, and rare automotive collectibles from every era.",
      icon: "🚗"
    }
  };

  const currentCategory = categoryData[categoryId as keyof typeof categoryData] || categoryData.art;

  return (
    <div className="category-page">
      <div className="container">
        <div className="category-header">
          <div className="category-icon">{currentCategory.icon}</div>
          <h1 className="category-title">{currentCategory.title}</h1>
          <p className="category-description">{currentCategory.description}</p>
        </div>
        
        <div className="category-content">
          <h2>Coming Soon</h2>
          <p>Category-specific auctions will be available here. Stay tuned for amazing {currentCategory.title.toLowerCase()} auctions!</p>
        </div>
      </div>
    </div>
  );
};

export default Category;