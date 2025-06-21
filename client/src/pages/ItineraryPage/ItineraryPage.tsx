import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ActionButton } from '@/components/ActionButton/ActionButton';
import { ItineraryDay } from '@/components/Itinerary/ItineraryDay';
import { TravelCard } from '@/components/Itinerary/TravelCard';
import { Loader } from '@/components/common/Loader';
import { useTripGeneration } from '@/hooks/useTripGeneration';
import { TripFormOutput } from '@/types/components/TripForm';
import './ItineraryPage.css';

export const ItineraryPage: React.FC<{ tripFormData: TripFormOutput }> = ({ tripFormData }) => {
  const navigate = useNavigate();
  
  const {
    flight,
    hotel,
    itinerary,
    loadingStates,
    error
  } = useTripGeneration(tripFormData);

  if (error) {
    return (
      <div className="itinerary-page">
        <div className="itinerary-page__error">
          <h2>Error</h2>
          <p>{error}</p>
          <ActionButton
            label="Back to Planner"
            icon="←"
            onClick={() => navigate('/plan-trip')}
            variant="secondary"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="itinerary-page">
      <div className="itinerary-page__header">
        <ActionButton
          label="Back to Planner"
          icon="←"
          onClick={() => navigate('/plan-trip')}
          variant="secondary"
        />
        <h1 className="itinerary-page__title">Your Travel Plan</h1>
        <p className="itinerary-page__overview">
          {itinerary?.overview || 'Generating your perfect travel experience...'}
        </p>
      </div>

      <div className="itinerary-page__content">
        <aside className="itinerary-page__sidebar">
          <section className="travel-section">
            <h2 className="travel-section__title">Flight</h2>
            {loadingStates.flights ? (
              <Loader text="Finding the best flight..." />
            ) : flight && (
              <TravelCard 
                type="flight" 
                data={flight} 
              />
            )}
          </section>

          <section className="travel-section">
            <h2 className="travel-section__title">Accommodation</h2>
            {loadingStates.accommodations ? (
              <Loader text="Finding your perfect stay..." />
            ) : hotel && (
              <TravelCard 
                type="hotel" 
                data={hotel} 
              />
            )}
          </section>
        </aside>

        <main className="itinerary-page__main">
          <h2 className="travel-section__title">Daily Itinerary</h2>
          {loadingStates.dailyItinerary ? (
            <Loader text="Crafting your daily adventures..." />
          ) : itinerary && (
            <div className="itinerary-page__days">
              {itinerary.days.map((day) => (
                <ItineraryDay key={day.day} day={day} />
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};