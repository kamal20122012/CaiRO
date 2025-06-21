import React from 'react';
import { Flight, Hotel } from '@/types/components/Itinerary';
import './TravelCard.css';

interface TravelCardProps {
  type: 'flight' | 'hotel';
  data: Flight | Hotel;
}

export const TravelCard: React.FC<TravelCardProps> = ({ type, data }) => {
  if (type === 'flight') {
    const flight = data as Flight;
    return (
      <div className="travel-card flight-card">
        <div className="travel-card__header">
          <span className="travel-card__time">{flight.date}</span>
          <h3 className="travel-card__name">{flight.name}</h3>
        </div>
        
        <div className="travel-card__main">
          <div className="flight-route">
            <div className="flight-endpoint">
              <span className="flight-time">{flight.departureTime}</span>
              <span className="flight-location">{flight.source}</span>
            </div>
            <span className="flight-arrow">→</span>
            <div className="flight-endpoint">
              <span className="flight-time">{flight.arrivalTime}</span>
              <span className="flight-location">{flight.destination}</span>
            </div>
          </div>
        </div>

        <div className="travel-card__footer">
          <span className="travel-card__price">{flight.price}</span>
        </div>
      </div>
    );
  }

  const hotel = data as Hotel;
  return (
    <div className="travel-card hotel-card">
      <div className="travel-card__header">
        <div className="hotel-rating">
          {'★'.repeat(hotel.rating)}{'☆'.repeat(5-hotel.rating)}
        </div>
        <h3 className="travel-card__name">{hotel.name}</h3>
      </div>

      <div className="travel-card__main">
        <div className="hotel-dates">
          <span>{hotel.checkIn} → {hotel.checkOut}</span>
        </div>
        <div className="hotel-location">📍 {hotel.location}</div>
      </div>

      <div className="travel-card__footer">
        <span className="travel-card__price">₹{hotel.price}/night</span>
      </div>
    </div>
  );
};