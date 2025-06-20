import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi, ApiError } from '../api/apiUtils';
import '../styles/Auth.css';
import { useAuth } from '../context/AuthContext';

interface ValidationErrors {
  email?: string[];
  password?: string[];
  non_field_errors?: string[];
  [key: string]: string[] | undefined;
}

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { login } = useAuth();


   useEffect(() => {
    if (isAuthenticated) {
      navigate('/', { replace: true }); // Redirect to home if already logged in
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear relevant errors when user types
    if (errors[name] || errors.non_field_errors) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        if (name === 'password') delete newErrors.non_field_errors;
        return newErrors;
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    
    // Client-side validation
    const newErrors: ValidationErrors = {};
    if (!formData.email.trim()) {
      newErrors.email = ['Email is required'];
    }
    if (!formData.password) {
      newErrors.password = ['Password is required'];
    }
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      const response = await authApi.login(formData.email, formData.password);
      
      // Store token and user data
      localStorage.setItem('authToken', response.authToken);
      localStorage.setItem('user', JSON.stringify(response.user)); 
      if (formData.rememberMe) {
        localStorage.setItem('userEmail', formData.email);
      } else {
        localStorage.removeItem('userEmail');
      }

      login(response.authToken, response.user);

      navigate('/');
    } catch (error) {
      const apiError = error as ApiError;
      
      if (apiError.errors) {
        // Handle API validation errors
        setErrors(apiError.errors);
      } else {
        // Handle generic API errors
        setErrors({
          non_field_errors: [apiError.message || 'Login failed. Please try again.']
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getErrorMessage = (field: string) => {
    if (!errors[field]) return null;
    return (
      <div className="error-message">
        {errors[field]?.map((msg, index) => (
          <p key={index}>{msg}</p>
        ))}
      </div>
    );
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-form-wrapper">
          <div className="auth-header">
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Sign in to your AuctionHub account</p>
          </div>
          {/* Display non-field errors at the top */}
          {/* Non-field errors display */}
          {errors.non_field_errors && (
            <div className="auth-error">
              {errors.non_field_errors.map((msg, index) => (
                <p key={index}>
                  {msg}                  
                </p>
              ))}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your email"
              />
              {getErrorMessage('email')}
            </div>

            <div className="form-group">
              <label htmlFor="password" className="form-label">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="form-input"
                placeholder="Enter your password"
              />
              {getErrorMessage('password')}
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="rememberMe"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  className="checkbox-input"
                />
                <span className="checkbox-custom"></span>
                Remember me
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Forgot password?
              </Link>
            </div>

            <button 
              type="submit" 
              className="btn btn-primary auth-submit"
              disabled={isLoading}
            >
             {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          {/*<div className="auth-divider">
            <span>or</span>
          </div>

          <div className="social-login">
            <button className="btn btn-social google">
              <span className="social-icon">G</span>
              Continue with Google
            </button>
            <button className="btn btn-social facebook">
              <span className="social-icon">f</span>
              Continue with Facebook
            </button>
          </div>*/}

          <div className="auth-footer">
            <p>
              Don't have an account?{' '}
              <Link to="/register" className="auth-link">
                Sign up here
              </Link>
            </p>
          </div>
        </div>

        <div className="auth-image">
          <div className="auth-image-content">
            <h2>Join the Auction</h2>
            <p>Discover amazing items and place winning bids on AuctionHub</p>
            <div className="auth-features">
              <div className="feature">
                <span className="feature-icon">🔒</span>
                <span>Secure Bidding</span>
              </div>
              <div className="feature">
                <span className="feature-icon">⚡</span>
                <span>Live Auctions</span>
              </div>
              <div className="feature">
                <span className="feature-icon">🏆</span>
                <span>Rare Collectibles</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

function authLogin(token: any) {
  throw new Error('Function not implemented.');
}
