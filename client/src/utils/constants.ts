export const APP_CONFIG = {
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:3001/api',
    APP_NAME: process.env.REACT_APP_NAME || 'AI Travel Planner',
    VERSION: process.env.REACT_APP_VERSION || '1.0.0',
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