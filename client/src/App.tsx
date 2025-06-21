import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { TravelPlanner } from '@/components/TravelPlanner/TravelPlanner';
import { PlanTrip } from '@/pages/PlanTrip/PlanTrip';
import { ItineraryPage } from '@/pages/ItineraryPage/ItineraryPage';

// This is temporary mock data until we integrate with the backend
const sampleItinerary = {
  title: "A Gentle Unfolding: 3 Days in Kyoto",
  overview: "This trip is built around moments of peace, rhythm, and soft immersion...",
  days: [
    {
      day: 1,
      title: "Arrival & First Breaths",
      narrative: "You arrive and step into the quiet elegance of Kyoto's backstreets...",
      activities: [
        {
          time: "Afternoon",
          name: "Check-in & Relax",
          location: "Gion Ryokan",
          description: "Traditional stay with garden view",
          image: "https://akm-img-a-in.tosshub.com/sites/dailyo//resources/202301/indog-2-1200090123105636.jpeg?size=*:480",
          link: "https://maps.google.com/...",
          tags: ["calm", "authentic", "arrival"]
        }
      ]
    },
    {
      day: 1,
      title: "Arrival & First Breaths",
      narrative: "You arrive and step into the quiet elegance of Kyoto's backstreets...",
      activities: [
        {
          time: "Afternoon",
          name: "Check-in & Relax",
          location: "Gion Ryokan",
          description: "Traditional stay with garden view",
          image: "https://akm-img-a-in.tosshub.com/sites/dailyo//resources/202301/indog-2-1200090123105636.jpeg?size=*:480",
          link: "https://maps.google.com/...",
          tags: ["calm", "authentic", "arrival"]
        }
      ]
    }
  ]
};

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<TravelPlanner />} />
          <Route path="/plan-trip" element={<PlanTrip />} />
          <Route 
            path="/itinerary" 
            element={<ItineraryPage itinerary={sampleItinerary} />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;