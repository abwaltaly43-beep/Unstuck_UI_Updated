// Centralized API configuration
// In production builds (Docker / AWS), use relative paths so Nginx proxies /api/ directly to backend
export const API_BASE = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : (import.meta.env.PROD ? '' : 'http://localhost:8000');

export default API_BASE;
