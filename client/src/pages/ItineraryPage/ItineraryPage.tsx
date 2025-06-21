import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ActionButton } from '@/components/ActionButton/ActionButton';
import { ItineraryDay } from '@/components/Itinerary/ItineraryDay';
import { ItineraryData } from '@/types/components/Itinerary';
import './ItineraryPage.css';

interface ItineraryPageProps {
  itinerary: ItineraryData;
}

export const ItineraryPage: React.FC<ItineraryPageProps> = ({ itinerary }) => {
  const navigate = useNavigate();

  return (
    <div className="itinerary-page">
      <div className="itinerary-page__header">
        <ActionButton
          label="Back to Planner"
          icon="←"
          onClick={() => navigate('/plan-trip')}
          variant="secondary"
        />
        <h1 className="itinerary-page__title">{itinerary.title}</h1>
        <p className="itinerary-page__overview">{itinerary.overview}</p>
      </div>
      
      <div className="itinerary-page__days">
        {itinerary.days.map((day) => (
          <ItineraryDay key={day.day} day={day} />
        ))}
      </div>
    </div>
  );
};