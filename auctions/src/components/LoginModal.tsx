import { useState } from "react";
import { authApi, ApiError } from "../api/apiUtils";
import { useAuth } from "../context/AuthContext";
import "../styles/LoginModal.css"; // We'll create this CSS file next
import { toast } from "react-toastify";

interface ValidationErrors {
  email?: string[];
  password?: string[];
  non_field_errors?: string[];
  [key: string]: string[] | undefined;
}

interface LoginModalProps {
  onClose: () => void;
  onLoginSuccess: () => void;
}

const LoginModal = ({ onClose, onLoginSuccess }: LoginModalProps) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });
  const [errors, setErrors] = useState<ValidationErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false); //
  const { login } = useAuth();

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));

    // Clear relevant errors when user types
    if (errors[name] || errors.non_field_errors) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        if (name === "password") delete newErrors.non_field_errors;
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
      newErrors.email = ["Email is required"];
    }
    if (!formData.password) {
      newErrors.password = ["Password is required"];
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsLoading(true);

    try {
      const response = await authApi.login(formData.email, formData.password);

      // Store token and user data
      localStorage.setItem("authToken", response.authToken);
      localStorage.setItem("user", JSON.stringify(response.user));
      if (formData.rememberMe) {
        localStorage.setItem("userEmail", formData.email);
      } else {
        localStorage.removeItem("userEmail");
      }
      if (response.authToken) {
        toast.success("Login successful.");
      }
      login(response.authToken, response.user);

      onLoginSuccess();
    } catch (error) {
      const apiError = error as ApiError;

      if (apiError.errors) {
        // Handle API validation errors
        setErrors(apiError.errors);
      } else {
        // Handle generic API errors
        setErrors({
          non_field_errors: [
            apiError.message || "Login failed. Please try again.",
          ],
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
    <div className="login-modal-overlay">
      <div className="login-modal">
        <button className="close-button" onClick={onClose}>
          &times;
        </button>

        <div className="login-modal-header">
          <h2>Login to Place Your Bid</h2>
          <p>You need to be logged in to place a bid on this lot</p>
        </div>

        {errors.non_field_errors && (
          <div className="login-modal-error">
            {errors.non_field_errors.map((msg, index) => (
              <p key={index}>{msg}</p>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-modal-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
            />
            {getErrorMessage("email")}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
                type={showPassword ? "text" : "password"}
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
            />
            <button
              type="button"
              className="password-toggle"
              onClick={togglePasswordVisibility}
            >
              {showPassword ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              )}
            </button>
            {getErrorMessage("password")}
          </div>

          <div className="form-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="rememberMe"
                checked={formData.rememberMe}
                onChange={handleChange}
              />
              <span className="checkbox-custom"></span>
              Remember me
            </label>
          </div>

          <button type="submit" className="submit-button" disabled={isLoading}>
            {isLoading ? "Logging In..." : "Login"}
          </button>
        </form>

        <div className="login-modal-footer">
          <p>
            Don't have an account?{" "}
            <a href="/register" className="register-link">
              Sign up here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
