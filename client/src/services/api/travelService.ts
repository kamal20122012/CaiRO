import { ApiClient } from './apiClient';
import { Flight, Hotel, ItineraryData } from '@/types/components/Itinerary';
import { TripFormOutput } from '@/types/components/TripForm';

export class TravelService {
  private static instance: TravelService;
  private apiClient: ApiClient;

  private constructor() {
    this.apiClient = ApiClient.getInstance();
  }

  public static getInstance(): TravelService {
    if (!TravelService.instance) {
      TravelService.instance = new TravelService();
    }
    return TravelService.instance;
  }

  async generateFlight(tripData: TripFormOutput): Promise<Flight> {
    const response = await this.apiClient.getAxiosInstance().post('/flights/generate', tripData);
    return response.data;
  }

  async generateHotel(tripData: TripFormOutput): Promise<Hotel> {
    const response = await this.apiClient.getAxiosInstance().post('/hotels/generate', tripData);
    return response.data;
  }

  async generateItinerary(tripData: TripFormOutput): Promise<ItineraryData> {
    const response = await this.apiClient.getAxiosInstance().post('/itinerary/generate', tripData);
    return response.data;
  }
}