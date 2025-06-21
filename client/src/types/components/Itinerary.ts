// Base interface for common properties
interface BaseActivity {
    name: string;
    location: string;
    price: number;
  }
  
  export interface Activity {
    time: string;
    name: string;
    location: string;
    description: string;
    image?: string;
    link?: string;
    tags?: string[];
  }
  
  export interface DayPlan {
    day: number;
    title: string;
    narrative: string;
    activities: Activity[];
  }
  
  export interface Hotel extends BaseActivity {
    checkIn: string;
    checkOut: string;
    rating: number;
  }
  
  export interface Flight extends BaseActivity {
    date: string;
    departureTime: string;
    arrivalTime: string;
    source: string;
    destination: string;
  }
  
  export interface ItineraryData {
    title: string;
    overview: string;
    days: DayPlan[];
  }