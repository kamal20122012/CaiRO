import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import { TravelPlanner } from '@/components/TravelPlanner/TravelPlanner';
import { PlanTrip } from '@/pages/PlanTrip/PlanTrip';
import { ItineraryPage } from '@/pages/ItineraryPage/ItineraryPage';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<TravelPlanner />} />
          <Route path="/plan-trip" element={<PlanTrip />} />
          <Route path="/itinerary" element={<ItineraryPage />} />
          <Route path="*" element={<Navigate to="/plan-trip" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;