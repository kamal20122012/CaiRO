import React from 'react';
import { ActivityCard } from './ActivityCard';
import { DayPlan } from '@/types/components/Itinerary';
import './ItineraryDay.css';

interface ItineraryDayProps {
  day: DayPlan;
}

export const ItineraryDay: React.FC<ItineraryDayProps> = ({ day }) => {
  return (
    <section className="itinerary-day">
      <div className="itinerary-day__header">
        <h2 className="itinerary-day__title">Day {day.day}: {day.title}</h2>
        <p className="itinerary-day__narrative">{day.narrative}</p>
      </div>
      
      <div className="itinerary-day__activities">
        {day.activities.map((activity, index) => (
          <ActivityCard key={index} activity={activity} />
        ))}
      </div>
    </section>
  );
};