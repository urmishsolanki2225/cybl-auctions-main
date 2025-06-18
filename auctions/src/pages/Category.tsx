import { useNavigate } from "react-router-dom";
import "../styles/Category.css";
import { useEffect, useState } from "react";
import { publicApi } from "../api/apiUtils";

const Category = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategory = async () => {
      try {
        setLoading(true);
        const response = await publicApi.getCategories();

        // Sort categories and subcategories
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
      <div className="container">
        {loading ? (
          <p>Loading categories...</p>
        ) : error ? (
          <p>{error}</p>
        ) : (
          categories.map((cat) => (
            <div key={cat.id} className="category-item">
              <h2>{cat.name}</h2>
              <ul>
                {cat.subcategories.map((sub) => (
                  <li key={sub.id}>
                    <div
                      onClick={() => navigate(`/subcategory/${sub.id}`)}
                      className="subcategory-link"
                    >
                      {sub.name}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Category;
