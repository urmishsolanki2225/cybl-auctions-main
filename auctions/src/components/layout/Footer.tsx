import { Link } from 'react-router-dom';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        {/*<div className="footer-content">
          
          <div className="footer-section">
            <h3 className="footer-title">AuctionHub</h3>
            <p className="footer-text">
              Your premier destination for online auctions. Discover unique items and bid with confidence.
            </p>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-subtitle">Quick Links</h4>
            <ul className="footer-links">
              <li><Link to="/">Home</Link></li>
              <li><Link to="/auctions">Auctions</Link></li>
              <li><Link to="/contact">Contact</Link></li>
              <li><Link to="/profile">Profile</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-subtitle">Categories</h4>
            <ul className="footer-links">
              <li><Link to="/category/art">Art & Collectibles</Link></li>
              <li><Link to="/category/electronics">Electronics</Link></li>
              <li><Link to="/category/jewelry">Jewelry</Link></li>
              <li><Link to="/category/vehicles">Vehicles</Link></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4 className="footer-subtitle">Support</h4>
            <ul className="footer-links">
              <li><Link to="/help">Help Center</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/security">Security</Link></li>
            </ul>
          </div>
        </div>*/}
        
        <div className="">
          <center><p>&copy; 2025 AuctionHub. All rights reserved.</p></center>
          {/*<div className="footer-social">
            <a href="#" className="social-link">Facebook</a>
            <a href="#" className="social-link">Twitter</a>
            <a href="#" className="social-link">Instagram</a>
          </div>*/}
        </div>
      </div>
    </footer>
  );
};

export default Footer;