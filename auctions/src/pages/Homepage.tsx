import { Link, useNavigate } from 'react-router-dom';
import LiveTimer from '../components/LiveTimer';
import LotsCarousel from '../components/homepage/LotsCarousel';
import '../styles/Homepage.css';
import { useEffect, useState } from 'react';
import { publicApi } from '../api/apiUtils';
import BASE_URL from '../api/endpoints';
import Banner from '../components/homepage/Banner';

const Index = () => {
  const [featuredAuction, SetFeaturedAuction] = useState<[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAuctions = async () => {
      try {
        setLoading(true);
        const response = await publicApi.getFeaturedAuctions();     
        console.log("respons",response.results)
        SetFeaturedAuction(response.results);

      } catch (err) {
        console.error('Failed to load bidding history', err);
        setError('Failed to load bidding history');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAuctions();
  }, []);

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
       <Banner/>
      </section>
      <section className="featured-section">
        <div className="container">          
          <h2 >Next Auctions to Close</h2>
          <div className="featured-auction-combined-card">
          </div>
          <h2 >Auctions by Category</h2>
          <div className="featured-auction-combined-card">
          </div>
        </div>
        <div className="container">
          <h2>Featured Auction</h2>
          {featuredAuction?.length > 0 && featuredAuction.slice(0, 6).map((auctions, index) => (
            <div className="featured-auction-combined-card" key={index}>
              <div className="auction-header">
                {/* Left - Company Info */}
                <div className="company-info">
                  <img
                    src={BASE_URL + auctions.location_details.company_logo}
                    alt="logo"
                    className="company-logo"
                  />
                  <div className="company-name" onClick={() => navigate(`/company/${auctions.location_details.id}`)}>{auctions.location_details.name}</div>

                </div>

                {/* Center - Auction Details */}
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

                {/* Right - Countdown */}
                <div className="auction-timer">
                  <div>
                    Begins Closing
                    {auctions.end_date}
                  </div>
                  <div>
                   Status :  {auctions.status}
                  </div>
                  <div>
                    <LiveTimer endTime={auctions.end_date} />
                  </div>                  
                </div>
              </div>

              {/* Divider */}
              <hr className="auction-divider" />

              {/* Carousel of Lots */}
              <div className="auction-lots">
                <LotsCarousel lots={auctions.inventory_items} auctionId={auctions.id} />
              </div>
            </div>
          ))}
        </div>
      </section>     

      {/* How It Works */}
      <section className="how-it-works">
        <div className="container">
          <h2 className="section-title">How It Works</h2>
          <div className="steps-grid">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Register & Verify</h3>
              <p>Create your account and verify your identity to start bidding</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Browse & Research</h3>
              <p>Explore our auctions and research items you're interested in</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Bid & Win</h3>
              <p>Place your bids and track auctions in real-time</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Pay & Receive</h3>
              <p>Complete payment and receive your winning items</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;