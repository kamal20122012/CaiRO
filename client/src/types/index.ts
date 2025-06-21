export interface TripPlan {
    id: string;
    destination: string;
    startDate: Date;
    endDate: Date;
    itinerary: ItineraryItem[];
    memories: Memory[];
  }
  
  export interface ItineraryItem {
    id: string;
    day: number;
    time: string;
    activity: string;
    location: string;
    description: string;
  }
  
  export interface Memory {
    id: string;
    tripId: string;
    title: string;
    description: string;
    date: Date;
    location: string;
    tags: string[];
  }
  
  export interface User {
    id: string;
    name: string;
    email: string;
    preferences: UserPreferences;
  }
  
  export interface UserPreferences {
    travelStyle: 'adventure' | 'relaxation' | 'cultural' | 'luxury';
    budget: 'low' | 'medium' | 'high';
    preferredDestinations: string[];
    dietaryRestrictions: string[];
  }
  
  export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
  }
  
  export interface TravelPlannerState {
    user: User | null;
    currentTrip: TripPlan | null;
    memories: Memory[];
    itineraries: TripPlan[];
    loading: boolean;
    error: string | null;
  }