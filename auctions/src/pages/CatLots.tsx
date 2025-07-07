// AuctionDetails.js - Enhanced to handle both auction and category views
import {
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import { useEffect, useState, useCallback, useMemo } from "react";
import { Search, Filter, X, ChevronDown, ChevronUp } from "lucide-react";
import SmallTimer from "../components/SmallTimer";
import "../styles/AuctionDetails.css";
import { publicApi } from "../api/apiUtils";
import BASE_URL from "../api/endpoints";
import WatchlistButton from "../components/WatchlistButton"; 

const CatLots = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const categoryId = location.state?.categoryId;

  // Determine if this is a category view
  const isCategoryView = Boolean(categoryId);

  // State for data - separated into static data and lots
  const [staticData, setStaticData] = useState(null); // Categories, auction info, etc.
  const [lots, setLots] = useState([]); // Only the lots/inventory items
  const [loading, setLoading] = useState(true);
  const [lotsLoading, setLotsLoading] = useState(false); // Separate loading for lots only
  const [error, setError] = useState(null);

  // Filter state
  const [searchTerm, setSearchTerm] = useState("");
  // Initialize selectedCategories properly based on categoryId from state
  const [selectedCategories, setSelectedCategories] = useState(
    categoryId ? [categoryId.toString()] : []
  );
  const [bidRange, setBidRange] = useState({ min: "", max: "" });
  const [lotStatus, setLotStatus] = useState("all");
  const [sortBy, setSortBy] = useState("closing_soon");
  const [showFilters, setShowFilters] = useState(true);

  // Initial data fetch - loads static data and categories
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      let response;

      // If we have a categoryId from state, fetch category-specific data
      if (categoryId) {
        // Fetch initial category data - you might need to adjust this based on your API
        response = await publicApi.getCategoryLots([categoryId.toString()], {
          page_size: 0, // Just get metadata, not actual lots
        });
      } else {
        // Fetch general auction data or handle non-category view
        // You'll need to implement this based on your requirements
        response = { categories: [], inventory_items: [] };
      }

      if (response) {
        // Separate static data from lots
        const { inventory_items, ...staticInfo } = response;
        setStaticData(staticInfo);
        // Don't set lots here, let fetchFilteredLots handle it
      }
    } catch (err) {
      console.error("Failed to load initial data", err);
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  // Fetch filtered lots
  const fetchFilteredLots = useCallback(
    async (filters = {}) => {
      try {
        setLotsLoading(true);

        let response;

        // Always call the API, but pass selectedCategories as is
        // If selectedCategories is empty, the API function will handle it by not adding category_id param
        response = await publicApi.getCategoryLots(selectedCategories, {
          search: filters.search || "",
          min_bid: filters.min_bid || "",
          max_bid: filters.max_bid || "",
          status: filters.status === "all" ? "" : filters.status || "",
          sort_by: filters.sort_by || "closing_soon",
        });

        setLots(response.inventory_items || []);
      } catch (err) {
        console.error("Failed to load filtered lots", err);
        setLots([]); // Set empty array on error
      } finally {
        setLotsLoading(false);
      }
    },
    [selectedCategories]
  );

  // Initial load
  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // Filter changes effect
  useEffect(() => {
    if (!staticData) return;

    const timeoutId = setTimeout(() => {
      fetchFilteredLots({
        search: searchTerm.trim(),
        min_bid: bidRange.min,
        max_bid: bidRange.max,
        status: lotStatus,
        sort_by: sortBy,
      });
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [
    searchTerm,
    selectedCategories,
    bidRange,
    lotStatus,
    sortBy,
    fetchFilteredLots,
    staticData,
  ]);

  const handleCategoryChange = (categoryId) => {
    const categoryIdStr = categoryId.toString();

    setSelectedCategories((prev) => {
      // Check if the category is already selected
      const isSelected = prev.includes(categoryIdStr);

      // Always allow toggling - remove the restriction for main category
      return isSelected
        ? prev.filter((id) => id !== categoryIdStr) // Remove if selected
        : [...prev, categoryIdStr]; // Add if not selected
    });
  };

  const clearAllFilters = () => {
    setSearchTerm("");
    // Clear all categories, including the initial category from state
    setSelectedCategories([]);
    setBidRange({ min: "", max: "" });
    setLotStatus("all");
    setSortBy("closing_soon");
  };

  const handlePlaceBidClick = (lot) => {
    navigate(`/lot/${lot.id}`);
  };

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (searchTerm.trim()) count++;
    // Count any selected categories as a filter
    if (selectedCategories.length > 0) count++;
    if (bidRange.min || bidRange.max) count++;
    if (lotStatus !== "all") count++;
    if (sortBy !== "closing_soon") count++;
    return count;
  }, [searchTerm, selectedCategories, bidRange, lotStatus, sortBy]);

  if (loading) {
    return (
      <div className="loading-state">Loading...</div>
    );
  }

  if (error) {
    return (
      <div className="auction-details-page">
        <div className="error-container">
          <h2>Error Loading Data</h2>
          <p>{error}</p>
          <button onClick={() => fetchInitialData()} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!staticData) {
    return (
      <div className="auction-details-page">
        <div className="no-data">
          <p>No data found</p>
        </div>
      </div>
    );
  }

  // Get page title based on view type
  const getPageTitle = () => {
    if (isCategoryView) {
      return staticData.category_info?.name || "Category Lots";
    }
    return "Lots";
  };

  // Function to get image URL or placeholder
  const getImageUrl = (mediaItem) => {
    if (mediaItem && mediaItem.path) {
      // Assuming you have a base URL for images
      return `${BASE_URL}/media/${mediaItem.path}`;
    }
    return null;
  };

  // Function to determine if reserve is met
  const isReserveMet = (currentBid, reservePrice) => {
    return parseFloat(currentBid) >= parseFloat(reservePrice);
  };

  return (
    <div className="auction-details-page auctions-container">
      <div className="auction-layout-page">
        {/* Left-side filter or info section */}
        <aside className="left-panel">
          <div className="filter-card">
            <div className="filter-header">
              <h4 className="filter-title">
                <Filter className="filter-icon" />
                Filter Lots
                {activeFiltersCount > 0 && (
                  <span className="active-filters-badge">
                    {activeFiltersCount}
                  </span>
                )}
              </h4>
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="toggle-filters-btn"
              >
                {showFilters ? <ChevronUp /> : <ChevronDown />}
              </button>
            </div>

            {showFilters && (
              <div className="filter-content">
                {/* Search */}
                <div className="filter-group">
                  <label className="filter-label">Search Lots</label>
                  <div className="search-input-wrapper">
                    <Search className="search-icon" />
                    <input
                      type="text"
                      placeholder="Search by title, description..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="search-input"
                    />
                    {searchTerm && (
                      <button
                        onClick={() => setSearchTerm("")}
                        className="clear-search-btn"
                      >
                        <X />
                      </button>
                    )}
                  </div>
                </div>

                {/* Categories */}
                <div className="filter-group">
                  <label className="filter-label">
                    Categories ({selectedCategories.length} selected)
                  </label>
                  <div className="categories-list">
                    {staticData.categories?.map((category) => (
                      <label key={category.id} className="category-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedCategories.includes(
                            category.id.toString()
                          )}
                          onChange={() =>
                            handleCategoryChange(category.id.toString())
                          }
                        />
                        <span>{category.name}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Bid Range */}
                <div className="filter-group">
                  <label className="filter-label">Current Bid Range ($)</label>
                  <div className="bid-range-inputs">
                    <input
                      type="number"
                      placeholder={`Min (${staticData.bid_range?.min || 0})`}
                      value={bidRange.min}
                      onChange={(e) =>
                        setBidRange((prev) => ({
                          ...prev,
                          min: e.target.value,
                        }))
                      }
                      className="bid-input"
                    />
                    <input
                      type="number"
                      placeholder={`Max (${
                        staticData.bid_range?.max || "Any"
                      })`}
                      value={bidRange.max}
                      onChange={(e) =>
                        setBidRange((prev) => ({
                          ...prev,
                          max: e.target.value,
                        }))
                      }
                      className="bid-input"
                    />
                  </div>
                </div>

                {/* Status */}
                <div className="filter-group">
                  <label className="filter-label">Lot Status</label>
                  <select
                    value={lotStatus}
                    onChange={(e) => setLotStatus(e.target.value)}
                    className="status-select"
                  >
                    <option value="all">All Lots</option>
                    <option value="open">Open Lots Only</option>
                    <option value="closed">Closed Lots Only</option>
                  </select>
                </div>

                {/* Sort By */}
                <div className="filter-group">
                  <label className="filter-label">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="sort-select"
                  >
                    <option value="closing_soon">Closing Soon</option>
                    <option value="lowest_bid">Lowest Bid First</option>
                    <option value="highest_bid">Highest Bid First</option>
                    <option value="title_asc">Title A-Z</option>
                    <option value="title_desc">Title Z-A</option>
                  </select>
                </div>

                {/* Clear Filters */}
                {activeFiltersCount > 0 && (
                  <button
                    onClick={clearAllFilters}
                    className="clear-filters-btn"
                  >
                    <X className="clear-icon" />
                    Clear All Filters
                  </button>
                )}
              </div>
            )}
          </div>
        </aside>

        {/* Right-side auction content */}
        <section className="right-panel">
          <div className="lots-container">
            {lotsLoading ? (
              <div className="loading-state"></div>
            ) : (
              <div className="lots-grid">
                {lots?.map((lot, index) => (
                  <div key={lot.id || index} className="lot-cards">
                    {/* Car Image Section */}
                    <div className="car-image-container">
                    <div className="watchlist-button-container">
                    <WatchlistButton
                        inventoryId={lot?.id}
                        size="small"
                        //onWatchlistChange={handleWatchlistChange}
                    />
                    </div>
                      {getImageUrl(lot.media_items) ? (
                        <img 
                          src={getImageUrl(lot.media_items)} 
                          alt={lot.title}
                          className="car-image"
                        />
                      ) : (
                        <div className="no-image-placeholder">
                          🚗
                        </div>
                      )}
                      
                      {/* Featured badge */}
                      {lot.auction_details?.is_featured && (
                        <div className="featured-badge">Featured</div>
                      )}
                      
                      {/* Condition badge */}
                      <div className={`condition-badge ${lot.condition === 'new' ? 'condition-new' : 'condition-used'}`}>
                        {lot.condition}
                      </div>
                      {/* Timer overlay */}
                      <div className="timer-overlay">
                        <div className="timer-info">
                          <div className="timer-icon">⏱</div>
                          <div className="timer-text"><SmallTimer endTime={lot.lot_end_time} /></div>
                        </div>
                        <div className="bid-info">
                          <div className="bid-label">Bid</div>
                          <div className="bid-amount">${parseFloat(lot.next_required_bid).toLocaleString()}</div>
                        </div>
                      </div>
                    </div>

                    {/* Card Content */}
                    <div className="card-content">
                      <h2 className="car-title">{lot.title}</h2>
                      
                      {/* Car details */}
                      <div className="car-details">
                        {/* <div className="car-detail">
                          <span>Category:</span>
                          <span>{lot.category_details?.category_name}</span>
                        </div> */}
                        {/* <div className="car-detail">
                          <span>Reserve:</span>
                          <span>${parseFloat(lot.reserve_price).toLocaleString()}</span>
                        </div> */}
                      </div>
                      
                      {/* <div className="car-spec">
                        {lot.description?.replace(/<[^>]*>/g, '') || 'No description available'}
                      </div> */}
                      
                      <div className="car-location">
                        {lot.auction_details?.name}
                      </div>

                      {/* Bid section */}
                      <div className="bid-section">
                        <div className="current-bid">
                          <div className="current-bid-label">Current Bid</div>
                          <div className="current-bid-amount">${parseFloat(lot.current_bid).toLocaleString()}</div>
                        </div>
                        <button className="place-bid-btn" onClick={()=> navigate(`/lot/${lot.id}`)}>
                          Place Bid
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default CatLots;
