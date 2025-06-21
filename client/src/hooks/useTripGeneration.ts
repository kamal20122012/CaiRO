import { useState, useEffect } from 'react';
import { Flight, Hotel, ItineraryData } from '@/types/components/Itinerary';
import { TravelService } from '@/services/api/travelService';
import { TripFormOutput } from '@/types/components/TripForm';

interface TripGenerationState {
  flight: Flight | null;
  hotel: Hotel | null;
  itinerary: ItineraryData | null;
  loadingStates: {
    flights: boolean;
    accommodations: boolean;
    dailyItinerary: boolean;
  };
  error: string | null;
}

export const useTripGeneration = (tripFormData: TripFormOutput) => {
  const [state, setState] = useState<TripGenerationState>({
    flight: null,
    hotel: null,
    itinerary: null,
    loadingStates: {
      flights: true,
      accommodations: true,
      dailyItinerary: true
    },
    error: null
  });

  useEffect(() => {
    const travelService = TravelService.getInstance();

    const generateAll = async () => {
      try {
        // Start all requests in parallel
        const [flightPromise, hotelPromise, itineraryPromise] = [
          travelService.generateFlight(tripFormData),
          travelService.generateHotel(tripFormData),
          travelService.generateItinerary(tripFormData)
        ];

        // Handle flight
        flightPromise
          .then(flight => {
            setState(prev => ({
              ...prev,
              flight,
              loadingStates: { ...prev.loadingStates, flights: false }
            }));
          })
          .catch(err => {
            console.error('Flight generation error:', err);
            setState(prev => ({
              ...prev,
              error: 'Failed to generate flight options',
              loadingStates: { ...prev.loadingStates, flights: false }
            }));
          });

        // Handle hotel
        hotelPromise
          .then(hotel => {
            setState(prev => ({
              ...prev,
              hotel,
              loadingStates: { ...prev.loadingStates, accommodations: false }
            }));
          })
          .catch(err => {
            console.error('Hotel generation error:', err);
            setState(prev => ({
              ...prev,
              error: 'Failed to generate hotel options',
              loadingStates: { ...prev.loadingStates, accommodations: false }
            }));
          });

        // Handle itinerary
        itineraryPromise
          .then(itinerary => {
            setState(prev => ({
              ...prev,
              itinerary,
              loadingStates: { ...prev.loadingStates, dailyItinerary: false }
            }));
          })
          .catch(err => {
            console.error('Itinerary generation error:', err);
            setState(prev => ({
              ...prev,
              error: 'Failed to generate daily itinerary',
              loadingStates: { ...prev.loadingStates, dailyItinerary: false }
            }));
          });
      } catch (err) {
        console.error('Generation error:', err);
        setState(prev => ({
          ...prev,
          error: 'Failed to generate trip details',
          loadingStates: {
            flights: false,
            accommodations: false,
            dailyItinerary: false
          }
        }));
      }
    };

    generateAll();
  }, [tripFormData]);

  return {
    ...state
  };
};