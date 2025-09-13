// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: `${API_BASE_URL}/api/auth/login/`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout/`,
    REGISTER: `${API_BASE_URL}/api/auth/register/`,
  },
  ACCOUNTS: {
    ACCOUNT: `${API_BASE_URL}/api/accounts/account/`,
    PORTFOLIO: `${API_BASE_URL}/api/accounts/portfolio/`,
  },
  MARKETS: {
    LIST: `${API_BASE_URL}/api/markets/markets/`,
    DETAIL: (id) => `${API_BASE_URL}/api/markets/markets/${id}/`,
    ORDER_BOOK: (id) => `${API_BASE_URL}/api/markets/markets/${id}/orderbook/YES/`,
    PLACE_ORDER: `${API_BASE_URL}/api/markets/place-order/`,
    CANCEL_ORDER: `${API_BASE_URL}/api/markets/orders/`,
  }
};

export default API_BASE_URL;
