import { useEffect, useState } from 'react';
import { Save, Edit } from 'lucide-react';
import { protectedApi, publicApi } from '../api/apiUtils';
import '../styles/ProfileDetailsTab.css';
import { toast } from 'react-toastify';

interface Country {
  id: number;
  name: string;
}
interface State {
  id: number;
  name: string;
}

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

interface ValidationErrors {
  title?: string;
  first_name?: string;
  last_name?: string;
  gender?: string;
  email?: string;
  phone_no?: string;
  address?: string;
  country?: string;
  state?: string;
  city?: string;
  zipcode?: string;
}

interface ProfileDetailsTabProps {
  userData: UserData;
  setUserData: (data: UserData) => void;
}

const ProfileDetailsTab = ({ userData, setUserData }: ProfileDetailsTabProps) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<UserData>(userData);
  const [countries, setCountries] = useState<Country[]>([]);
  const [states, setStates] = useState<State[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  useEffect(() => {
    setFormData(userData);
  }, [userData]);

  useEffect(() => {
    fetchCountries();
  }, []);

  useEffect(() => {
    if (formData.country) {
      fetchStates(formData.country);
    } else {
      setStates([]);
      // Reset state when country changes
      setFormData(prev => ({ ...prev, state: undefined }));
    }
  }, [formData.country]);

  const fetchCountries = async () => {
    try {
      const response = await publicApi.getCountries();
      setCountries(response);
    } catch (err) {
      console.error('Failed to load countries', err);
    }
  };

  const fetchStates = async (countryId: number) => {
    try {
      const response = await publicApi.getStatesByCountry(countryId);
      setStates(response);
    } catch (err) {
      console.error('Failed to load states', err);
      setStates([]);
    }
  };

  const validateForm = (): boolean => {
    const errors: ValidationErrors = {};

    // Validate title
    if (!formData.title || formData.title.trim() === '') {
      errors.title = 'Title is required';
    }

    // Validate first name
    if (!formData.first_name || formData.first_name.trim() === '') {
      errors.first_name = 'First name is required';
    }

    // Validate last name
    if (!formData.last_name || formData.last_name.trim() === '') {
      errors.last_name = 'Last name is required';
    }

    // Validate gender
    if (!formData.gender || formData.gender.trim() === '') {
      errors.gender = 'Gender is required';
    }

    // Validate email
    if (!formData.email || formData.email.trim() === '') {
      errors.email = 'Email address is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // Validate phone number
    if (!formData.phone_no || formData.phone_no.trim() === '') {
      errors.phone_no = 'Phone number is required';
    }

    // Validate address
    if (!formData.address || formData.address.trim() === '') {
      errors.address = 'Address is required';
    }

    // Validate country
    if (!formData.country) {
      errors.country = 'Country is required';
    }

    // Validate state
    if (!formData.state) {
      errors.state = 'State is required';
    }

    // Validate city
    if (!formData.city || formData.city.trim() === '') {
      errors.city = 'City is required';
    }

    // Validate zipcode
    if (!formData.zipcode || formData.zipcode.trim() === '') {
      errors.zipcode = 'Zipcode is required';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = async () => {
    // Validate form before saving
    if (!validateForm()) {
      setSaveError('Please fill in all required fields');
      return;
    }

    try {
      setIsLoading(true);
      setSaveError(null);

      // Prepare data for API
      const updateData = {
        name: formData.name,
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim(),
        phone_no: formData.phone_no?.trim(),
        address: formData.address?.trim(),
        country: formData.country,
        state: formData.state,
        city: formData.city?.trim(),
        zipcode: formData.zipcode?.trim(),
        gender: formData.gender,
        title: formData.title,
      };

      console.log('Sending update data:', updateData);

      const response = await protectedApi.updateProfile(updateData);
      console.log('Update response:', response);

      // Update the parent state with the response data
      if (response && response.user) {
        const updatedUserData = {
          username: response.user.username,
          name: `${response.user.first_name || ''} ${response.user.last_name || ''}`.trim(),
          first_name: response.user.first_name || '',
          last_name: response.user.last_name || '',
          email: response.user.email,
          avatar: response.user.photo || userData.avatar,
          memberSince: userData.memberSince,
          wonAuctions: userData.wonAuctions,
          phone_no: response.user.phone_no || '',
          address: response.user.address || '',
          country: response.user.country || undefined,
          state: response.user.state || undefined,
          city: response.user.city || '',
          zipcode: response.user.zipcode || '',
          gender: response.user.gender || '',
          title: response.user.title || '',
        };

        setUserData(updatedUserData);
        setFormData(updatedUserData);
      }

      setIsEditing(false);
      setValidationErrors({});
      toast.success(`Profile updated Successfully`);
    } catch (err: any) {
      console.error('Failed to update profile', err);
      setSaveError(err.response?.data?.detail || err.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData(userData);
    setIsEditing(false);
    setSaveError(null);
    setValidationErrors({});
  };

  const handleFieldChange = (field: keyof UserData, value: string | number | undefined) => {
    setFormData({
      ...formData,
      [field]: value
    });

    // Clear validation error for this field when user starts typing
    if (validationErrors[field as keyof ValidationErrors]) {
      setValidationErrors({
        ...validationErrors,
        [field]: undefined
      });
    }
  };

  const getFieldClassName = (fieldName: keyof ValidationErrors, baseClass: string = 'form-input') => {
    const classes = [baseClass];
    if (!isEditing) {
      classes.push('form-input-disabled');
    }
    if (validationErrors[fieldName]) {
      classes.push('form-input-error');
    }
    return classes.join(' ');
  };

  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <h2 className="profile-card-title">Profile Details</h2>
        <button
          className={`btn ${isEditing ? 'btn-outline' : 'btn-primary'}`}
          onClick={() => (isEditing ? handleCancel() : setIsEditing(true))}
        >
          <Edit className="btn-icon" />
          {isEditing ? 'Cancel' : 'Edit Profile'}
        </button>
      </div>

      <div className="profile-card-content">
        {saveError && (
          <div className="error-message" style={{ 
            color: '#dc3545', 
            backgroundColor: '#f8d7da', 
            border: '1px solid #f5c6cb', 
            padding: '12px', 
            borderRadius: '4px', 
            marginBottom: '20px' 
          }}>
            {saveError}
          </div>
        )}
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="title">
              Title <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <select
              id="title"
              value={formData.title || ''}
              onChange={(e) => handleFieldChange('title', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('title')}
            >
              <option value="">Choose Title</option>
              <option value="mr">Mr.</option>
              <option value="ms">Ms.</option>
              <option value="other">Other</option>
            </select>
            {validationErrors.title && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.title}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="first_name">
              First Name <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="first_name"
              type="text"
              value={formData.first_name}
              onChange={(e) => handleFieldChange('first_name', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('first_name')}
            />
            {validationErrors.first_name && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.first_name}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="last_name">
              Last Name <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="last_name"
              type="text"
              value={formData.last_name}
              onChange={(e) => handleFieldChange('last_name', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('last_name')}
            />
            {validationErrors.last_name && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.last_name}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="gender">
              Gender <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <select
              id="gender"
              value={formData.gender || ''}
              onChange={(e) => handleFieldChange('gender', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('gender')}
            >
              <option value="">Select Gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
            {validationErrors.gender && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.gender}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="email">
              Email Address <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => handleFieldChange('email', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('email')}
            />
            {validationErrors.email && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.email}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="phone">
              Phone Number <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="phone"
              type="text"
              value={formData.phone_no || ''}
              onChange={(e) => handleFieldChange('phone_no', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('phone_no')}
            />
            {validationErrors.phone_no && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.phone_no}
              </span>
            )}
          </div>
        </div>
        <div className="form-group form-group-full">
          <label htmlFor="address">
            Address <span style={{ color: '#dc3545' }}>*</span>
          </label>
          <input
            id="address"
            type="text"
            value={formData.address || ''}
            onChange={(e) => handleFieldChange('address', e.target.value)}
            disabled={!isEditing}
            className={getFieldClassName('address')}
          />
          {validationErrors.address && (
            <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
              {validationErrors.address}
            </span>
          )}
        </div>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="country">
              Country <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <select
              id="country"
              value={formData.country || ''}
              onChange={(e) => {
                const countryId = Number(e.target.value);
                setFormData({
                  ...formData,
                  country: countryId || undefined,
                  state: undefined, // reset state when country changes
                });
                // Clear validation errors
                if (validationErrors.country) {
                  setValidationErrors({
                    ...validationErrors,
                    country: undefined,
                    state: undefined // also clear state error since it gets reset
                  });
                }
              }}
              disabled={!isEditing}
              className={getFieldClassName('country')}
            >
              <option value="">Select Country</option>
              {countries.map((country) => (
                <option key={country.id} value={country.id}>
                  {country.name}
                </option>
              ))}
            </select>
            {validationErrors.country && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.country}
              </span>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="state">
              State <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <select
              id="state"
              value={formData.state || ''}
              onChange={(e) => handleFieldChange('state', Number(e.target.value) || undefined)}
              disabled={!isEditing || !formData.country}
              className={getFieldClassName('state')}
            >
              <option value="">Select State</option>
              {states.map((state) => (
                <option key={state.id} value={state.id}>
                  {state.name}
                </option>
              ))}
            </select>
            {validationErrors.state && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.state}
              </span>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="city">
              City <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="city"
              type="text"
              value={formData.city || ''}
              onChange={(e) => handleFieldChange('city', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('city')}
            />
            {validationErrors.city && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.city}
              </span>
            )}
          </div>
          <div className="form-group">
            <label htmlFor="zipcode">
              Zipcode <span style={{ color: '#dc3545' }}>*</span>
            </label>
            <input
              id="zipcode"
              type="text"
              value={formData.zipcode || ''}
              onChange={(e) => handleFieldChange('zipcode', e.target.value)}
              disabled={!isEditing}
              className={getFieldClassName('zipcode')}
            />
            {validationErrors.zipcode && (
              <span className="error-text" style={{ color: '#dc3545', fontSize: '14px' }}>
                {validationErrors.zipcode}
              </span>
            )}
          </div>
        </div>
        {isEditing && (
          <div className="form-actions">
            <button 
              onClick={handleSave} 
              className="btn btn-primary"
              disabled={isLoading}
            >
              <Save className="btn-icon" />
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
            <button onClick={handleCancel} className="btn btn-outline">
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfileDetailsTab;