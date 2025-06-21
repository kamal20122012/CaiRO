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
  
  export interface ItineraryData {
    title: string;
    overview: string;
    days: DayPlan[];
  }