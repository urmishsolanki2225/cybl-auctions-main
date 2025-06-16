import { useEffect, useState } from 'react';
import { Clock, DollarSign, Trophy, X } from 'lucide-react';
import '../styles/BiddingHistoryTab.css';
import { protectedApi, publicApi } from '../api/apiUtils';
import BASE_URL from '../api/endpoints'

interface BiddingHistoryItem {
  inventory_id: number;
  inventory_title: string;
  inventory_first_image: string;
  auction_name: string;
  highest_bid: string;
  my_last_bid: string;
  lot_end_time: string;
  bid_status: 'active' | 'won' | 'lost';
  is_winning: boolean;
  reserve_met: boolean;
  total_bids_by_me: number;
  last_bid_time: string;
  starting_bid: string;
  reserve_price: string;
}

interface ApiResponse {
  success: boolean;
  data: BiddingHistoryItem[];
  counts: {
    all: number;
    won: number;
    lost: number;
    active: number;
  };
  current_tab: string;
  total_items: number;
}

const BiddingHistoryTab = () => {
  const [biddingHistory, setBiddingHistory] = useState<BiddingHistoryItem[]>([]);
  const [counts, setCounts] = useState({
    all: 0,
    won: 0,
    lost: 0,
    active: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchBids = async () => {
      try {
        setLoading(true);
        const response = await protectedApi.getUsersBids();
        
        if (response.success) {
          setBiddingHistory(response.data);
          setCounts(response.counts);
        } else {
          setError('Failed to load bidding history');
        }
      } catch (err) {
        console.error('Failed to load bidding history', err);
        setError('Failed to load bidding history');
      } finally {
        setLoading(false);
      }
    };
    
    fetchBids();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Clock className="w-4 h-4" />;
      case 'won':
        return <Trophy className="w-4 h-4" />;
      case 'lost':
        return <X className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const filteredHistory = (status: string) => 
    biddingHistory.filter(item => status === 'all' || item.bid_status === status);

  const BiddingCard = ({ item }: { item: BiddingHistoryItem }) => (
    <div className={`bidding-card ${item.bid_status}`}>
      <div className="bidding-image">
        <img src={BASE_URL + '/media/'+ item.inventory_first_image} alt={item.inventory_title} />
        <div className={`status-badge ${item.bid_status}`}>
          {getStatusIcon(item.bid_status)}
          {item.bid_status.charAt(0).toUpperCase() + item.bid_status.slice(1)}
        </div>
      </div>
      <div className="bidding-content">
        <h3 className="bidding-title">{item.inventory_title}</h3>
        <p className="auction-name">{item.auction_name}</p>
        
        <div className="bidding-details">
          <div className="bid-info">
            <span className="bid-label">Current Bid</span>
            <span className="bid-amount">${parseFloat(item.highest_bid).toLocaleString()}</span>
          </div>
          <div className="bid-info">
            <span className="bid-label">My Bid</span>
            <span className="bid-amount my-bid">${parseFloat(item.my_last_bid).toLocaleString()}</span>
          </div>
        </div>

        <div className="end-time">
          <span className="bid-label">End Time</span>
          <span className="end-time-value">{new Date(item.lot_end_time).toLocaleString()}</span>
        </div>

        {item.bid_status === 'active' && (
          <div className="bidding-actions">
            <button className="btn btn-primary">
              <DollarSign className="w-4 h-4" />
              Increase Bid
            </button>
            <button className="btn btn-outline">
              Watch
            </button>
          </div>
        )}

        {item.bid_status === 'won' && item.is_winning && (
          <div className="winning-badge">
            <Trophy className="w-4 h-4" />
            Winning Bid
          </div>
        )}
      </div>
    </div>
  );

  const EmptyState = ({ status }: { status: string }) => (
    <div className="empty-state">
      <div className="empty-icon">
        {status === 'active' ? '⏰' : status === 'won' ? '🏆' : status === 'lost' ? '😔' : '📦'}
      </div>
      <h3>No {status === 'all' ? '' : status} lots found</h3>
      <p>You don't have any {status === 'all' ? '' : status} auction lots at the moment.</p>
    </div>
  );

  if (loading) {
    return (
      <div className="bidding-history-tab">
        <div className="profile-card">
          <div className="profile-card-header">
            <h2 className="profile-card-title">Bidding History</h2>
          </div>
          <div className="profile-card-content">
            <div className="loading-state">Loading your bidding history...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bidding-history-tab">
        <div className="profile-card">
          <div className="profile-card-header">
            <h2 className="profile-card-title">Bidding History</h2>
          </div>
          <div className="profile-card-content">
            <div className="error-state">
              <p>{error}</p>
              <button 
                className="btn btn-primary" 
                onClick={() => window.location.reload()}
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bidding-history-tab">
      <div className="profile-card">
        <div className="profile-card-header">
          <h2 className="profile-card-title">Bidding History</h2>
        </div>
        <div className="profile-card-content">
          <div className="custom-tabs">
            <div className="tab-list">
              <button 
                className={`tab-button ${activeTab === 'all' ? 'active' : ''}`}
                onClick={() => setActiveTab('all')}
              >
                All ({counts.all})
              </button>
              <button 
                className={`tab-button ${activeTab === 'active' ? 'active' : ''}`}
                onClick={() => setActiveTab('active')}
              >
                Active ({counts.active})
              </button>
              <button 
                className={`tab-button ${activeTab === 'won' ? 'active' : ''}`}
                onClick={() => setActiveTab('won')}
              >
                Won ({counts.won})
              </button>
              <button 
                className={`tab-button ${activeTab === 'lost' ? 'active' : ''}`}
                onClick={() => setActiveTab('lost')}
              >
                Lost ({counts.lost})
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'all' && (
                biddingHistory.length > 0 ? (
                  <div className="bidding-grid">
                    {biddingHistory.map((item) => (
                      <BiddingCard key={item.inventory_id} item={item} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="all" />
                )
              )}
              
              {activeTab === 'active' && (
                filteredHistory('active').length > 0 ? (
                  <div className="bidding-grid">
                    {filteredHistory('active').map((item) => (
                      <BiddingCard key={item.inventory_id} item={item} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="active" />
                )
              )}
              
              {activeTab === 'won' && (
                filteredHistory('won').length > 0 ? (
                  <div className="bidding-grid">
                    {filteredHistory('won').map((item) => (
                      <BiddingCard key={item.inventory_id} item={item} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="won" />
                )
              )}
              
              {activeTab === 'lost' && (
                filteredHistory('lost').length > 0 ? (
                  <div className="bidding-grid">
                    {filteredHistory('lost').map((item) => (
                      <BiddingCard key={item.inventory_id} item={item} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="lost" />
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BiddingHistoryTab;