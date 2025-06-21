import React, { useState } from 'react';
import { ActionButton } from '@/components/ActionButton/ActionButton';
import './TripForm.css';

interface TripFormData {
  vibe: string;
  source: string;
  destination: string;
  departureDate: string;
  arrivalDate: string;
  activities: string[];
  duration: number;
  beenBefore: boolean;
}

interface TripFormOutput {
  source: string;
  destination: string;
  departureDate: string;
  arrivalDate: string;
  days: number;
  trip_theme: string;
  user_mood: string;
  vibe_keywords: string[];
  activities: string[];
  avoid: string[];
  been_here_before: boolean;
}

const ACTIVITIES = [
  'Long walks',
  'People watching',
  'Tea/coffee rituals',
  'Photography',
  'Hiking alone',
  'Art galleries',
  'Historical sites',
  'Just surprise me'
];

export const TripForm: React.FC = () => {
  const [formData, setFormData] = useState<TripFormData>({
    vibe: '',
    source: '',
    destination: '',
    departureDate: '',
    arrivalDate: '',
    activities: [],
    duration: 3,
    beenBefore: false
  });

  const [output, setOutput] = useState<TripFormOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.vibe.trim() || !formData.destination.trim() || !formData.source.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    if (!formData.departureDate || !formData.arrivalDate) {
      setError('Please select both departure and arrival dates');
      return;
    }

    setLoading(true);

    // Simulate API call
    setTimeout(() => {
      const generatedOutput: TripFormOutput = {
        source: formData.source,
        destination: formData.destination,
        departureDate: formData.departureDate,
        arrivalDate: formData.arrivalDate,
        days: formData.duration,
        trip_theme: formData.vibe,
        user_mood: extractMood(formData.vibe),
        vibe_keywords: extractKeywords(formData.vibe),
        activities: formData.activities,
        avoid: ['crowds', 'strict schedules'],
        been_here_before: formData.beenBefore
      };

      setOutput(generatedOutput);
      setLoading(false);
    }, 1500);
  };

  const handleReset = () => {
    setFormData({
      vibe: '',
      source: '',
      destination: '',
      departureDate: '',
      arrivalDate: '',
      activities: [],
      duration: 3,
      beenBefore: false
    });
    setOutput(null);
    setError('');
  };

  const extractMood = (vibe: string): string => {
    const lowerVibe = vibe.toLowerCase();
    if (lowerVibe.includes('heal')) return 'calm and reflective';
    if (lowerVibe.includes('adventure')) return 'excited and energetic';
    if (lowerVibe.includes('escape')) return 'seeking solitude';
    return 'exploratory';
  };

  const extractKeywords = (vibe: string): string[] => {
    return vibe
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3)
      .slice(0, 3);
  };

  return (
    <div className="trip-form">
      <form onSubmit={handleSubmit} className="trip-form__container">
        <h2 className="trip-form__title">Plan Your Journey</h2>
        
        <div className="trip-form__field">
          <label htmlFor="vibe">What's the vibe of your trip?</label>
          <textarea
            id="vibe"
            value={formData.vibe}
            onChange={(e) => setFormData(prev => ({ ...prev, vibe: e.target.value }))}
            placeholder="e.g., healing and quiet time in nature"
            className="trip-form__textarea"
          />
        </div>

        <div className="trip-form__source">
          <label htmlFor="source">Where are you traveling from?</label>
          <input
            type="text"
            id="source"
            value={formData.source}
            onChange={(e) => setFormData(prev => ({ ...prev, source: e.target.value }))}
            placeholder="Enter your starting point"
            className="trip-form__input"
          />
        </div>

        <div className="trip-form__field">
          <label htmlFor="destination">Where would you like to go?</label>
          <input
            type="text"
            id="destination"
            value={formData.destination}
            onChange={(e) => setFormData(prev => ({ ...prev, destination: e.target.value }))}
            placeholder="Enter destination"
            className="trip-form__input"
          />
        </div>

        <div className="trip-form__dates">
          <div className="trip-form__date-input">
            <label htmlFor="departure">Departure Date</label>
            <input
              type="date"
              id="departure"
              value={formData.departureDate}
              onChange={(e) => setFormData(prev => ({ ...prev, departureDate: e.target.value }))}
              min={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="trip-form__date-input">
            <label htmlFor="arrival">Return Date</label>
            <input
              type="date"
              id="arrival"
              value={formData.arrivalDate}
              onChange={(e) => setFormData(prev => ({ ...prev, arrivalDate: e.target.value }))}
              min={formData.departureDate || new Date().toISOString().split('T')[0]}
            />
          </div>
        </div>

        <div className="trip-form__field">
          <label>Choose your activities:</label>
          <div className="trip-form__activities">
            {ACTIVITIES.map(activity => (
              <label key={activity} className="trip-form__checkbox-label">
                <input
                  type="checkbox"
                  checked={formData.activities.includes(activity)}
                  onChange={(e) => {
                    const newActivities = e.target.checked
                      ? [...formData.activities, activity]
                      : formData.activities.filter(a => a !== activity);
                    setFormData(prev => ({ ...prev, activities: newActivities }));
                  }}
                />
                {activity}
              </label>
            ))}
          </div>
        </div>

        <div className="trip-form__field">
          <label htmlFor="duration">Trip duration (days):</label>
          <div className="trip-form__slider-container">
            <input
              type="range"
              id="duration"
              min="1"
              max="10"
              value={formData.duration}
              onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) }))}
              className="trip-form__slider"
            />
          </div>
          <span className="trip-form__duration-display">{formData.duration} days</span>
        </div>

        <div className="trip-form__field">
          <label className="trip-form__checkbox-label">
            <input
              type="checkbox"
              checked={formData.beenBefore}
              onChange={(e) => setFormData(prev => ({ ...prev, beenBefore: e.target.checked }))}
            />
            Have you been here before?
          </label>
        </div>

        {error && <div className="trip-form__error">{error}</div>}

        <div className="trip-form__actions">
          <ActionButton
            label="Generate Itinerary"
            icon="✧"
            onClick={() => handleSubmit}
            variant="primary"
            disabled={loading}
          />
          <ActionButton
            label="Reset"
            icon="↺"
            onClick={handleReset}
            variant="secondary"
            disabled={loading}
          />
        </div>
      </form>

      {loading && (
        <div className="trip-form__loading">
          <div className="trip-form__loading-spinner"></div>
          <p>Crafting your perfect journey...</p>
        </div>
      )}

      {output && (
        <div className="trip-form__output">
          <h3>Your Journey Blueprint</h3>
          <pre>{JSON.stringify(output, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};