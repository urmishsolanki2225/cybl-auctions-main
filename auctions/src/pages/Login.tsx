import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authApi } from '../api/apiUtils';
import '../styles/Auth.css';
import { useAuth } from '../context/AuthContext';
import { toast } from "react-toastify";
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { API_ENDPOINTS } from "../api/endpoints";

interface ValidationErrors {
  email?: string[];
  password?: string[];
  non_field_errors?: string[];
  [key: string]: string[] | undefined;
}

interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  groups?: string[]; // Assuming groups contains role names like 'Buyer' or 'Seller'
}

interface GoogleAuthResponse {
  credential?: string;
  clientId?: string;
  select_by?: string;
}

interface ApiError {
  errors?: ValidationErrors;
  message?: string;
}



const Login = () => {
  const GOOGLE_CLIENT_ID = "1087829592235-sm0nbsei6bl5jnvrgft26l8ide3sjgbm.apps.googleusercontent.com";

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { login } = useAuth();


   useEffect(() => {
    if (isAuthenticated) {
      navigate('/account', { replace: true }); // Redirect to home if already logged in
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

      toast.success("Login successfully!");

      login(response.authToken, response.user);

      // Check user role and redirect accordingly
      const user = response.user as User;
      console.log('User groups:', user.groups); // Debug log
      
      // Case-insensitive check and trim whitespace
      const normalizedGroups = user.groups?.map(group => group.trim().toLowerCase());
      
      if (normalizedGroups?.includes('seller')) {
         console.log('Redirecting to seller activity');
          navigate('/seller/dashbaord', { replace: true });
      } else {
        console.log('Redirecting to account');
        navigate('/account', { replace: true });
      }
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

  // Google Login Handler
  const handleGoogleSuccess = async (response: GoogleAuthResponse) => {
    try {
      if (!response.credential) {
        throw new Error("No credential received from Google");
      }

      setGoogleLoading(true);
      setErrors({});

      const googleResponse = await fetch(`${API_ENDPOINTS.LOGIN}google/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          auth_token: response.credential,
        }),
      });

      const data = await googleResponse.json();

      if (googleResponse.ok && data.user) {
        // Store token and user data
        localStorage.setItem('authToken', data.authToken);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        toast.success("Login successful!");
        login(data.authToken, data.user);

        // Check user role and redirect accordingly
        const user = data.user as User;
        console.log('User groups:', user.groups);
        
        const normalizedGroups = user.groups?.map(group => group.trim().toLowerCase());
        
        if (normalizedGroups?.includes('seller')) {
          console.log('Redirecting to seller dashboard');
          navigate('/seller/dashboard', { replace: true });
        } else {
          console.log('Redirecting to account');
          navigate('/account', { replace: true });
        }
      } else {
        // Handle different error scenarios
        if (googleResponse.status === 404 && data.redirect_to_register) {
          // User doesn't exist, redirect to registration
          toast.info("Account not found. Please register first.");
          navigate('/register', {
            state: {
              message: "Account not found. Please register first.",
              email: data.email // If available
            }
          });
        } else if (data.errors) {
          setErrors(data.errors);
        } else {
          setErrors({
            non_field_errors: [data.message || "Google login failed"]
          });
        }
      }
    } catch (error) {
      console.error("Google login error:", error);
      setErrors({
        non_field_errors: ["Failed to authenticate with Google. Please try again."]
      });
    } finally {
      setGoogleLoading(false);
    }
  };

  const handleGoogleError = () => {
    setErrors({
      non_field_errors: ["Google login failed. Please try again or use email login."]
    });
  };

  return (
    <div className="container">
      <div className="auth-form-wrapper">
        <div className="auth-header">
          <h1 className="auth-title">Welcome Back</h1>
        </div>
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

        <div className="social-login-options">
          <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={handleGoogleError}
              useOneTap={false}
              text="signin_with"
              shape="rectangular"
              size="large"
              width="300"
              logo_alignment="left"
              disabled={isLoading || googleLoading}
            />
          </GoogleOAuthProvider>
        </div>
        
        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

