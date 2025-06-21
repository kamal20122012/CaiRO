import { TripPlan, ItineraryItem, Memory } from '@/types';

export class TravelPlannerService {
  private static instance: TravelPlannerService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';
  }

  public static getInstance(): TravelPlannerService {
    if (!TravelPlannerService.instance) {
      TravelPlannerService.instance = new TravelPlannerService();
    }
    return TravelPlannerService.instance;
  }

  async planTrip(destination: string, preferences: any): Promise<TripPlan> {
    // TODO: Integrate with AI backend
    const response = await fetch(`${this.baseUrl}/plan-trip`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ destination, preferences }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to plan trip');
    }
    
    return response.json();
  }

  async getMemories(): Promise<Memory[]> {
    // TODO: Fetch user memories from backend
    const response = await fetch(`${this.baseUrl}/memories`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch memories');
    }
    
    return response.json();
  }

  async getSuggestions(userId: string): Promise<string[]> {
    // TODO: Get AI-powered suggestions
    const response = await fetch(`${this.baseUrl}/suggestions/${userId}`);
    
    if (!response.ok) {
      throw new Error('Failed to get suggestions');
    }
    
    return response.json();
  }

  async getItineraries(): Promise<TripPlan[]> {
    // TODO: Fetch saved itineraries
    const response = await fetch(`${this.baseUrl}/itineraries`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch itineraries');
    }
    
    return response.json();
  }
}