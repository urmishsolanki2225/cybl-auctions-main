// src/api/endpoints.ts
const BASE_URL = 'http://192.168.2.108:8000/';
export default BASE_URL;

const BASE_API_URL = 'http://192.168.2.108:8000/api/';

export const API_ENDPOINTS = {
  // Authentication
  LOGIN: `${BASE_API_URL}login/`,
  GOOGLE_LOGIN: `${BASE_URL}/login/google/`,
  
  // User Profile
  PROFILEPAGE: `${BASE_API_URL}profile/`,
  USERBIDS: `${BASE_API_URL}user/bidding-history/`,
  USERPAYMENTHISTORY: `${BASE_API_URL}user/payment-history/?tab=all`,
  
  // Location Data
  COUNTRIES: `${BASE_API_URL}countries/`,
  STATES_BY_COUNTRY: (countryId: number) => `${BASE_API_URL}countries/${countryId}/states/`,
  
  // Auctions
  FEATURED_AUCTIONS: `${BASE_API_URL}auctions/?type=featured`,
  RUNNING_AUCTIONS: `${BASE_API_URL}auctions/?type=running&`,
  NEXT_TO_CLOSE : `${BASE_API_URL}auctions/closing-soon/`,
  AUCTION_DETAILS: (id: number) => `${BASE_API_URL}auctions/${id}/`,
  BIDDINGHISTROY: `${BASE_API_URL}bidding-history/`,

  PASSWORD_UPDATE: `${BASE_API_URL}password/update/`,

  REGISTRATION: `${BASE_API_URL}register/`,

  // Lots
  LOT_DETAILS: (id: number) => `${BASE_API_URL}lots/${id}/`,
  LOTS: (id: number) => `${BASE_API_URL}lots/${id}/bid/`,
  LOTSBIDS: (id: number) => `${BASE_API_URL}lots/${id}/bids/`,
  
  // Companies & Categories
  COMPANIES: `${BASE_API_URL}companies/`,

  CATEGORIES: `${BASE_API_URL}categories/`,
  SUB_CATEGORIES: (id: number) => `${BASE_API_URL}categories/${id}`,
  CATEGORY_LOTS: `${BASE_API_URL}lots/`, 
  
  // Search & Filters
  // SEARCH_AUCTIONS: `${BASE_API_URL}auctions/search/`,
  // FILTER_AUCTIONS: `${BASE_API_URL}auctions/filter/`,

  INVOICE: (paymentId: number) => `${BASE_API_URL}payments/${paymentId}/invoice/`,

  // Watchlist Endpoints
  WATCHLIST: `${BASE_API_URL}watchlist/`,
  WATCHLIST_ADD: (inventoryId: number) => `${BASE_API_URL}watchlist/add/${inventoryId}/`,
  WATCHLIST_REMOVE: (inventoryId: number) => `${BASE_API_URL}watchlist/remove/${inventoryId}/`,

  LOT_COMMENTS: (lotId) => `${BASE_API_URL}lots/${lotId}/comments/`,


  ACTIVE_LOTS: `${BASE_API_URL}lots/active/`,
};