import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { useWatchlist } from "../../context/WatchlistContext"; // ADD THIS IMPORT
import "./Navbar.css";
import { Heart } from "lucide-react";


const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { logout, isAuthenticated, isLoading } = useAuth();
  const { watchlist } = useWatchlist(); // USE WATCHLIST CONTEXT
  const location = useLocation();

  // Get watchlist count from context instead of separate API call
  const watchlistCount = watchlist?.length;

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const closeMenu = () => setIsMenuOpen(false);
  const isActive = (path: string) =>
    location.pathname === path ? "active" : "";

  if (isLoading) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          <span className="logo-icon">⚡</span>
          AuctionHub
        </Link>

        <div className={`navbar-menu ${isMenuOpen ? "active" : ""}`}>
          <Link
            to="/"
            className={`navbar-link ${isActive("/")}`}
            onClick={closeMenu}
          >
            Home
          </Link>
          <Link
            to="/auctions"
            className={`navbar-link ${isActive("/auctions")}`}
            onClick={closeMenu}
          >
            Auctions
          </Link>
          <Link
            to="/contact"
            className={`navbar-link ${isActive("/contact")}`}
            onClick={closeMenu}
          >
            Contact
          </Link>
          <Link
            to="/category"
            className={`navbar-link ${isActive("/category")}`}
            onClick={closeMenu}
          >
            Category
          </Link>

          {!isAuthenticated ? (
            <>
              <Link
                to="/login"
                className={`navbar-link ${isActive("/login")}`}
                onClick={closeMenu}
              >
                Login
              </Link>
              <Link
                to="/register"
                className={`navbar-link ${isActive("/register")}`}
                onClick={closeMenu}
              >
                Register
              </Link>
            </>
          ) : (
            <>
              <Link
                to="/account"
                className={`navbar-link ${isActive("/account")}`}
                onClick={closeMenu}
              >
                My Account
              </Link>
              <Link
                to="/seller/dashbaord"
                className={`navbar-link ${isActive("/seller/dashbaord")}`}
              >
                Seller Activity
              </Link>
              <button
                className="btn btn-link nav-link"
                onClick={() => {
                  logout();
                  closeMenu();
                }}
              >
                Logout
              </button>
              <Link
                to="/watchlist"
                className={`navbar-link icon-link ${isActive("/watchlist")}`}
                onClick={closeMenu}
              >
                <Heart size={20} className="heart-icon" />
                {watchlistCount > 0 && (                                   
                    <span className="watchlist-count-badge">
                      {watchlistCount}
                    </span>
                )}
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;