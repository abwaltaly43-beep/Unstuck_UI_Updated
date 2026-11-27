// Centralized API configuration for Unstuck
// Whenever running on a server (like AWS IP 16.171.133.147 or any production domain),
// ALWAYS use relative path "" so Nginx proxies /api/ requests to the backend container automatically.
export const API_BASE = (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')
  ? ''
  : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

export default API_BASE;
