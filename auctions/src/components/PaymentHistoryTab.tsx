import { useEffect, useState } from 'react';
import { CreditCard, Download, Eye, Clock, CheckCircle } from 'lucide-react';
import '../styles/PaymentHistoryTab.css';
import { protectedApi, publicApi } from '../api/apiUtils';

interface PaymentHistoryItem {
  payment_id: number;
  transaction_id: string;
  lot_name: string;
  lot_image: string;
  lot_id: number;
  auction_name: string;
  auction_id: number;
  price: string;
  status: string;
  status_display: string;
  payment_method: string;
  payment_method_display: string;
  date: string;
  updated_date: string;
  payment_status_filter: string;
  inventory_number: string;
  lot_condition: string;
}

interface ApiResponse {
  success: boolean;
  data: PaymentHistoryItem[];
  counts: {
    all: number;
    pending: number;
    paid: number;
  };
  current_tab: string;
  total_items: number;
}

const PaymentHistoryTab = () => {
  const [paymentHistory, setPaymentHistory] = useState<PaymentHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [counts, setCounts] = useState({ all: 0, pending: 0, paid: 0 });
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchPaymentHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const response: ApiResponse = await protectedApi.getUsersPaymentHistory();
        
        if (response.success) {
          setPaymentHistory(response.data);
          setCounts(response.counts);
        } else {
          setError('Failed to fetch payment history');
        }
      } catch (err) {
        console.error('Failed to load payment history', err);
        setError('Failed to load payment history. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPaymentHistory();
  }, []);

  const filteredPayments = (status: string) => {
    if (status === 'all') return paymentHistory;
    return paymentHistory.filter(item => item.payment_status_filter === status);
  };

  const getStatusIcon = (status: string) => {
    const normalizedStatus = status.toLowerCase();
    return normalizedStatus === 'paid' || normalizedStatus === 'completed' 
      ? <CheckCircle className="w-4 h-4" /> 
      : <Clock className="w-4 h-4" />;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatAmount = (price: string) => {
    return parseFloat(price).toLocaleString();
  };

  const PaymentRow = ({ payment }: { payment: PaymentHistoryItem }) => (
    <div className="payment-card">
      <div className="payment-card-content">
        <div className="payment-item-title">
          <h3>{payment.lot_name}</h3>
          <p className="payment-method">{payment.payment_method_display}</p>
          <p className="auction-name">{payment.auction_name}</p>
        </div>
        
        <div className="payment-amount">
          <p className="payment-label">Amount</p>
          <p className="payment-value amount">${formatAmount(payment.price)}</p>
        </div>
        
        <div className="payment-date">
          <p className="payment-label">Date</p>
          <p className="payment-value">{formatDate(payment.date)}</p>
        </div>
        
        <div className="payment-transaction">
          <p className="payment-label">Transaction ID</p>
          <p className="payment-value transaction-id">{payment.transaction_id}</p>
        </div>
        
        <div className="payment-actions">
          <div className={`payment-status ${payment.payment_status_filter}`}>
            {getStatusIcon(payment.status)}
            {payment.status_display}
          </div>
          
          <div className="payment-buttons">
            {payment.payment_status_filter === 'pending' ? (
              <button className="btn btn-primary">
                <CreditCard className="w-4 h-4" />
                Pay Now
              </button>
            ) : (
              <>
                <button className="btn btn-outline">
                  <Eye className="w-4 h-4" />
                  View
                </button>
                <button className="btn btn-outline">
                  <Download className="w-4 h-4" />
                  Receipt
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const EmptyState = ({ status }: { status: string }) => (
    <div className="empty-state">
      <div className="empty-icon">
        {status === 'pending' ? '⏳' : status === 'paid' ? '✅' : '💳'}
      </div>
      <h3>No {status} payments found</h3>
      <p>You don't have any {status} payments at the moment.</p>
    </div>
  );

  const LoadingState = () => (
    <div className="loading-state">
      <div className="loading-spinner">
        <div className="spinner"></div>
      </div>
      <p>Loading payment history...</p>
    </div>
  );

  const ErrorState = ({ message }: { message: string }) => (
    <div className="error-state">
      <div className="error-icon">❌</div>
      <h3>Error</h3>
      <p>{message}</p>
      <button 
        className="btn btn-primary"
        onClick={() => window.location.reload()}
      >
        Retry
      </button>
    </div>
  );

  const calculateTotals = () => {
    const pending = filteredPayments('pending').reduce((sum, p) => sum + parseFloat(p.price), 0);
    const paid = filteredPayments('paid').reduce((sum, p) => sum + parseFloat(p.price), 0);
    return { pending, paid };
  };

  const { pending: totalPending, paid: totalPaid } = calculateTotals();

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="payment-history-tab">
      <div className="profile-card">
        <div className="profile-card-header">
          <h2 className="profile-card-title">Payment History</h2>
          <div className="payment-summary">
            <div className="summary-card pending">
              <p className="summary-label">Total Pending</p>
              <p className="summary-amount">${totalPending.toLocaleString()}</p>
            </div>
            <div className="summary-card paid">
              <p className="summary-label">Total Paid</p>
              <p className="summary-amount">${totalPaid.toLocaleString()}</p>
            </div>
          </div>
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
                className={`tab-button ${activeTab === 'pending' ? 'active' : ''}`}
                onClick={() => setActiveTab('pending')}
              >
                Pending ({counts.pending})
              </button>
              <button 
                className={`tab-button ${activeTab === 'paid' ? 'active' : ''}`}
                onClick={() => setActiveTab('paid')}
              >
                Paid ({counts.paid})
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'all' && (
                filteredPayments('all').length > 0 ? (
                  <div className="payment-list">
                    {filteredPayments('all').map((payment) => (
                      <PaymentRow key={payment.payment_id} payment={payment} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="all" />
                )
              )}
              
              {activeTab === 'pending' && (
                filteredPayments('pending').length > 0 ? (
                  <div className="payment-list">
                    {filteredPayments('pending').map((payment) => (
                      <PaymentRow key={payment.payment_id} payment={payment} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="pending" />
                )
              )}
              
              {activeTab === 'paid' && (
                filteredPayments('paid').length > 0 ? (
                  <div className="payment-list">
                    {filteredPayments('paid').map((payment) => (
                      <PaymentRow key={payment.payment_id} payment={payment} />
                    ))}
                  </div>
                ) : (
                  <EmptyState status="paid" />
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentHistoryTab;