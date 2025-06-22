export const APP_CONFIG = {
      API_BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:3001/api',
  APP_NAME: import.meta.env.VITE_APP_NAME || 'AI Travel Planner',
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  } as const;
  
  export const TRAVEL_STYLES = {
    ADVENTURE: 'adventure',
    RELAXATION: 'relaxation',
    CULTURAL: 'cultural',
    LUXURY: 'luxury',
  } as const;
  
  export const BUDGET_LEVELS = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
  } as const;