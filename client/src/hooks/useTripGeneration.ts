import { useState, useEffect, useRef, useMemo } from 'react';
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

  const isGeneratingRef = useRef(false);
  
  // Memoize tripFormData to prevent unnecessary re-renders
  const memoizedTripFormData = useMemo(() => tripFormData, [
    tripFormData.source,
    tripFormData.destination,
    tripFormData.departureDate,
    tripFormData.arrivalDate,
    tripFormData.days,
    tripFormData.trip_theme,
    tripFormData.activities
  ]);

  useEffect(() => {
    // Prevent duplicate calls
    if (isGeneratingRef.current) {
      console.log('🚫 [TRIP GENERATION] Request already in progress, skipping...');
      return;
    }

    console.log('🚀 [TRIP GENERATION] Starting trip generation with data:', {
      tripFormData: memoizedTripFormData,
      timestamp: new Date().toISOString()
    });

    isGeneratingRef.current = true;
    const travelService = TravelService.getInstance();
    const generationStartTime = performance.now();

    const generateAll = async () => {
      try {
        // Start all requests in parallel
        console.log('🔄 [TRIP GENERATION] Initiating parallel API calls...');
        
        const [flightPromise, hotelPromise, itineraryPromise] = [
          travelService.generateFlight(memoizedTripFormData),
          travelService.generateHotel(memoizedTripFormData),
          travelService.generateItinerary(memoizedTripFormData)
        ];

        // Handle flight
        flightPromise
          .then(flight => {
            const flightTime = performance.now();
            console.log('✅ [TRIP GENERATION] Flight data received and processed:', {
              flight,
              processingTime: `${(flightTime - generationStartTime).toFixed(2)}ms`,
              isValidStructure: !!(flight?.name && flight?.price && flight?.departureTime),
              flightDetails: {
                airline: flight?.name,
                route: `${flight?.source} → ${flight?.destination}`,
                time: `${flight?.departureTime} - ${flight?.arrivalTime}`,
                price: flight?.price,
                date: flight?.date
              }
            });

            setState(prev => ({
              ...prev,
              flight,
              loadingStates: { ...prev.loadingStates, flights: false }
            }));
          })
          .catch(err => {
            const errorTime = performance.now();
            console.error('❌ [TRIP GENERATION] Flight generation failed:', {
              error: err,
              errorMessage: err instanceof Error ? err.message : 'Unknown error',
              processingTime: `${(errorTime - generationStartTime).toFixed(2)}ms`,
              requestData: {
                source: memoizedTripFormData.source,
                destination: memoizedTripFormData.destination,
                date: memoizedTripFormData.departureDate
              }
            });

            setState(prev => ({
              ...prev,
              error: 'Failed to generate flight options',
              loadingStates: { ...prev.loadingStates, flights: false }
            }));
          });

        // Handle hotel
        hotelPromise
          .then(hotel => {
            const hotelTime = performance.now();
            console.log('✅ [TRIP GENERATION] Hotel data received and processed:', {
              hotel,
              processingTime: `${(hotelTime - generationStartTime).toFixed(2)}ms`,
              isValidStructure: !!(hotel?.name && hotel?.price && hotel?.location),
              hotelDetails: {
                name: hotel?.name,
                location: hotel?.location,
                rating: hotel?.rating,
                pricePerNight: hotel?.price,
                checkIn: hotel?.checkIn,
                checkOut: hotel?.checkOut
              }
            });

            setState(prev => ({
              ...prev,
              hotel,
              loadingStates: { ...prev.loadingStates, accommodations: false }
            }));
          })
          .catch(err => {
            const errorTime = performance.now();
            console.error('❌ [TRIP GENERATION] Hotel generation failed:', {
              error: err,
              errorMessage: err instanceof Error ? err.message : 'Unknown error',
              processingTime: `${(errorTime - generationStartTime).toFixed(2)}ms`,
              requestData: {
                destination: memoizedTripFormData.destination,
                checkIn: memoizedTripFormData.departureDate,
                checkOut: memoizedTripFormData.arrivalDate
              }
            });

            setState(prev => ({
              ...prev,
              error: 'Failed to generate hotel options',
              loadingStates: { ...prev.loadingStates, accommodations: false }
            }));
          });

        // Handle itinerary
        itineraryPromise
          .then(itinerary => {
            const itineraryTime = performance.now();
            console.log('✅ [TRIP GENERATION] Itinerary data received and processed:', {
              itinerary,
              processingTime: `${(itineraryTime - generationStartTime).toFixed(2)}ms`,
              isValidStructure: !!(itinerary?.title && itinerary?.days && Array.isArray(itinerary.days)),
              itineraryDetails: {
                title: itinerary?.title,
                overview: itinerary?.overview?.substring(0, 100) + '...',
                daysCount: Array.isArray(itinerary?.days) ? itinerary.days.length : 0,
                firstDayPreview: itinerary?.days?.[0] ? {
                  day: itinerary.days[0].day,
                  title: itinerary.days[0].title,
                  activitiesCount: Array.isArray(itinerary.days[0].activities) ? itinerary.days[0].activities.length : 0
                } : null,
                totalActivities: Array.isArray(itinerary?.days) 
                  ? itinerary.days.reduce((sum, day) => sum + (Array.isArray(day.activities) ? day.activities.length : 0), 0)
                  : 0
              }
            });

            setState(prev => ({
              ...prev,
              itinerary,
              loadingStates: { ...prev.loadingStates, dailyItinerary: false }
            }));
          })
          .catch(err => {
            const errorTime = performance.now();
            console.error('❌ [TRIP GENERATION] Itinerary generation failed:', {
              error: err,
              errorMessage: err instanceof Error ? err.message : 'Unknown error',
              processingTime: `${(errorTime - generationStartTime).toFixed(2)}ms`,
              requestData: {
                destination: memoizedTripFormData.destination,
                days: memoizedTripFormData.days,
                theme: memoizedTripFormData.trip_theme
              }
            });

            setState(prev => ({
              ...prev,
              error: 'Failed to generate daily itinerary',
              loadingStates: { ...prev.loadingStates, dailyItinerary: false }
            }));
          });

        // Wait for all promises to settle and log final summary
        Promise.allSettled([flightPromise, hotelPromise, itineraryPromise])
          .then(results => {
            const totalTime = performance.now();
            const summary = {
              totalProcessingTime: `${(totalTime - generationStartTime).toFixed(2)}ms`,
              results: {
                flight: results[0].status === 'fulfilled' ? '✅ Success' : `❌ Failed: ${results[0].status === 'rejected' ? results[0].reason?.message : 'Unknown'}`,
                hotel: results[1].status === 'fulfilled' ? '✅ Success' : `❌ Failed: ${results[1].status === 'rejected' ? results[1].reason?.message : 'Unknown'}`,
                itinerary: results[2].status === 'fulfilled' ? '✅ Success' : `❌ Failed: ${results[2].status === 'rejected' ? results[2].reason?.message : 'Unknown'}`
              },
              successfulRequests: results.filter(r => r.status === 'fulfilled').length,
              failedRequests: results.filter(r => r.status === 'rejected').length
            };

            console.log('🎯 [TRIP GENERATION] All requests completed - Final Summary:', summary);
            
            if (summary.successfulRequests === 3) {
              console.log('🎉 [TRIP GENERATION] All data successfully generated and ready for display!');
            } else if (summary.successfulRequests > 0) {
              console.warn('⚠️ [TRIP GENERATION] Partial success - some data may be missing');
            } else {
              console.error('💥 [TRIP GENERATION] All requests failed - no data available');
            }
          })
          .finally(() => {
            // Reset the flag when all requests are done
            isGeneratingRef.current = false;
          });

      } catch (err) {
        const errorTime = performance.now();
        console.error('💥 [TRIP GENERATION] Critical error during generation:', {
          error: err,
          errorMessage: err instanceof Error ? err.message : 'Unknown error',
          processingTime: `${(errorTime - generationStartTime).toFixed(2)}ms`,
          tripFormData: memoizedTripFormData
        });

        setState(prev => ({
          ...prev,
          error: 'Failed to generate trip details',
          loadingStates: {
            flights: false,
            accommodations: false,
            dailyItinerary: false
          }
        }));
        
        // Reset the flag on error as well
        isGeneratingRef.current = false;
      }
    };

    generateAll();
  }, [memoizedTripFormData]);

  // Log state changes for debugging
  useEffect(() => {
    console.log('📊 [TRIP GENERATION] State updated:', {
      hasFlightData: !!state.flight,
      hasHotelData: !!state.hotel,
      hasItineraryData: !!state.itinerary,
      loadingStates: state.loadingStates,
      error: state.error,
      timestamp: new Date().toISOString()
    });
  }, [state]);

  return {
    ...state
  };
};