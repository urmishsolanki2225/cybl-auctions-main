import { useNavigate } from "react-router-dom";
import "../styles/Category.css";
import { useEffect, useState } from "react";
import { publicApi } from "../api/apiUtils";
import BASE_URL from "../api/endpoints";

const Category = () => {
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategory = async () => {
      try {
        setLoading(true);
        const response = await publicApi.getCategories();
        const sorted = sortCategories(response);
        setCategories(sorted);
      } catch (err) {
        console.error("Failed to load categories", err);
        setError("Failed to load categories");
      } finally {
        setLoading(false);
      }
    };

    fetchCategory();
  }, []);

  const sortCategories = (data: any[]) => {
    const sortByOrder = (a: any, b: any) => {
      if (a.order === null && b.order === null) return 0;
      if (a.order === null) return 1;
      if (b.order === null) return -1;
      return a.order - b.order;
    };

    if (!Array.isArray(data)) return [];

    return data
      .slice()
      .sort(sortByOrder)
      .map((category) => ({
        ...category,
        subcategories: Array.isArray(category.subcategories)
          ? category.subcategories.slice().sort(sortByOrder)
          : [],
      }));
  };

  return (
    <div className="category-page">
      <div className="auctions-container">
        {loading ? (
          <div className="loading-state">Loading...</div>
        ) : error ? (
          <div className="loading-state">{error}</div>
        ) : (
          <div className="categories-grid">
            {categories.map((cat) => (
              <div key={cat.id} className="category-card" onClick={() => navigate(`/category/${cat.id}`)}>
                {cat.image ? (
                  <div
                    className="category-image"
                    style={{ backgroundImage: `url(${BASE_URL}${cat.image})` }}
                    aria-label={cat.name}
                    onError={(e) => (e.currentTarget.style.display = "none")}
                  />
                ) : (
                  <div className="category-placeholder">
                    {cat.name?.[0]?.toUpperCase() ?? "?"}
                  </div>
                )}
                <h2 className="category-title">{cat.name}</h2>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Category;
