/**
 * NASA-Grade API Configuration
 * Auto-detects environment and provides optimized backend endpoints.
 */

const IS_PRODUCTION = window.location.hostname !== 'localhost';

export const BACKEND_URL = IS_PRODUCTION
    ? 'https://ai-saas-backend-ds91.onrender.com'
    : (import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000');

export const API_ENDPOINTS = {
    CHAT: `${BACKEND_URL}/api/chat`,
    IMAGE_GEN: `${BACKEND_URL}/api/generate/image`,
    CEO_ADVISOR: `${BACKEND_URL}/ceo-advisor`,
    ANTIGRAVITY_METRICS: `${BACKEND_URL}/antigravity/metrics`,
    ANTIGRAVITY_ACTIVATE: `${BACKEND_URL}/antigravity/activate`,
    CHECKOUT: `${BACKEND_URL}/api/checkout`,
    HEALTH: `${BACKEND_URL}/api/health`,
};

console.log(`[ANTIGRAVITY V2] Running in ${IS_PRODUCTION ? 'PRODUCTION' : 'DEVELOPMENT'} mode`);
console.log(`[ANTIGRAVITY V2] Backend Target: ${BACKEND_URL}`);
