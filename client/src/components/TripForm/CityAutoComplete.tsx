import React, { useState, useEffect, useRef } from 'react';
import './CityAutoComplete.css';

declare global {
  interface Window {
    google: any;
  }
}

let googleMapsPromise: Promise<void> | null = null;

const loadGoogleMapsScript = (apiKey: string) => {
  if (!googleMapsPromise) {
    googleMapsPromise = new Promise((resolve, reject) => {
      if (window.google && window.google.maps) {
        return resolve();
      }

      const scriptId = 'google-maps-script';
      if (document.getElementById(scriptId)) {
        // If script is already in the DOM, just wait for the promise to resolve
        return;
      }

      const script = document.createElement('script');
      script.id = scriptId;
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&loading=async`;
      script.onload = () => resolve();
      script.onerror = () => {
        googleMapsPromise = null; // Allow retrying
        reject(new Error('Failed to load Google Maps API'));
      };

      document.head.appendChild(script);
    });
  }
  return googleMapsPromise;
};


interface CityAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (city: string) => void;
  onConfirm?: (city: string) => void;
  placeholder: string;
  label: string;
  id: string;
  showConfirmButton?: boolean;
  isConfirmed?: boolean;
}

// Define the type for a single suggestion
interface AutocompleteSuggestion {
  placePrediction: {
    text: {
      text: string;
    };
  };
}

export const CityAutocomplete: React.FC<CityAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  onConfirm,
  placeholder,
  label,
  id,
  showConfirmButton = false,
  isConfirmed = false
}) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const [sessionToken, setSessionToken] = useState<any | undefined>(undefined);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const apiKey = import.meta.env.VITE_GOOGLE_PLACES_API_KEY;
    if (!apiKey) {
      console.error('Google Places API key not found. Please set VITE_GOOGLE_PLACES_API_KEY environment variable.');
      return;
    }

    let isMounted = true;
    loadGoogleMapsScript(apiKey)
      .then(() => {
        if (isMounted) {
          setIsGoogleLoaded(true);
        }
      })
      .catch((error) => console.error(error));

    // Close suggestions on click outside
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      isMounted = false;
      document.removeEventListener('mousedown', handleClickOutside);
      // Clean up debounce timer
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  const fetchCitySuggestions = async (query: string) => {
    if (!query.trim() || !isGoogleLoaded) {
      setSuggestions([]);
      return;
    }

    const request = {
      input: query,
      sessionToken: sessionToken,
      includedPrimaryTypes: ['(cities)'],
    };

    try {
      const { suggestions } =
        await window.google.maps.places.AutocompleteSuggestion.fetchAutocompleteSuggestions(
          request
        );

      if (suggestions) {
        const cityNames = suggestions.map((suggestion: AutocompleteSuggestion) => {
          return suggestion.placePrediction.text.text;
        });
        setSuggestions(cityNames.slice(0, 5));
      } else {
        setSuggestions([]);
      }
    } catch (error) {
      console.error("Error fetching city suggestions:", error);
      setSuggestions([]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onChange(value);
    
    if (!sessionToken && window.google) {
      setSessionToken(new window.google.maps.places.AutocompleteSessionToken());
    }
    
    // Clear previous debounce timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    
    // Debounce the API call to avoid too many requests
    debounceTimer.current = setTimeout(async () => {
      await fetchCitySuggestions(value);
      setShowSuggestions(true);
    }, 300);
  };

  const handleSuggestionClick = (suggestion: string) => {
    onSelect(suggestion);
    setShowSuggestions(false);
    setSessionToken(undefined); // End session on selection
  };

  const handleConfirm = () => {
    if (value.trim() && onConfirm) {
      onConfirm(value);
    }
  };

  return (
    <div className="city-autocomplete" ref={wrapperRef}>
      <label htmlFor={id}>{label}</label>
      <div className="city-autocomplete__input-container">
        <input
          type="text"
          id={id}
          value={value}
          onChange={handleInputChange}
          placeholder={placeholder}
          className={`city-autocomplete__input ${isConfirmed ? 'city-autocomplete__input--confirmed' : ''}`}
          autoComplete="off"
          disabled={isConfirmed}
        />
        {showConfirmButton && !isConfirmed && value.trim() && (
          <button
            type="button"
            onClick={handleConfirm}
            className="city-autocomplete__confirm-btn"
          >
            ✓
          </button>
        )}
        {isConfirmed && (
          <span className="city-autocomplete__confirmed-icon">✓</span>
        )}
      </div>
      {showSuggestions && suggestions.length > 0 && !isConfirmed && (
        <ul className="city-autocomplete__suggestions">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="city-autocomplete__suggestion"
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};