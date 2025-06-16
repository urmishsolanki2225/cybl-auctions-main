import { useState, useRef, useEffect } from 'react';
import { Upload, User, Lock, History, CreditCard, Check } from 'lucide-react';
import ProfileDetailsTab from '../components/ProfileDetailsTab';
import PasswordChangeTab from '../components/PasswordChangeTab';
import BiddingHistoryTab from '../components/BiddingHistoryTab';
import PaymentHistoryTab from '../components/PaymentHistoryTab';
import { protectedApi } from '../api/apiUtils';
import '../styles/UserProfile.css';

interface UserData {
  username: string;
  name: string;
  first_name: string;
  last_name: string;
  email: string;
  avatar: string;
  memberSince: string;
  wonAuctions: number;
  phone_no?: string;
  address?: string;
  country?: number;
  state?: number;
  city?: string;
  zipcode?: string;
  gender?: string;
  title?: string;
  seller_type?: string;
}

const UserProfile = () => {
  const [userData, setUserData] = useState<UserData>({
    username: "",
    name: "",
    first_name: "",
    last_name: "",
    email: "",
    avatar: "/placeholder.svg",
    memberSince: "2022",
    wonAuctions: 0,
    phone_no: "",
    address: "",
    country: undefined,
    state: undefined,
    city: "",
    zipcode: "",
    gender: "",
    title: "",
  });

  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await protectedApi.getProfile(); 
        //console.log('Profile response:', response); // Debug log
        
        const profileData = {
          username: response.user.username,
          name: `${response.user.title ? response.user.title.charAt(0).toUpperCase() + response.user.title.slice(1).toLowerCase() : ''} ${response.user.first_name || ''} ${response.user.last_name || ''}`.trim(),
          first_name: response.user.first_name || '',
          last_name: response.user.last_name || '',
          email: response.user.email,
          avatar: response.user.photo || "/placeholder.svg",
          memberSince: response.user.member_since || '2022',
          wonAuctions: response.user.won_auctions || 0,
          phone_no: response.user.phone_no || '',
          address: response.user.address || '',
          country: response.user.country || undefined,
          state: response.user.state || undefined,
          city: response.user.city || '',
          zipcode: response.user.zipcode || '',
          gender: response.user.gender || '',
          title: response.user.title || '',
        };
        
        setUserData(profileData);
      } catch (err) {
        console.error("Failed to load user profile", err);
      }
    };

    fetchUserData();
  }, []);

  const handleImageClick = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  const handleImageChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setUploadError('Please select a valid image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('Image size should be less than 5MB');
      return;
    }

    try {
      setIsUploading(true);
      setUploadError(null);
      setUploadSuccess(false);

      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        const result = e.target?.result as string;
        setPreviewImage(result);
      };
      reader.readAsDataURL(file);

      // Prepare FormData
      const formData = new FormData();
      formData.append('photo', file);

      // Upload using the API utility
      const response = await protectedApi.updateProfile(formData);
      
      // Update user data with new avatar URL from API response
      setUserData(prev => ({ 
        ...prev, 
        avatar: response.user.photo || previewImage 
      }));

      setUploadSuccess(true);
      
      // Hide success badge after 3 seconds
      setTimeout(() => {
        setUploadSuccess(false);
      }, 3000);

    } catch (error: any) {
      console.error('Photo upload failed:', error);
      setUploadError(error.message || 'Failed to upload photo');
      // Reset preview on error
      setPreviewImage(null);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="profile-page">
      <div className="container">
        {/* Profile Header */}
        <div className="profile-header">
          <div className="gradient-bg"></div>
          <div className="profile-content">
            <div className="profile-main">
              {/* Avatar with Upload */}
              <div className="profile-avatar-section">
                <div 
                  className={`profile-avatar ${isUploading ? 'uploading' : ''}`} 
                  onClick={handleImageClick}
                >
                  <img 
                    src={previewImage || userData.avatar} 
                    alt={userData.name} 
                    style={{ opacity: isUploading ? 0.7 : 1 }}
                  />
                  
                  <div className="avatar-overlay">
                    {isUploading ? (
                      <div className="upload-spinner">
                        <div className="spinner"></div>
                      </div>
                    ) : (
                      <Upload className="upload-icon" />
                    )}
                  </div>

                  {/* Success Badge */}
                  {uploadSuccess && (
                    <div className="upload-success-badge">
                      <Check className="success-icon" />
                    </div>
                  )}

                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="file-input"
                    disabled={isUploading}
                  />
                </div>
                
                {/* Upload Status Messages */}
                {uploadError && (
                  <div className="upload-error">
                    {uploadError}
                  </div>
                )}
                
                {isUploading && (
                  <div className="upload-status">
                    Uploading photo...
                  </div>
                )}
              </div>

              {/* User Info */}
              <div className="profile-info">
                <div className="profile-details">
                  <h1 className="profile-name">{userData.name || userData.username}</h1>
                  <p className="profile-email">{userData.email}</p>
                  
                  {/* Stats */}
                  <div className="profile-stats">
                    <div className="stat">
                      <div className="stat-number">{userData.wonAuctions}</div>
                      <div className="stat-label">Won Auctions</div>
                    </div>
                    <div className="stat">
                      <div className="stat-number">{userData.memberSince}</div>
                      <div className="stat-label">Member Since</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Tabs */}
        <div className="tabs-container">
          <div className="tabs-list">
            <button 
              className={`tab-trigger ${activeTab === 'profile' ? 'active' : ''}`}
              onClick={() => setActiveTab('profile')}
            >
              <User className="tab-icon" />
              <span className="tab-text">Profile Details</span>
              <span className="tab-text-mobile">Profile</span>
            </button>
            <button 
              className={`tab-trigger ${activeTab === 'password' ? 'active' : ''}`}
              onClick={() => setActiveTab('password')}
            >
              <Lock className="tab-icon" />
              <span className="tab-text">Password</span>
              <span className="tab-text-mobile">Security</span>
            </button>
            <button 
              className={`tab-trigger ${activeTab === 'bidding' ? 'active' : ''}`}
              onClick={() => setActiveTab('bidding')}
            >
              <History className="tab-icon" />
              <span className="tab-text">Bidding History</span>
              <span className="tab-text-mobile">Bids</span>
            </button>
            <button 
              className={`tab-trigger ${activeTab === 'payment' ? 'active' : ''}`}
              onClick={() => setActiveTab('payment')}
            >
              <CreditCard className="tab-icon" />
              <span className="tab-text">Payment History</span>
              <span className="tab-text-mobile">Payments</span>
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'profile' && (
              <ProfileDetailsTab userData={userData} setUserData={setUserData} />
            )}
            {activeTab === 'password' && (
              <PasswordChangeTab />
            )}
            {activeTab === 'bidding' && (
              <BiddingHistoryTab />
            )}
            {activeTab === 'payment' && (
              <PaymentHistoryTab />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;