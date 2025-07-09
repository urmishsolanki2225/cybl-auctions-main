import { Link, useNavigate } from "react-router-dom";
import LiveTimer from "../components/LiveTimer";
import LotsCarousel from "../components/homepage/LotsCarousel";
import "../styles/Homepage.css";
import { useEffect, useState } from "react";
import { publicApi } from "../api/apiUtils";
import BASE_URL from "../api/endpoints";
import ActiveLots from "../components/ActiveLots";
import NextToClose from "../components/NextToClose";
import CategoryAuctions from "../components/CategoryAuctions";

const Index = () => {
  const [featuredAuction, SetFeaturedAuction] = useState<[]>([]);
  const [closingSoonAuctions, setClosingSoonAuctions] = useState<[]>([]);
  const [category, setCategory] = useState<[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAuctions = async () => {
      try {
        setLoading(true);
        const response = await publicApi.getFeaturedAuctions();
        const closedAuctions = await publicApi.getNextToCloseAuctions();
        const categories = await publicApi.getCategories();
        setCategory(categories);
        SetFeaturedAuction(response.results);
        setClosingSoonAuctions(closedAuctions);
      } catch (err) {
        setLoading(false);
        console.error("Failed to load bidding history", err);
        setError("Failed to load bidding history");
      } finally {
        setLoading(false);
      }
    };

    fetchAuctions();
  }, []);

  return loading ? (
    <div className="loading-state">Loading...</div>
  ) : (
    <div className="homepage">
      <ActiveLots />
      <div className="auctions-container">
        <NextToClose auctions={closingSoonAuctions} />
        {category.length > 1 && <CategoryAuctions categories={category} /> }
        
      </div>
      {/* <section className="featured-section">
        <div className="container">
          <h2>Featured Auction</h2>
          {featuredAuction?.length > 0 &&
            featuredAuction.slice(0, 6).map((auctions, index) => (
              <div className="featured-auction-combined-card" key={index}>
                <div className="auction-header">
                  <div className="company-info">
                    <img
                      src={BASE_URL + auctions.location_details.company_logo}
                      alt="logo"
                      className="company-logo"
                    />
                    <div
                      className="company-name"
                      onClick={() =>
                        navigate(`/company/${auctions.location_details.id}`)
                      }
                    >
                      {auctions.location_details.name}
                    </div>
                  </div>
                  <div className="auction-details">
                    <h3 className="auction-name">{auctions.name}</h3>
                    <div className="auction-location">
                      <span>
                        {auctions.location_details.address},&nbsp;
                        {auctions.location_details.city},&nbsp;
                        {auctions.location_details.state},&nbsp;
                        {auctions.location_details.country}
                      </span>
                      <span>pincode: {auctions.location_details.zipcode}</span>
                    </div>
                    <span>{auctions.lot_count} Lots Open for Bidding </span>
                  </div>
                  <div className="auction-timer">
                    <div>
                      Begins Closing
                      {auctions.end_date}
                    </div>
                    <div>Status : {auctions.status}</div>
                    <div>
                      <LiveTimer endTime={auctions.end_date} />
                    </div>
                    <span className="mt-2">
                      <button
                        className="bid-btn"
                        onClick={() => navigate(`/auction/${auctions.id}`)}
                      >
                        View Details{" "}
                      </button>
                    </span>
                  </div>
                </div>
                <hr className="auction-divider" />
                <div className="auction-lots">
                  <LotsCarousel
                    lots={auctions.inventory_items}
                    auctionId={auctions.id}
                  />
                </div>
              </div>
            ))}
        </div>
      </section> */}
    </div>
  );
};

export default Index;
