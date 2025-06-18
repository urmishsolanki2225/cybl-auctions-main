import { API_ENDPOINTS } from './endpoints';

interface ApiError {
  message: string;
  errors?: {
    [key: string]: string[];
    non_field_errors?: string[];
  };
  status?: number;
}

// Helper function to handle API requests
async function makeRequest<T>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data: any = null,
  requiresAuth: boolean = false
): Promise<T> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (requiresAuth) {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    method,
    headers,
  };

  if (data) {
    config.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(url, config);
    const responseData = await response.json();

    if (!response.ok) {
      throw {
        message: responseData.message || 'Something went wrong',
        errors: responseData.errors,
        status: response.status
      } as ApiError;
    }
    return responseData as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Helper function specifically for FormData requests (like file uploads)
async function makeFormDataRequest<T>(
  url: string,
  method: 'POST' | 'PUT' = 'POST',
  formData: FormData,
  requiresAuth: boolean = true
): Promise<T> {
  const headers: HeadersInit = {};

  if (requiresAuth) {
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('Authentication token not found');
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    method,
    headers,
    body: formData,
  };

  try {
    const response = await fetch(url, config);
    const responseData = await response.json();

    if (!response.ok) {
      throw {
        message: responseData.message || 'Something went wrong',
        errors: responseData.errors,
        status: response.status
      } as ApiError;
    }
    return responseData as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Auth API functions
export const authApi = {
  login: async (email: string, password: string) => {
    return makeRequest(API_ENDPOINTS.LOGIN, 'POST', { email, password });
  },
};

// Public API functions (don't require token)
export const publicApi = {
  getCountries: async () => {
    return makeRequest(API_ENDPOINTS.COUNTRIES);
  },  
  getStatesByCountry: async (countryId: number) => {
    return makeRequest(API_ENDPOINTS.STATES_BY_COUNTRY(countryId));
  },
  getFeaturedAuctions: async () => {
    return makeRequest(API_ENDPOINTS.FEATURED_AUCTIONS);
  },  
  getRunningAuctions: async (queryString?: string) => {
    const url = queryString 
      ? `${API_ENDPOINTS.RUNNING_AUCTIONS}${queryString}`
      : API_ENDPOINTS.RUNNING_AUCTIONS;
    return makeRequest(url);
  },  

  getAuctionDetails: async (id, filters = {}) => {
    const params = new URLSearchParams();    
    // Add filter parameters that match your Django serializer
    if (filters.search) params.append('search', filters.search);
    if (filters.categories && filters.categories.length > 0) {
      filters.categories.forEach(cat => params.append('categories', cat));
    }
    if (filters.min_bid) params.append('min_bid', filters.min_bid);
    if (filters.max_bid) params.append('max_bid', filters.max_bid);
    if (filters.status) params.append('status', filters.status);
    if (filters.sort_by) params.append('sort_by', filters.sort_by);
    
    const url = params.toString() 
      ? `${API_ENDPOINTS.AUCTION_DETAILS(id)}?${params.toString()}`
      : API_ENDPOINTS.AUCTION_DETAILS(id);
      
    return makeRequest(url);
  },

  getLotDetails: async (id: number) => {
    return makeRequest(API_ENDPOINTS.LOT_DETAILS(id));
  },

  getCompanies: async () => {
    return makeRequest(API_ENDPOINTS.COMPANIES);
  },

  getCategories: async () => {
    return makeRequest(API_ENDPOINTS.CATEGORIES);
  },
  
  // Search/Filter functions
  searchAuctions: async (filters: {
    company_id?: string;
    closing_date?: string;
    distance?: string;
    zip_code?: string;
    categories?: string[];
  }) => {
    const params = new URLSearchParams();
    
    if (filters.company_id) params.append('company_id', filters.company_id);
    if (filters.closing_date) params.append('closing_date', filters.closing_date);
    if (filters.distance) params.append('distance', filters.distance);
    if (filters.zip_code) params.append('zip_code', filters.zip_code);
    if (filters.categories && filters.categories.length > 0) {
      filters.categories.forEach(cat => params.append('categories', cat));
    }
    
    return makeRequest(`${API_ENDPOINTS.RUNNING_AUCTIONS}?${params.toString()}`);
  },
};

// Protected API functions (require token)
export const protectedApi = {
  getProfile: async () => {
    return makeRequest(API_ENDPOINTS.PROFILEPAGE, 'GET', null, true);
  },
  updateProfile: async (profileData: any) => {
    return makeRequest(API_ENDPOINTS.PROFILEPAGE, 'PUT', profileData, true);
  },
  uploadProfilePhoto: async (formData: FormData) => {
    return makeFormDataRequest(API_ENDPOINTS.PROFILEPAGE, 'PUT', formData, true);
  },
  getBiddingHistory: async () => {
    return makeRequest(API_ENDPOINTS.BIDDINGHISTROY, 'GET', null, true);
  },
  placeBid: async (lotId: number, amount: number) => {
    return makeRequest(API_ENDPOINTS.LOTS(lotId), 'POST', { amount }, true);
  },
  getLotBids: async (lotId: number) => {
    return makeRequest(API_ENDPOINTS.LOTSBIDS(lotId), 'GET', null, true);
  },
  getUsersBids: async () => {
    return makeRequest(API_ENDPOINTS.USERBIDS, 'GET', null, true);
  },
  getUsersPaymentHistory: async () => {
    return makeRequest(API_ENDPOINTS.USERPAYMENTHISTORY, 'GET', null, true);
  },
};