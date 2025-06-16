import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { logout, isAuthenticated, isLoading  } = useAuth();
  const location = useLocation();

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  const closeMenu = () => setIsMenuOpen(false);
  const isActive = (path: string) => (location.pathname === path ? 'active' : '');
  if (isLoading) {
      return null; // or a loading spinner
  }
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMenu}>
          <span className="logo-icon">⚡</span>
          AuctionHub
        </Link>

        <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
          <Link to="/" className={`navbar-link ${isActive('/')}`} onClick={closeMenu}>
            Home
          </Link>
          <Link to="/auctions" className={`navbar-link ${isActive('/auctions')}`} onClick={closeMenu}>
            Auctions
          </Link>
          <Link to="/contact" className={`navbar-link ${isActive('/contact')}`} onClick={closeMenu}>
            Contact
          </Link>
          <Link to="/category" className={`navbar-link ${isActive('/category')}`} onClick={closeMenu}>
            Category
          </Link>

          {!isAuthenticated ? (
            <>
              <Link to="/login" className={`navbar-link ${isActive('/login')}`} onClick={closeMenu}>
                Login
              </Link>
              <Link to="/register" className={`navbar-link ${isActive('/register')}`} onClick={closeMenu}>
                Register
              </Link>
            </>
          ) : (
            <>
              <Link to="/account" className={`navbar-link ${isActive('/account')}`} onClick={closeMenu}>
                My Account
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
            </>
          )}
        </div>

        <div className="navbar-toggle" onClick={toggleMenu}>
          <span className={`hamburger ${isMenuOpen ? 'active' : ''}`}></span>
          <span className={`hamburger ${isMenuOpen ? 'active' : ''}`}></span>
          <span className={`hamburger ${isMenuOpen ? 'active' : ''}`}></span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
