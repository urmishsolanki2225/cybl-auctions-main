// AuctionDetails.js - Integrated with your existing API structure

import { useNavigate, useParams } from "react-router-dom";
import { useEffect, useState, useCallback, useMemo } from "react";
import { Search, Filter, X, ChevronDown, ChevronUp } from "lucide-react";
import LiveTimer from "../components/LiveTimer";
import "../styles/AuctionDetails.css";
import { publicApi } from "../api/apiUtils";
import BASE_URL from "../api/endpoints";
import WatchlistButton from "../components/WatchlistButton"; // Import the new component

const AuctionDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // State for auction data
  const [auction, setAuction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Watchlist state
  const [watchlistItems, setWatchlistItems] = useState(new Set());
  const [watchlistLoading, setWatchlistLoading] = useState(false);

  // Filter state
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [bidRange, setBidRange] = useState({ min: "", max: "" });
  const [lotStatus, setLotStatus] = useState("all");
  const [sortBy, setSortBy] = useState("closing_soon");
  const [showFilters, setShowFilters] = useState(true);

  // Debounced API call function
  const fetchAuctionData = useCallback(
    async (filters = {}) => {
      try {
        setLoading(true);
        setError(null);

        // Use your existing API with enhanced filtering
        const response = await publicApi.getAuctionDetails(id, {
          search: filters.search || "",
          categories: filters.categories || [],
          min_bid: filters.min_bid || "",
          max_bid: filters.max_bid || "",
          status: filters.status === "all" ? "" : filters.status || "",
          sort_by: filters.sort_by || "closing_soon",
        });

        setAuction(response || {});
      } catch (err) {
        console.error("Failed to load auction details", err);
        setError(err.message || "Failed to load auction details");
      } finally {
        setLoading(false);
      }
    },
    [id]
  );

  // Initial load
  useEffect(() => {
    fetchAuctionData();
  }, [fetchAuctionData]);

  // Auto-apply filters with debouncing for better performance
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      const filters = {
        search: searchTerm.trim(),
        categories: selectedCategories,
        min_bid: bidRange.min,
        max_bid: bidRange.max,
        status: lotStatus,
        sort_by: sortBy,
      };

      // Only call API if we have meaningful filters or if it's the initial load
      fetchAuctionData(filters);
    }, 300); // 300ms debounce

    return () => clearTimeout(timeoutId);
  }, [
    searchTerm,
    selectedCategories,
    bidRange,
    lotStatus,
    sortBy,
    fetchAuctionData,
  ]);

  const handleCategoryChange = (categoryId) => {
    setSelectedCategories((prev) =>
      prev.includes(categoryId)
        ? prev.filter((id) => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const clearAllFilters = () => {
    setSearchTerm("");
    setSelectedCategories([]);
    setBidRange({ min: "", max: "" });
    setLotStatus("all");
    setSortBy("closing_soon");
  };

  const handlePlaceBidClick = (lot) => {
    // Navigate to bid placement page or open bid modal
    console.log("Place bid for lot:", lot.id);
    navigate(`/lot/${lot.id}`);
  };

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let count = 0;
    if (searchTerm.trim()) count++;
    if (selectedCategories.length > 0) count++;
    if (bidRange.min || bidRange.max) count++;
    if (lotStatus !== "all") count++;
    if (sortBy !== "closing_soon") count++;
    return count;
  }, [searchTerm, selectedCategories, bidRange, lotStatus, sortBy]);

  if (error) {
    return (
      <div className="auction-details-page">
        <div className="error-container">
          <h2>Error Loading Auction</h2>
          <p>{error}</p>
          <button onClick={() => fetchAuctionData()} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!auction) {
    return (
      <div className="auction-details-page">
        <div className="no-auction">
          <p>No auction found</p>
        </div>
      </div>
    );
  }

  // Callback for when watchlist changes
  const handleWatchlistChange = (inventoryId, isAdded) => {
    console.log(
      `Item ${inventoryId} ${isAdded ? "added to" : "removed from"} watchlist`
    );
    // You can add any additional logic here, like updating UI state
  };

  return (
    <div className="auction-details-page">
      <div className="auction-header-details">
        <div>
          {auction.location_details?.company_logo && (
            <div>
              <img
                src={
                  BASE_URL + auction.location_details.company_logo ||
                  "https://demofree.sirv.com/nope-not-here.jpg"
                }
                alt="Company Logo"
                className="company-logo"
              />
              <div>{auction.location_details.name}</div>
            </div>
          )}
        </div>

        <div className="auction-details">
          <h3 className="auction-name">{auction.name}</h3>
          <div className="auction-location">
            <span className="address">
              {auction.location_details?.address},&nbsp;
              {auction.location_details?.city},&nbsp;
              {auction.location_details?.state},&nbsp;
              {auction.location_details?.country}
            </span>
            <span className="zipcode">
              Pincode: {auction.location_details?.zipcode}
            </span>
            <span className="phone">
              Phone: {auction.location_details?.phone_no}
            </span>
          </div>
          <div className="lot-count">
            <strong>{auction.lot_count}</strong> Lots Open for Bidding
          </div>
        </div>

        <div className="auction-timer">
          <div className="closing-info">
            <span className="closing-label">Begins Closing</span>
            <span className="closing-date">{auction.end_date}</span>
          </div>
          <div className="status-info">
            <span className="status-label">Status:</span>
            <span className={`status ${auction.status?.toLowerCase()}`}>
              {auction.status}
            </span>
          </div>
          <div className="timer">
            <LiveTimer endTime={auction.end_date} />
          </div>
        </div>
      </div>
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
                    {auction.categories?.map((category) => (
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
                      placeholder={`Min (${auction.bid_range?.min || 0})`}
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
                      placeholder={`Max (${auction.bid_range?.max || "Any"})`}
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
            {loading ? (
              <div className="loading-spinner"></div>
            ) : (
              <div className="lots-grid">
                {auction?.inventory_items?.map((lot) => (
                  <div className="lot-card" key={lot.id}>
                    {/* Image with watchlist button */}
                    <div className="lot-image-container">
                      <img
                        src={`${BASE_URL}/media/${lot.media_items?.[0]?.path}`}
                        alt={lot.title}
                        className="lot-image"
                      />
                      <div className="watchlist-button-container">
                        <WatchlistButton
                          inventoryId={lot.id}
                          size="small"
                          onWatchlistChange={handleWatchlistChange}
                        />
                      </div>
                    </div>

                    {/* Lot content */}
                    <div className="lot-content">
                      <div className="lot-header">
                        <h5 className="lot-title">{lot.title}</h5>
                        <div className="lot-category">
                          {lot?.category?.name}
                        </div>
                      </div>

                      <div className="lot-details">
                        <div className="lot-detail-row">
                          <span className="lot-detail-label">Current Bid:</span>
                          <span className="lot-detail-value">
                            ${lot.current_bid || lot.starting_bid}
                          </span>
                        </div>

                        <div className="lot-detail-row">
                          <span className="lot-detail-label">Next Bid:</span>
                          <span className="lot-detail-value">
                            $
                            {lot.next_required_bid ||
                              (lot.current_bid
                                ? lot.current_bid + 1
                                : lot.starting_bid)}
                          </span>
                        </div>

                        <div className="lot-detail-row">
                          <span className="lot-detail-label">High Bidder:</span>
                          <span className="lot-detail-value">
                            {lot.highest_bidder?.username || "None"}
                          </span>
                        </div>

                        <div className="lot-detail-row">
                          <span className="lot-detail-label">Reserve:</span>
                          <span
                            className={`lot-reserve ${
                              lot.reserve_met
                                ? "reserve-met"
                                : "reserve-not-met"
                            }`}
                          >
                            {lot.reserve_met ? "Met" : "Not Met"}
                          </span>
                        </div>
                      </div>

                      <div className="lot-footer">
                        <div className="lot-timer">
                          <LiveTimer endTime={lot.lot_end_time} />
                        </div>
                        <button
                          className="lot-bid-button"
                          onClick={() => handlePlaceBidClick(lot)}
                        >
                          Place Bid
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            {!loading && auction?.inventory_items?.length === 0 && (
              <div className="no-lots-message">
                No lots found matching your criteria.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default AuctionDetails;