import React from 'react';
import { Activity } from '@/types/components/Itinerary';
import './ActivityCard.css';

interface ActivityCardProps {
  activity: Activity;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({ activity }) => {
  return (
    <div className="activity-card">
      <div className="activity-card__image-container">
        {activity.image && (
          <img 
            src={activity.image} 
            alt={activity.name} 
            className="activity-card__image"
          />
        )}
      </div>
      <div className="activity-card__content">
        <div className="activity-card__main-info">
          <span className="activity-card__time">{activity.time}</span>
          <h3 className="activity-card__name">{activity.name}</h3>
          
          {activity.location && (
            <a 
              href={activity.link || `https://maps.google.com/search?q=${encodeURIComponent(activity.location)}`}
              className="activity-card__location"
              target="_blank"
              rel="noopener noreferrer"
            >
              📍 {activity.location}
            </a>
          )}
          
          <p className="activity-card__description">{activity.description}</p>
        </div>
        
        {activity.tags && activity.tags.length > 0 && (
          <div className="activity-card__tags">
            {activity.tags.map((tag, index) => (
              <span key={index} className="activity-card__tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};