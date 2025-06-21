import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import { TravelPlanner } from '@/components/TravelPlanner/TravelPlanner';
import { PlanTrip } from '@/pages/PlanTrip/PlanTrip';
import { ItineraryPage } from '@/pages/ItineraryPage/ItineraryPage';
import { ItineraryData } from './types/components/Itinerary';

// This is temporary mock data until we integrate with the backend
const sampleItinerary: ItineraryData = {
  title: "A Gentle Unfolding: 3 Days in Kyoto",
  overview: "This trip is built around moments of peace, rhythm, and soft immersion...",
  days: [
    // ... existing day activities ...
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
          image: "https://example.com/ryokan.jpg",
          link: "https://maps.google.com/...",
          tags: ["calm", "authentic", "arrival"]
        },
        {
          time: "Evening",
          name: "Night Walk",
          location: "Gion District",
          description: "Walk under lantern-lit paths and historic alleyways",
          image: "https://example.com/gion.jpg",
          link: "https://maps.google.com/...",
          tags: ["romantic", "night", "historical"]
        }
      ]
    }
  ],
  travelArrangements: {
    flights: [
      {
        date: "2024-03-20",
        departureTime: "10:30",
        arrivalTime: "14:45",
        name: "Japan Airlines JL750",
        price: 45000,
        source: "Delhi",
        destination: "Kyoto",
        location: "Terminal 3" // For consistency with BaseActivity
      }
    ],
    hotels: [
      {
        name: "Gion Ryokan Karaku",
        location: "Gion District, Kyoto",
        price: 15000,
        checkIn: "2024-03-20",
        checkOut: "2024-03-23",
        rating: 4
      }
    ]
  }
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