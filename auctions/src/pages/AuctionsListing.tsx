import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import LiveTimer from '../components/LiveTimer';
import LotsCarousel from '../components/homepage/LotsCarousel';
import AuctionFilters from '../components/auctions/AuctionFilters';
import { useAuctionFilters } from '../hooks/useAuctionFilters';
import '../styles/Homepage.css';
import { publicApi } from '../api/apiUtils';
import BASE_URL from '../api/endpoints';

const Index = () => {
  const [featuredAuction, setFeaturedAuction] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(true);

  const navigate = useNavigate();

  const {
    filters,
    updateFilters,
    clearFilters,
    buildApiQueryString,
    hasActiveFilters,
    filterSummary
  } = useAuctionFilters();

  const fetchAuctions = useCallback(
    async (page = 1, isInitial = false) => {
      try {
        setLoading(true);
        setError(null);

        const queryString = `${buildApiQueryString()}&page=${page}`;
        const response = await publicApi.getRunningAuctions(queryString);

        if (isInitial) {
          setFeaturedAuction(response.results || []);
        } else {
          setFeaturedAuction((prev) => [...prev, ...response.results]);
        }

        setHasNextPage(!!response.next);
        setCurrentPage(page + 1);
      } catch (err: any) {
        console.error('Failed to load auctions', err);
        setError(err.message || 'Failed to load auctions');
      } finally {
        setLoading(false);
      }
    },
    [buildApiQueryString]
  );

  useEffect(() => {
    fetchAuctions(1, true);
  }, [fetchAuctions]);

  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 &&
        !loading &&
        hasNextPage
      ) {
        fetchAuctions(currentPage);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [fetchAuctions, currentPage, loading, hasNextPage]);

  return (
    <div className="homepage">
      {/* Filters Section */}
      <section className="filters-section">
        <div className="container">
          <AuctionFilters
            filters={filters}
            onFilterChange={updateFilters}
            onClearFilters={clearFilters}
          />
        </div>
      </section>

      {/* Featured Section */}
      <section className="featured-section">
        <div className="container">
          <div className="section-header">
            <div className="section-title-area">
              <h2>Running Auctions</h2>
              {hasActiveFilters && (
                <p className="filter-summary">
                  Filtered by: {filterSummary.join(', ')}
                </p>
              )}
            </div>
            {hasActiveFilters && (
              <button className="clear-filters-btn" onClick={clearFilters}>
                Clear All Filters
              </button>
            )}
          </div>

          {loading && featuredAuction.length === 0 && (
            <div className="loading">
              <div className="loading-spinner"></div>
              <p>Loading auctions...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button onClick={() => fetchAuctions(1, true)} className="retry-btn">
                Try Again
              </button>
            </div>
          )}

          {!loading && !error && featuredAuction.length === 0 && (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h3>No auctions found</h3>
              <p>
                {hasActiveFilters
                  ? 'No auctions match your current filters. Try adjusting your search criteria.'
                  : 'There are currently no running auctions.'}
              </p>
              {hasActiveFilters && (
                <button onClick={clearFilters} className="try-again-btn">
                  Clear All Filters
                </button>
              )}
            </div>
          )}

          {!error && featuredAuction.length > 0 && (
            <>
              <div className="results-summary">
                <p>
                  Showing {featuredAuction.length} auction
                  {featuredAuction.length !== 1 ? 's' : ''}
                </p>
              </div>

              {featuredAuction.map((auction: any, index:any) => (
                <div
                  key={index}
                  className="bg-blue-600 rounded-md px-4 py-2 text-center font-medium shadow-md hover:bg-blue-700 transition-colors cursor-pointer"
                  onClick={() => navigate(`/auction/${auction.id}`)}
                >
                  <div className="featured-auction-combined-card">
                    <div className="auction-header">
                      {/* Left - Company Info */}
                      <div className="company-info">
                        <img
                          src={BASE_URL + auction.location_details.company_logo || 'https://demofree.sirv.com/nope-not-here.jpg'}
                          alt={`${auction.location_details.name} logo`}
                          className="company-logo"
                          onError={(e) => {
                            e.currentTarget.src = 'https://demofree.sirv.com/nope-not-here.jpg';
                          }}
                        />
                        <div
                          className="company-name"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/company/${auction.location_details.id}`);
                          }}
                          role="button"
                          tabIndex={0}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                              navigate(`/company/${auction.location_details.id}`);
                            }
                          }}
                        >
                          {auction.location_details.name}
                        </div>
                      </div>

                      {/* Center - Auction Details */}
                      <div className="auction-details">
                        <h3 className="auction-name">{auction.name}</h3>
                        <div className="auction-location">
                          <span className="address">
                            {auction.location_details.address},&nbsp;
                            {auction.location_details.city},&nbsp;
                            {auction.location_details.state},&nbsp;
                            {auction.location_details.country}
                          </span>
                          <span className="zipcode">
                            Pincode: {auction.location_details.zipcode}
                          </span>
                          <span className="phone">
                            Phone: {auction.location_details.phone_no}
                          </span>
                        </div>
                        <div className="lot-count">
                          <strong>{auction.lot_count}</strong> Lots Open for Bidding
                        </div>
                      </div>

                      {/* Right - Countdown */}
                      <div className="auction-timer">
                        <div className="closing-info">
                          <span className="closing-label">Begins Closing</span>
                          <span className="closing-date">{auction.end_date}</span>
                        </div>
                        <div className="status-info">
                          <span className="status-label">Status:</span>
                          <span className={`status ${auction.status.toLowerCase()}`}>
                            {auction.status}
                          </span>
                        </div>
                        <div className="timer">
                          <LiveTimer endTime={auction.end_date} />
                        </div>
                      </div>
                    </div>

                    {/* Divider */}
                    <hr className="auction-divider" />

                    {/* Carousel of Lots */}
                    <div className="auction-lots">
                      <LotsCarousel lots={auction.inventory_items} auctionId={auction.id} />
                    </div>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="loading">
                  <div className="loading-spinner"></div>
                  <p>Loading more auctions...</p>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default Index;
