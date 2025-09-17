import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getSearchSuggestions } from '../../store/slices/searchSlice';
import { aiService } from '../../services/aiService';

const SearchSuggestions = ({ 
  onSuggestionSelect, 
  onQueryChange, 
  currentQuery = '',
  placeholder = "Search your data..." 
}) => {
  const dispatch = useDispatch();
  const { suggestions, recentSearches } = useSelector(state => state.search);
  
  const [localQuery, setLocalQuery] = useState(currentQuery);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestionIndex, setActiveSuggestionIndex] = useState(-1);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [smartSuggestions, setSmartSuggestions] = useState([]);
  
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);
  const debounceRef = useRef(null);

  // Debounced suggestion fetch
  const fetchSuggestions = useCallback(
    async (query) => {
      if (!query.trim() || query.length < 2) {
        setSmartSuggestions([]);
        return;
      }

      setIsLoadingSuggestions(true);
      
      try {
        // Get search suggestions from backend
        await dispatch(getSearchSuggestions(query));
        
        // Get AI-powered query suggestions
        const aiSuggestions = await aiService.getQuerySuggestions(query);
        setSmartSuggestions(aiSuggestions.suggestions || []);
        
      } catch (error) {
        console.error('Error fetching suggestions:', error);
      } finally {
        setIsLoadingSuggestions(false);
      }
    },
    [dispatch]
  );

  // Debounce suggestion fetching
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      if (localQuery !== currentQuery) {
        onQueryChange && onQueryChange(localQuery);
      }
      
      if (showSuggestions && localQuery.trim().length >= 2) {
        fetchSuggestions(localQuery);
      }
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [localQuery, currentQuery, onQueryChange, fetchSuggestions, showSuggestions]);

  // Handle input change
  const handleInputChange = (e) => {
    const value = e.target.value;
    setLocalQuery(value);
    setShowSuggestions(true);
    setActiveSuggestionIndex(-1);
  };

  // Handle input focus
  const handleInputFocus = () => {
    setShowSuggestions(true);
    if (localQuery.trim().length >= 2) {
      fetchSuggestions(localQuery);
    }
  };

  // Handle input blur (delayed to allow suggestion click)
  const handleInputBlur = () => {
    setTimeout(() => {
      setShowSuggestions(false);
      setActiveSuggestionIndex(-1);
    }, 150);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e) => {
    if (!showSuggestions) return;

    const allSuggestions = [
      ...smartSuggestions.map(s => ({ type: 'ai', ...s })),
      ...suggestions.map(s => ({ type: 'search', text: s })),
      ...recentSearches.slice(0, 5).map(s => ({ type: 'recent', text: s.query, timestamp: s.timestamp }))
    ];

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveSuggestionIndex(prev => 
          prev < allSuggestions.length - 1 ? prev + 1 : 0
        );
        break;
        
      case 'ArrowUp':
        e.preventDefault();
        setActiveSuggestionIndex(prev => 
          prev > 0 ? prev - 1 : allSuggestions.length - 1
        );
        break;
        
      case 'Enter':
        e.preventDefault();
        if (activeSuggestionIndex >= 0 && allSuggestions[activeSuggestionIndex]) {
          handleSuggestionSelect(allSuggestions[activeSuggestionIndex]);
        } else if (localQuery.trim()) {
          handleSuggestionSelect({ type: 'custom', text: localQuery.trim() });
        }
        break;
        
      case 'Escape':
        setShowSuggestions(false);
        setActiveSuggestionIndex(-1);
        inputRef.current?.blur();
        break;
        
      default:
        break;
    }
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion) => {
    const queryText = suggestion.text || suggestion.query || '';
    setLocalQuery(queryText);
    setShowSuggestions(false);
    setActiveSuggestionIndex(-1);
    
    if (onSuggestionSelect) {
      onSuggestionSelect(queryText, suggestion);
    }
  };

  // Get suggestion icon
  const getSuggestionIcon = (type) => {
    switch (type) {
      case 'ai':
        return '🧠';
      case 'search':
        return '🔍';
      case 'recent':
        return '🕒';
      default:
        return '💡';
    }
  };

  // Get suggestion label
  const getSuggestionLabel = (type) => {
    switch (type) {
      case 'ai':
        return 'AI Suggestion';
      case 'search':
        return 'Search Suggestion';
      case 'recent':
        return 'Recent Search';
      default:
        return 'Suggestion';
    }
  };

  // Prepare all suggestions for rendering
  const allSuggestions = [
    ...smartSuggestions.map(s => ({ type: 'ai', ...s })),
    ...suggestions.map(s => ({ type: 'search', text: s })),
    ...recentSearches.slice(0, 5).map(s => ({ 
      type: 'recent', 
      text: s.query, 
      timestamp: s.timestamp,
      resultCount: s.resultCount 
    }))
  ];

  // Remove duplicates
  const uniqueSuggestions = allSuggestions.filter((suggestion, index, self) => 
    index === self.findIndex(s => s.text === suggestion.text)
  );

  return (
    <div className="relative">
      {/* Search Input */}
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={localQuery}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
        />
        
        {/* Search Icon */}
        <div className="absolute inset-y-0 right-0 flex items-center pr-3">
          {isLoadingSuggestions ? (
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          ) : (
            <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          )}
        </div>
      </div>

      {/* Suggestions Dropdown */}
      {showSuggestions && uniqueSuggestions.length > 0 && (
        <div
          ref={suggestionsRef}
          className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg max-h-80 overflow-y-auto"
        >
          {uniqueSuggestions.map((suggestion, index) => (
            <div
              key={`${suggestion.type}-${index}`}
              className={`px-4 py-3 cursor-pointer border-b border-gray-100 dark:border-gray-700 last:border-b-0 ${
                index === activeSuggestionIndex
                  ? 'bg-blue-50 dark:bg-blue-900'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
              onClick={() => handleSuggestionSelect(suggestion)}
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg">{getSuggestionIcon(suggestion.type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {suggestion.text}
                  </div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {getSuggestionLabel(suggestion.type)}
                    </span>
                    {suggestion.confidence && (
                      <span className="text-xs text-blue-600 dark:text-blue-400">
                        {Math.round(suggestion.confidence * 100)}% match
                      </span>
                    )}
                    {suggestion.resultCount !== undefined && (
                      <span className="text-xs text-green-600 dark:text-green-400">
                        {suggestion.resultCount} results
                      </span>
                    )}
                    {suggestion.timestamp && (
                      <span className="text-xs text-gray-400">
                        {new Date(suggestion.timestamp).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                  {suggestion.description && (
                    <div className="text-xs text-gray-600 dark:text-gray-300 mt-1">
                      {suggestion.description}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {/* No suggestions message */}
          {uniqueSuggestions.length === 0 && localQuery.trim().length >= 2 && !isLoadingSuggestions && (
            <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
              No suggestions found for "{localQuery}"
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      {showSuggestions && localQuery.trim().length === 0 && recentSearches.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg">
          <div className="px-4 py-2 border-b border-gray-100 dark:border-gray-700">
            <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Recent Searches</span>
          </div>
          {recentSearches.slice(0, 5).map((search, index) => (
            <div
              key={index}
              className="px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 last:border-b-0"
              onClick={() => handleSuggestionSelect(search)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-lg">🕒</span>
                  <span className="text-sm text-gray-900 dark:text-white">{search.query}</span>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {search.resultCount} results
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchSuggestions;