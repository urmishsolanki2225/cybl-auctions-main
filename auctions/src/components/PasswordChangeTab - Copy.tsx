import { useState } from 'react';
import { Lock, Eye, EyeOff, CheckCircle, AlertCircle, Check, X } from 'lucide-react';
import { API_ENDPOINTS } from '../api/endpoints';
import { toast } from 'react-toastify';
 
interface PasswordFormData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
 
interface PasswordFormErrors {
  currentPassword?: string;
  newPassword?: string;
  confirmPassword?: string;
  confirmNewPassword?: string;
  general?: string;
}
 
interface ApiResponse {
  success: boolean;
  message: string;
  user?: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    full_name: string;
  };
  errors?: {
    [key: string]: string[] | string;
  };
}
 
interface PasswordRequirement {
  id: string;
  label: string;
  test: (password: string) => boolean;
}
 
const PasswordChangeTab = () => {
  const [formData, setFormData] = useState<PasswordFormData>({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
 
  const [loading, setLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<PasswordFormErrors>({});
  const [successMessage, setSuccessMessage] = useState<string>('');
 
  const passwordRequirements: PasswordRequirement[] = [
    {
      id: 'length',
      label: 'At least 8 characters',
      test: (password: string) => password.length >= 8
    },
    {
      id: 'uppercase',
      label: 'One uppercase letter',
      test: (password: string) => /[A-Z]/.test(password)
    },
    {
      id: 'lowercase',
      label: 'One lowercase letter',
      test: (password: string) => /[a-z]/.test(password)
    },
    {
      id: 'number',
      label: 'One number',
      test: (password: string) => /\d/.test(password)
    },
    {
      id: 'special',
      label: 'One special character (!@#$%^&*)',
      test: (password: string) => /[!@#$%^&*(),.?":{}|<>]/.test(password)
    }
  ];
 
  const getAuthToken = (): string => {
    return localStorage.getItem('authToken') || localStorage.getItem('token') || '';
  };
 
  const validatePassword = (password: string): boolean => {
    return passwordRequirements.every(req => req.test(password));
  };
 
  const getPasswordStrength = (password: string) => {
    const passedRequirements = passwordRequirements.filter(req => req.test(password)).length;
    return {
      score: passedRequirements,
      total: passwordRequirements.length,
      isValid: passedRequirements === passwordRequirements.length
    };
  };
 
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
 
    if (errors[name as keyof PasswordFormErrors]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
 
    if (successMessage) {
      setSuccessMessage('');
    }
  };
 
  const validateForm = (): PasswordFormErrors => {
    const newErrors: PasswordFormErrors = {};
 
    if (!formData.currentPassword) {
      newErrors.currentPassword = 'Current password is required';
    }
 
    if (!formData.newPassword) {
      newErrors.newPassword = 'New password is required';
    } else if (!validatePassword(formData.newPassword)) {
      newErrors.newPassword = 'Password does not meet all requirements';
    }
 
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your new password';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = 'New passwords do not match';
    }
 
    if (formData.currentPassword && formData.newPassword && formData.currentPassword === formData.newPassword) {
      newErrors.newPassword = 'New password must be different from current password';
    }
 
    return newErrors;
  };
 
  const handleSubmit = async (): Promise<void> => {
    console.log('Form submission started');
    setErrors({});
    setSuccessMessage('');
 
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      console.log('Client validation failed:', validationErrors);
      setErrors(validationErrors);
      return;
    }
 
    setLoading(true);
 
    try {
      const token = getAuthToken();
      console.log('Auth token exists:', !!token);
 
      const requestBody = {
        currentPassword: formData.currentPassword,
        newPassword: formData.newPassword,
        confirmNewPassword: formData.confirmPassword
      };
      
      const response = await fetch(API_ENDPOINTS.PASSWORD_UPDATE, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });
 
      const data: ApiResponse = await response.json();
 
      if (response.ok && data.success) {
        toast.success(`Password update successful`);
        setSuccessMessage(data.message || 'Password updated successfully!');
        setFormData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        });
      } else {
        console.log('Password update failed:', data);
        
        const serverErrors: PasswordFormErrors = {};
        
        if (data.errors) {
          Object.keys(data.errors).forEach(key => {
            const errorValue = data.errors![key];
            const errorMessage = Array.isArray(errorValue) ? errorValue[0] : errorValue;
            
            if (key === 'confirmNewPassword') {
              serverErrors.confirmPassword = errorMessage;
            } else {
              serverErrors[key as keyof PasswordFormErrors] = errorMessage;
            }
          });
        }
        
        if (data.message && !Object.keys(serverErrors).length) {
          serverErrors.general = data.message;
        }
        
        setErrors(serverErrors);
      }
    } catch (error) {
      console.error('Network error:', error);
      setErrors({
        general: 'Network error. Please check your connection and try again.'
      });
    } finally {
      setLoading(false);
    }
  };
 
  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };
 
  const passwordStrength = getPasswordStrength(formData.newPassword);
 
  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <Lock className="w-5 h-5" />
            Change Password
          </h2>
        </div>
        
        <div className="p-6">         
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-800 rounded-lg flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              {errors.general}
            </div>
          )}
 
          <div className="space-y-6">
            <div>
              <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Current Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="currentPassword"
                  name="currentPassword"
                  type={showPasswords.current ? "text" : "password"}
                  value={formData.currentPassword}
                  onChange={handleChange}
                  required
                  style={{
                    width: '50%',
                    padding: '12px 16px',
                    border: '2px solid #e9ecef',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    borderColor: errors.currentPassword ? 'red' : '#e9ecef',
                  }}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  onClick={() => togglePasswordVisibility('current')}
                  aria-label="Toggle password visibility"
                >
                  {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.currentPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.currentPassword}</p>
              )}
            </div>
 
            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
                New Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="newPassword"
                  name="newPassword"
                  type={showPasswords.new ? "text" : "password"}
                  value={formData.newPassword}
                  onChange={handleChange}
                  required
                  style={{
                    width: '50%',
                    padding: '12px 16px',
                    border: '2px solid #e9ecef',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    borderColor: errors.currentPassword ? 'red' : '#e9ecef',
                  }}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  onClick={() => togglePasswordVisibility('new')}
                  aria-label="Toggle password visibility"
                >
                  {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              
              {errors.newPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.newPassword}</p>
              )}
 
              {/* Password Requirements - Always visible when user starts typing */}
              {formData.newPassword && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Password Requirements ({passwordStrength.score}/{passwordStrength.total} met)
                  </p>
                  <div className="space-y-1">
                    {passwordRequirements.map((requirement) => {
                      const isMet = requirement.test(formData.newPassword);
                      return (
                        <div
                          key={requirement.id}
                          className={`flex items-center gap-2 text-sm ${
                            isMet ? 'text-green-600' : 'text-gray-500'
                          }`}
                        >
                          {isMet ? (
                            <Check className="w-4 h-4 text-green-500" />
                          ) : (
                            <X className="w-4 h-4 text-gray-400" />
                          )}
                          <span className={isMet ? 'font-medium' : ''}>{requirement.label}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
 
              {/* Static helper text when no password is entered */}
              {!formData.newPassword && (
                <p className="text-sm text-gray-500 mt-2">
                  Must be at least 8 characters with uppercase, lowercase, number, and special character.
                </p>
              )}
            </div>
 
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showPasswords.confirm ? "text" : "password"}
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  style={{
                    width: '50%',
                    padding: '12px 16px',
                    border: '2px solid #e9ecef',
                    borderRadius: '8px',
                    fontSize: '16px',
                    transition: 'border-color 0.3s ease',
                    borderColor: errors.currentPassword ? 'red' : '#e9ecef',
                  }}
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  onClick={() => togglePasswordVisibility('confirm')}
                  aria-label="Toggle password visibility"
                >
                  {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
              )}
              
              {/* Password match indicator */}
              {formData.confirmPassword && formData.newPassword && (
                <div className={`mt-2 flex items-center gap-2 text-sm ${
                  formData.newPassword === formData.confirmPassword ? 'text-green-600' : 'text-red-600'
                }`}>
                  {formData.newPassword === formData.confirmPassword ? (
                    <>
                      <Check className="w-4 h-4" />
                      <span>Passwords match</span>
                    </>
                  ) : (
                    <>
                      <X className="w-4 h-4" />
                      <span>Passwords do not match</span>
                    </>
                  )}
                </div>
              )}
            </div>
 
            <button
              type="button"
              onClick={handleSubmit}
              className="btn btn-primary w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              disabled={loading}
              style={{

                marginTop: '20px'
              }}
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                  </svg>
                  Updating...
                </div>
              ) : (
                'Update Password'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
 
export default PasswordChangeTab;
 