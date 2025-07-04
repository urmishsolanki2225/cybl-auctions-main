import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "../styles/Auth.css";
import { API_ENDPOINTS } from "../api/endpoints";
import { toast } from "react-toastify";
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from "jwt-decode";

// Type definitions
interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

interface FormErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  agreeToTerms?: string;
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
    date_joined: string;
  };
  errors?: {
    [key: string]: string[] | string;
  };
}


// Add to your interfaces
interface GoogleAuthResponse {
  credential?: string;
  clientId?: string;
  select_by?: string;
}

interface GoogleUserData {
  given_name: string;
  family_name: string;
  email: string;
  picture?: string;
}

// Add this constant (get from your Google Cloud Console)
const GOOGLE_CLIENT_ID = "1087829592235-sm0nbsei6bl5jnvrgft26l8ide3sjgbm.apps.googleusercontent.com";

const Registration: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [successMessage, setSuccessMessage] = useState<string>("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    // Clear specific field error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const validateForm = (): FormErrors => {
    const newErrors: FormErrors = {};

    // First name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = "First name is required";
    } else if (formData.firstName.trim().length < 2) {
      newErrors.firstName = "First name must be at least 2 characters";
    }

    // Last name validation
    if (!formData.lastName.trim()) {
      newErrors.lastName = "Last name is required";
    } else if (formData.lastName.trim().length < 2) {
      newErrors.lastName = "Last name must be at least 2 characters";
    }

    // Email validation
    if (!formData.email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = "Please enter a valid email address";
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors.password =
        "Password must contain at least one uppercase letter, one lowercase letter, and one number";
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    // Terms agreement validation
    if (!formData.agreeToTerms) {
      newErrors.agreeToTerms = "You must agree to the Terms of Service";
    }

    return newErrors;
  };

  const handleSubmit = async (
    e: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage("");

    // Client-side validation
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(API_ENDPOINTS.REGISTRATION, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstName: formData.firstName.trim(),
          lastName: formData.lastName.trim(),
          email: formData.email.trim().toLowerCase(),
          password: formData.password,
          confirmPassword: formData.confirmPassword,
        }),
      });

      const data: ApiResponse = await response.json();

      if (response.ok && data.success && data.user) {
        setSuccessMessage(
          `Welcome ${data.user.full_name}! Your account has been created successfully.`
        );
        toast.success(
          `Welcome ${data.user.full_name}! Your account has been created successfully.`
        );
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/login", {
          state: {
            message: `Welcome ${data.user.full_name}! Your account has been created successfully.`,
          },
        });
      } else {
        // Handle API errors
        if (data.errors) {
          const apiErrors: FormErrors = {};

          // Map backend field names to frontend field names
          Object.keys(data.errors).forEach((key) => {
            const errorValue = data.errors![key];
            const errorMessage = Array.isArray(errorValue)
              ? errorValue[0]
              : errorValue;

            switch (key) {
              case "first_name":
                apiErrors.firstName = errorMessage;
                break;
              case "last_name":
                apiErrors.lastName = errorMessage;
                break;
              case "email":
                apiErrors.email = errorMessage;
                break;
              case "password":
                apiErrors.password = errorMessage;
                break;
              case "confirm_password":
                apiErrors.confirmPassword = errorMessage;
                break;
              case "non_field_errors":
                apiErrors.general = errorMessage;
                break;
              default:
                apiErrors.general = errorMessage;
            }
          });

          setErrors(apiErrors);
        } else {
          setErrors({
            general: data.message || "Registration failed. Please try again.",
          });
        }
      }
    } catch (error) {
      console.error("Registration error:", error);
      setErrors({
        general: "Network error. Please check your connection and try again.",
      });
    } finally {
      setLoading(false);
    }
  };


  // Add these new functions
  const handleGoogleSuccess = async (response: GoogleAuthResponse) => {
    try {
      if (!response.credential) {
        throw new Error("No credential received from Google");
      }

      const userData: GoogleUserData = jwtDecode(response.credential);
      
      setLoading(true);
      setErrors({});

      const googleResponse = await fetch(`${API_ENDPOINTS.REGISTRATION}google/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          auth_token: response.credential,
        }),
      });

      const data: ApiResponse = await googleResponse.json();

      if (googleResponse.ok && data.success && data.user) {
        toast.success(
          `Welcome ${data.user.full_name}! Your account has been created successfully.`
        );
        localStorage.setItem("user", JSON.stringify(data.user));
        navigate("/account");
      } else {
        if (data.errors) {
          setErrors({
            general: data.errors.non_field_errors || "Google registration failed",
          });
        } else {
          setErrors({
            general: data.message || "Google registration failed",
          });
        }
      }
    } catch (error) {
      console.error("Google login error:", error);
      setErrors({
        general: "Failed to authenticate with Google. Please try again.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleError = () => {
    setErrors({
      general: "Google login failed. Please try again or use email registration.",
    });
  };


  return (
    <div className="container">
      <div className="auth-container">
        <div className="auth-form-wrapper-register">
          <div className="auth-header">
            <h1 className="auth-title">Create Account</h1>
          </div>

          {/* Success Message */}
          {successMessage && (
            <div className="alert alert-success">{successMessage}</div>
          )}

          {/* General Error Message */}
          {errors.general && (
            <div className="alert alert-error">{errors.general}</div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-row">
              <div className="form-group register-from-group">
                <label htmlFor="firstName" className="form-label">
                  First Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className={`form-input ${errors.firstName ? "error" : ""}`}
                  placeholder="Enter your first name"
                  autoComplete="given-name"
                />
                {errors.firstName && (
                  <span className="error-message">{errors.firstName}</span>
                )}
              </div>

              <div className="form-group register-from-group">
                <label htmlFor="lastName" className="form-label">
                  Last Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className={`form-input ${errors.lastName ? "error" : ""}`}
                  placeholder="Enter your last name"
                  autoComplete="family-name"
                />
                {errors.lastName && (
                  <span className="error-message">{errors.lastName}</span>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email Address <span className="required">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`form-input ${errors.email ? "error" : ""}`}
                placeholder="Enter your email address"
                autoComplete="email"
              />
              {errors.email && (
                <span className="error-message">{errors.email}</span>
              )}
            </div>
            <div className="form-row">
              <div className="form-group register-from-group">
                <label htmlFor="password" className="form-label">
                  Password <span className="required">*</span>
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`form-input ${errors.password ? "error" : ""}`}
                  placeholder="Create a strong password"
                  autoComplete="new-password"
                />
                <small className="form-hint">
                  Must be at least 8 characters with uppercase, lowercase, and
                  number
                </small>
                {errors.password && (
                  <div className="error-message">{errors.password}</div>
                )}
              </div>

              <div className="form-group register-from-group">
                <label htmlFor="confirmPassword" className="form-label">
                  Confirm Password <span className="required">*</span>
                </label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className={`form-input ${
                    errors.confirmPassword ? "error" : ""
                  }`}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
                {errors.confirmPassword && (
                  <span className="error-message">
                    {errors.confirmPassword}
                  </span>
                )}
              </div>
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="agreeToTerms"
                  checked={formData.agreeToTerms}
                  onChange={handleChange}
                  className="checkbox-input"
                />
                <span className="checkbox-custom"></span>I agree to the&nbsp;
                <Link
                  to="/terms"
                  className="terms-link"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  &nbsp;Terms of Service&nbsp;
                </Link>
                and&nbsp;
                <Link
                  to="/privacy"
                  className="terms-link"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </Link>
              </label>
              {errors.agreeToTerms && (
                <span className="error-message">{errors.agreeToTerms}</span>
              )}
            </div>

            <button
              type="submit"
              className="btn btn-primary auth-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner"></span>
                  Creating Account...
                </>
              ) : (
                "Create Account"
              )}
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <div className="social-login-options">
            <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap={false}
                text="continue_with"
                shape="rectangular"
                size="large"
                width="300"
                logo_alignment="left"
              />
            </GoogleOAuthProvider>

          </div>

          <div className="auth-footer">
            <p>
              Already have an account?{" "}
              <Link to="/login" className="auth-link">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Registration;
