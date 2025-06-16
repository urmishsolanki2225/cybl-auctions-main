import { createContext, useContext, useState, ReactNode, useEffect, useRef } from 'react';
import { isTokenExpired, getTimeUntilExpiration } from '../utils/tokenUtils';

interface User {
    id: number;
    email: string;
    username: string;
    first_name?: string;
    last_name?: string;
}

interface AuthContextType {
    isAuthenticated: boolean;
    user: User | null;
    isLoading: boolean;
    login: (token: string, userData: User) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const tokenCheckInterval = useRef<NodeJS.Timeout | null>(null);

    // Function to clear auth data
    const clearAuthData = () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        localStorage.removeItem('userEmail');
        setIsAuthenticated(false);
        setUser(null);
        
        // Clear the token check interval
        if (tokenCheckInterval.current) {
            clearInterval(tokenCheckInterval.current);
            tokenCheckInterval.current = null;
        }
    };

    // Function to start monitoring token expiration
    const startTokenMonitoring = (token: string) => {
        // Clear existing interval
        if (tokenCheckInterval.current) {
            clearInterval(tokenCheckInterval.current);
        }

        // Check token expiration every minute
        tokenCheckInterval.current = setInterval(() => {
            if (isTokenExpired(token)) {
                console.log('Token expired during session, logging out');
                clearAuthData();
            }
        }, 60000); // Check every 1 minute

        // Also set a timeout for exact expiration time
        const timeUntilExpiration = getTimeUntilExpiration(token);
        if (timeUntilExpiration > 0) {
            setTimeout(() => {
                console.log('Token expired, logging out');
                clearAuthData();
            }, timeUntilExpiration);
        }
    };

    useEffect(() => {
        console.log('Checking auth state...');
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('user');
       // console.log('Token exists:', !!token, 'User data exists:', !!userData);
        
        if (token && userData) {
            // Check if token is expired
            if (isTokenExpired(token)) {
                console.log('Token is expired, clearing auth data');
                clearAuthData();
            } else {
                try {
                    const parsedUser = JSON.parse(userData);
                    //console.log('Token is valid, setting authenticated user:', parsedUser);
                    setIsAuthenticated(true);
                    setUser(parsedUser);
                    
                    // Start monitoring token expiration
                    startTokenMonitoring(token);
                } catch (e) {
                    console.error('Failed to parse user data', e);
                    clearAuthData();
                }
            }
        }
        setIsLoading(false);

        // Cleanup interval on unmount
        return () => {
            if (tokenCheckInterval.current) {
                clearInterval(tokenCheckInterval.current);
            }
        };
    }, []);

    const login = (token: string, userData: User) => {
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setIsAuthenticated(true);
        setUser(userData);
        
        // Start monitoring the new token
        startTokenMonitoring(token);
        
        console.log('Logged in:', userData);
    };

    const logout = () => {
        clearAuthData();
    };

    if (isLoading) {
        return null; // Or return a loading spinner component
    }

    return (
        <AuthContext.Provider value={{ 
            isAuthenticated, 
            user, 
            isLoading, 
            login, 
            logout 
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};