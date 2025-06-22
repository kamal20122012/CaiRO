import React, { useState } from 'react';
import { Activity } from '@/types/components/Itinerary';
import './ActivityCard.css';

interface ActivityCardProps {
  activity: Activity;
}

export const ActivityCard: React.FC<ActivityCardProps> = ({ activity }) => {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // Fallback image URLs in order of preference
  const fallbackImages = [
    'https://via.placeholder.com/400x300/8B5CF6/FFFFFF?text=Travel+Activity',
    'https://picsum.photos/400/300?random=100',
    'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDQwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjOEI1Q0Y2Ii8+Cjx0ZXh0IHg9IjIwMCIgeT0iMTUwIiBmaWxsPSJ3aGl0ZSIgZm9udC1zaXplPSIxOCIgZm9udC1mYW1pbHk9IkFyaWFsIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+VHJhdmVsIEFjdGl2aXR5PC90ZXh0Pgo8L3N2Zz4K'
  ];

  const handleImageError = () => {
    setImageError(true);
    setImageLoading(false);
  };

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  // Determine which image to show
  const getImageSrc = () => {
    if (!activity.image || imageError) {
      return fallbackImages[0]; // Use the first fallback
    }
    return activity.image;
  };

  return (
    <div className="activity-card">
      <div className="activity-card__image-container">
        {/* Always show an image, whether it's the activity image or fallback */}
        <img 
          src={getImageSrc()}
          alt={activity.name || 'Travel Activity'} 
          className={`activity-card__image ${imageLoading ? 'loading' : ''}`}
          onError={handleImageError}
          onLoad={handleImageLoad}
          loading="lazy"
        />
        {imageLoading && (
          <div className="activity-card__image-loader">
            <div className="loader-spinner"></div>
          </div>
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