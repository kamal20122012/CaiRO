import React, { useState, useEffect, useRef } from 'react';
import './CityAutocomplete.css';

interface CityAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (city: string) => void;
  placeholder: string;
  label: string;
  id: string;
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
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Close suggestions on click outside
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchCitySuggestions = async (query: string) => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`https://api.teleport.org/api/cities/?search=${encodeURIComponent(query)}&limit=5`);
      const data = await response.json();
      const cityNames = data._embedded['city:search-results']
        .map((result: any) => result.matching_full_name)
        .slice(0, 5);
      setSuggestions(cityNames);
    } catch (error) {
      console.error('Error fetching city suggestions:', error);
      setSuggestions([]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onChange(value);
    fetchCitySuggestions(value);
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (suggestion: string) => {
    onSelect(suggestion);
    setShowSuggestions(false);
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