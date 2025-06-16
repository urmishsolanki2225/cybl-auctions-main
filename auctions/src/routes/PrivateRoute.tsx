// src/routes/PrivateRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const { isAuthenticated } = useAuth();
  const token = localStorage.getItem('authToken');

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default PrivateRoute;
