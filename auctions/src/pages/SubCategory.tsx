import { useNavigate, useParams } from "react-router-dom";
import "../styles/Category.css";
import { useEffect, useState } from "react";
import { publicApi } from "../api/apiUtils";
import BASE_URL from "../api/endpoints";

const SubCategory = () => {
  const { id } = useParams();
  const [subCategories, setSubCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSubCategory = async (id) => {
      try {
        setLoading(true);
        const response = await publicApi.getSubCategories(id);
        const sorted = sortSubCategories(response);
        setSubCategories(sorted);
      } catch (err) {
        setError("Failed to load categories");
      } finally {
        setLoading(false);
      }
    };

    fetchSubCategory(id);
  }, [id]);

  const sortSubCategories = (data: any[]) => {
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

  const handleSubcategoryClick = (subcategoryId: number) => {
    navigate("/category/lots", {
      state: {
        categoryId: subcategoryId,
      },
    });
  };

  return (
    <div className="category-page">
      <div className="container">
        {loading ? (
          <div className="loading-container">
            <p>Loading categories...</p>
          </div>
        ) : error ? (
          <div className="error-container">
            <p>{error}</p>
          </div>
        ) : (
          <div className="categories-grid">
            {subCategories.map((cat) => (
              <div key={cat.id} className="category-card">
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

export default SubCategory;
