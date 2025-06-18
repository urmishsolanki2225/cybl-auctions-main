// Create a new file: src/utils/tokenUtils.ts

/**
 * Decode JWT token payload without verification
 * @param token JWT token string
 * @returns Decoded payload object
 */
export const decodeJWTPayload = (token: string): any => {
    try {
        // JWT has 3 parts separated by dots: header.payload.signature
        const parts = token.split('.');
        if (parts.length !== 3) {
            throw new Error('Invalid JWT format');
        }

        // Decode the payload (second part)
        const payload = parts[1];
        
        // Add padding if needed (base64 requires padding)
        const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
        
        // Decode base64
        const decodedPayload = atob(paddedPayload);
        
        // Parse JSON
        return JSON.parse(decodedPayload);
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
};

/**
 * Check if JWT token is expired
 * @param token JWT token string
 * @returns true if expired, false if valid
 */
export const isTokenExpired = (token: string): boolean => {
    try {
        const payload = decodeJWTPayload(token);
        
        if (!payload || !payload.exp) {
            // If we can't decode or no expiration, consider it expired
            return true;
        }

        // JWT exp is in seconds, Date.now() is in milliseconds
        const currentTime = Date.now() / 1000;
        const expirationTime = payload.exp;

        // console.log('Token expires at:', new Date(expirationTime * 1000));
        // console.log('Current time:', new Date(currentTime * 1000));
        console.log('Token expired:', expirationTime < currentTime);

        return expirationTime < currentTime;
    } catch (error) {
        console.error('Error checking token expiration:', error);
        return true; // Consider invalid tokens as expired
    }
};

/**
 * Get token expiration date
 * @param token JWT token string
 * @returns Date object or null if invalid
 */
export const getTokenExpirationDate = (token: string): Date | null => {
    try {
        const payload = decodeJWTPayload(token);
        
        if (!payload || !payload.exp) {
            return null;
        }

        // Convert from seconds to milliseconds
        return new Date(payload.exp * 1000);
    } catch (error) {
        console.error('Error getting token expiration date:', error);
        return null;
    }
};

/**
 * Get time remaining until token expires
 * @param token JWT token string
 * @returns milliseconds until expiration, or 0 if expired
 */
export const getTimeUntilExpiration = (token: string): number => {
    try {
        const expirationDate = getTokenExpirationDate(token);
        
        if (!expirationDate) {
            return 0;
        }

        const timeRemaining = expirationDate.getTime() - Date.now();
        return Math.max(0, timeRemaining);
    } catch (error) {
        console.error('Error calculating time until expiration:', error);
        return 0;
    }
};