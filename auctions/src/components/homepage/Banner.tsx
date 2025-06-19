import React from 'react';
import { Link } from 'react-router-dom';

const Banner: React.FC = () => {
    return (
        <div className="hero-content">
            <div>
                <h1 className="hero-title">
                    Discover Unique Items at
                    <span className="hero-highlight"> AuctionHub</span>
                </h1>
                <p className="hero-subtitle">
                    Join thousands of bidders in exciting live auctions. Find rare collectibles,
                    vintage items, and exclusive pieces from around the world.
                </p>
                <div className="hero-actions">
                    <Link to="/auctions" className="btn btn-primary btn-lg">
                        Browse Auctions
                    </Link>
                    {/*<Link to="/register" className="btn btn-secondary btn-lg">
                        Start Bidding
                    </Link>*/}
                </div>
            </div>
            <div className="hero-image">
                <img src="https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=600&h=400&fit=crop" alt="Auction House" />
            </div>
        </div>
    );
};

export default Banner;
