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

// Define Google Places types
declare global {
  interface Window {
    google: any;
  }
}

interface CityAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (city: string) => void;
  placeholder: string;
  label: string;
  id: string;
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
  placeholder,
  label,
  id
}) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGoogleLoaded, setIsGoogleLoaded] = useState(false);
  const [sessionToken, setSessionToken] = useState<any | undefined>(undefined);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const apiKey = "AIzaSyD51XwFtTeI724p8W_HWojrv4nxLb9DyiA";
    if (!apiKey) {
      console.error('Google Places API key not found.');
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

  return (
    <div className="city-autocomplete" ref={wrapperRef}>
      <label htmlFor={id}>{label}</label>
      <input
        type="text"
        id={id}
        value={value}
        onChange={handleInputChange}
        placeholder={placeholder}
        className="city-autocomplete__input"
        autoComplete="off"
      />
      {showSuggestions && suggestions.length > 0 && (
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