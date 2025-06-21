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
    console.log('🛫 [FLIGHT API] Requesting flight data with:', {
      source: tripData.source,
      destination: tripData.destination,
      departureDate: tripData.departureDate,
      tripFormData: tripData
    });
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.getAxiosInstance().post('/flights/generate', tripData);
      const endTime = performance.now();
      
      console.log('✅ [FLIGHT API] Response received:', {
        status: response.status,
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        rawResponse: response.data,
        dataStructure: {
          hasStatus: 'status' in response.data,
          hasData: 'data' in response.data,
          responseKeys: Object.keys(response.data),
          dataKeys: response.data?.data ? Object.keys(response.data.data) : 'No data field'
        }
      });
      
      // Validate and extract flight data
      const flightData = response.data?.data || response.data;
      
      console.log('🔍 [FLIGHT API] Parsed flight data:', {
        flightData,
        isValidFlight: this.validateFlightData(flightData),
        requiredFields: {
          name: !!flightData?.name,
          price: !!flightData?.price,
          departureTime: !!flightData?.departureTime,
          arrivalTime: !!flightData?.arrivalTime,
          source: !!flightData?.source,
          destination: !!flightData?.destination,
          date: !!flightData?.date
        }
      });
      
      return flightData;
    } catch (error) {
      const endTime = performance.now();
      console.error('❌ [FLIGHT API] Request failed:', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        error: error,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
        errorStack: error instanceof Error ? error.stack : undefined
      });
      throw error;
    }
  }

  async generateHotel(tripData: TripFormOutput): Promise<Hotel> {
    console.log('🏨 [HOTEL API] Requesting hotel data with:', {
      destination: tripData.destination,
      departureDate: tripData.departureDate,
      arrivalDate: tripData.arrivalDate,
      tripFormData: tripData
    });
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.getAxiosInstance().post('/hotels/generate', tripData);
      const endTime = performance.now();
      
      console.log('✅ [HOTEL API] Response received:', {
        status: response.status,
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        rawResponse: response.data,
        dataStructure: {
          hasStatus: 'status' in response.data,
          hasData: 'data' in response.data,
          responseKeys: Object.keys(response.data),
          dataKeys: response.data?.data ? Object.keys(response.data.data) : 'No data field'
        }
      });
      
      // Validate and extract hotel data
      const hotelData = response.data?.data || response.data;
      
      console.log('🔍 [HOTEL API] Parsed hotel data:', {
        hotelData,
        isValidHotel: this.validateHotelData(hotelData),
        requiredFields: {
          name: !!hotelData?.name,
          price: !!hotelData?.price,
          location: !!hotelData?.location,
          rating: !!hotelData?.rating,
          checkIn: !!hotelData?.checkIn,
          checkOut: !!hotelData?.checkOut
        }
      });
      
      return hotelData;
    } catch (error) {
      const endTime = performance.now();
      console.error('❌ [HOTEL API] Request failed:', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        error: error,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
        errorStack: error instanceof Error ? error.stack : undefined
      });
      throw error;
    }
  }

  async generateItinerary(tripData: TripFormOutput): Promise<ItineraryData> {
    console.log('🗓️ [ITINERARY API] Requesting itinerary data with:', {
      destination: tripData.destination,
      days: tripData.days,
      theme: tripData.trip_theme,
      activities: tripData.activities,
      tripFormData: tripData
    });
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.getAxiosInstance().post('/itinerary/generate', tripData);
      const endTime = performance.now();
      
      console.log('✅ [ITINERARY API] Response received:', {
        status: response.status,
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        rawResponse: response.data,
        dataStructure: {
          hasStatus: 'status' in response.data,
          hasData: 'data' in response.data,
          responseKeys: Object.keys(response.data),
          dataKeys: response.data?.data ? Object.keys(response.data.data) : 'No data field'
        }
      });
      
      // Validate and extract itinerary data
      const itineraryData = response.data?.data || response.data;
      
      console.log('🔍 [ITINERARY API] Parsed itinerary data:', {
        itineraryData,
        isValidItinerary: this.validateItineraryData(itineraryData),
        structure: {
          hasTitle: !!itineraryData?.title,
          hasOverview: !!itineraryData?.overview,
          hasDays: !!itineraryData?.days,
          daysCount: Array.isArray(itineraryData?.days) ? itineraryData.days.length : 0,
          firstDayStructure: itineraryData?.days?.[0] ? {
            hasDay: !!itineraryData.days[0].day,
            hasTitle: !!itineraryData.days[0].title,
            hasNarrative: !!itineraryData.days[0].narrative,
            hasActivities: !!itineraryData.days[0].activities,
            activitiesCount: Array.isArray(itineraryData.days[0].activities) ? itineraryData.days[0].activities.length : 0
          } : 'No days data'
        }
      });
      
      return itineraryData;
    } catch (error) {
      const endTime = performance.now();
      console.error('❌ [ITINERARY API] Request failed:', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        error: error,
        errorMessage: error instanceof Error ? error.message : 'Unknown error',
        errorStack: error instanceof Error ? error.stack : undefined
      });
      throw error;
    }
  }

  async updateItinerary(userRequest: string): Promise<ItineraryData> {
    console.log('🔄 [ITINERARY API] Requesting itinerary update with:', {
      userRequest
    });
    
    const startTime = performance.now();
    
    try {
      const response = await this.apiClient.getAxiosInstance().post('/itinerary/update', {
        user_request: userRequest
      });
      
      const endTime = performance.now();
      console.log('✅ [ITINERARY API] Update response received:', {
        status: response.status,
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        rawResponse: response.data
      });
      
      const updatedItinerary = response.data?.data || response.data;
      
      if (!this.validateItineraryData(updatedItinerary)) {
        throw new Error('Invalid itinerary data received');
      }
      
      return updatedItinerary;
    } catch (error) {
      const endTime = performance.now();
      console.error('❌ [ITINERARY API] Update request failed:', {
        duration: `${(endTime - startTime).toFixed(2)}ms`,
        error: error
      });
      throw error;
    }
  }

  // Validation helper methods
  private validateFlightData(data: any): boolean {
    return !!(data?.name && data?.price && data?.departureTime && data?.arrivalTime && data?.source && data?.destination);
  }

  private validateHotelData(data: any): boolean {
    return !!(data?.name && data?.price && data?.location && data?.rating);
  }

  private validateItineraryData(data: any): boolean {
    return !!(data?.title && data?.overview && Array.isArray(data?.days) && data.days.length > 0);
  }
}