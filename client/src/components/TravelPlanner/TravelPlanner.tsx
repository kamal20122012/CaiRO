import React from 'react';
import { ActionButton } from '@/components/ActionButton/ActionButton';
import { useTravelPlanner } from '@/hooks/useTravelPlanner';
import './TravelPlanner.css';

export const TravelPlanner: React.FC = () => {
  const { handleAction } = useTravelPlanner();

  return (
    <div className="travel-planner">
      <div className="travel-planner__background">
        <div className="travel-planner__constellation"></div>
      </div>
      
      <div className="travel-planner__content">
        <h1 className="travel-planner__title">Journee</h1>
        <p className="travel-planner__subtitle">
          Where every journey becomes a story worth telling
        </p>
        
        <div className="travel-planner__actions">
          <ActionButton
            label="Begin Your Tale"
            icon="✧"
            onClick={() => handleAction('plan-trip')}
            variant="primary"
          />
          <ActionButton
            label="Past Adventures"
            icon="✧"
            onClick={() => handleAction('view-memories')}
            variant="secondary"
          />
        </div>
      </div>
    </div>
  );
};