import React, { useState, useRef, useEffect } from 'react';
import { searchDrugs } from '../services/api';

export default function DrugAutocomplete({ value, onChange, onSelect }) {
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightIndex, setHighlightIndex] = useState(-1);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    if (!value || value.length < 1) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    // Debounce API call
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setLoading(true);
      searchDrugs(value)
        .then(results => {
          setSuggestions(results);
          setIsOpen(results.length > 0);
          setHighlightIndex(-1);
        })
        .catch(console.error)
        .finally(() => setLoading(false));
    }, 150);

    return () => clearTimeout(debounceRef.current);
  }, [value]);

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target) &&
          inputRef.current && !inputRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleKeyDown = (e) => {
    if (!isOpen) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIndex(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (highlightIndex >= 0 && highlightIndex < suggestions.length) {
        handleSelect(suggestions[highlightIndex]);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleSelect = (drug) => {
    onSelect(drug);
    setIsOpen(false);
    setSuggestions([]);
  };

  const highlightMatch = (text, query) => {
    if (!query) return text;
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return text;
    return (
      <>
        {text.slice(0, idx)}
        <strong style={{ color: '#1B5E96' }}>{text.slice(idx, idx + query.length)}</strong>
        {text.slice(idx + query.length)}
      </>
    );
  };

  return (
    <div className="autocomplete-container">
      <input
        ref={inputRef}
        id="drug-search-input"
        type="text"
        className="form-input"
        placeholder="Type to search medications..."
        value={value}
        onChange={e => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onFocus={() => suggestions.length > 0 && setIsOpen(true)}
        autoComplete="off"
      />
      {loading && (
        <div style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)' }}>
          <div className="loading-spinner" style={{ width: '14px', height: '14px' }} />
        </div>
      )}

      {isOpen && suggestions.length > 0 && (
        <div ref={dropdownRef} className="autocomplete-dropdown">
          {suggestions.map((drug, idx) => (
            <div
              key={drug.id}
              className={`autocomplete-item ${idx === highlightIndex ? 'highlighted' : ''}`}
              onClick={() => handleSelect(drug)}
              onMouseEnter={() => setHighlightIndex(idx)}
            >
              <span className="autocomplete-drug-name">
                {highlightMatch(drug.genericName, value)}
              </span>
              <span className="autocomplete-drug-brands">
                Brands: {drug.brandNames.join(', ')}
              </span>
              <span className="autocomplete-drug-meta">
                {drug.drugClass} • {drug.therapeuticCategory}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
