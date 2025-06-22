export interface TripFormData {
    vibe: string;
    source: string;
    destination: string;
    departureDate: string;
    arrivalDate: string;
    activities: string[];
    beenBefore: boolean;
    sourceConfirmed: boolean;
    destinationConfirmed: boolean;
  }
  
  export interface TripFormOutput {
    source: string;
    destination: string;
    departureDate: string;
    arrivalDate: string;
    days: number;
    trip_theme: string;
    user_mood: string;
    vibe_keywords: string[];
    activities: string[];
    avoid: string[];
    been_here_before: boolean;
  }