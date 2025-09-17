import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { performSearch, updateFilter, clearFilters } from '../../store/slices/searchSlice';

const AdvancedSearch = () => {
  const dispatch = useDispatch();
  const { filters, facets, isLoading } = useSelector(state => state.search);
  
  const [localFilters, setLocalFilters] = useState({
    categories: [],
    tags: [],
    dateRange: { start: '', end: '' },
    contentFields: {},
    minScore: 0.0
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleFilterChange = (filterType, value) => {
    const newFilters = { ...localFilters };
    
    if (filterType === 'categories' || filterType === 'tags') {
      if (newFilters[filterType].includes(value)) {
        newFilters[filterType] = newFilters[filterType].filter(item => item !== value);
      } else {
        newFilters[filterType] = [...newFilters[filterType], value];
      }
    } else if (filterType === 'dateRange') {
      newFilters.dateRange = { ...newFilters.dateRange, ...value };
    } else {
      newFilters[filterType] = value;
    }
    
    setLocalFilters(newFilters);
    dispatch(updateFilter({ key: filterType, value: newFilters[filterType] }));
  };

  const handleClearFilters = () => {
    setLocalFilters({
      categories: [],
      tags: [],
      dateRange: { start: '', end: '' },
      contentFields: {},
      minScore: 0.0
    });
    dispatch(clearFilters());
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600 p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Search Filters
        </h3>
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          {showAdvanced ? 'Hide Advanced' : 'Show Advanced'}
        </button>
      </div>

      {/* Quick Filters */}
      <div className="space-y-4">
        {/* Categories */}
        {facets.categories && Object.keys(facets.categories).length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Categories
            </label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(facets.categories).map(([category, count]) => (
                <button
                  key={category}
                  onClick={() => handleFilterChange('categories', category)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    localFilters.categories.includes(category)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {category} ({count})
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {facets.tags && Object.keys(facets.tags).length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tags
            </label>
            <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
              {Object.entries(facets.tags)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 20)
                .map(([tag, count]) => (
                <button
                  key={tag}
                  onClick={() => handleFilterChange('tags', tag)}
                  className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                    localFilters.tags.includes(tag)
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {tag} ({count})
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600 space-y-4">
          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Date Range
            </label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="date"
                value={localFilters.dateRange.start}
                onChange={(e) => handleFilterChange('dateRange', { start: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
              <input
                type="date"
                value={localFilters.dateRange.end}
                onChange={(e) => handleFilterChange('dateRange', { end: e.target.value })}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Minimum Score */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Minimum Relevance Score: {localFilters.minScore}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={localFilters.minScore}
              onChange={(e) => handleFilterChange('minScore', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0.0</span>
              <span>1.0</span>
            </div>
          </div>
        </div>
      )}

      {/* Clear Filters */}
      {(localFilters.categories.length > 0 || localFilters.tags.length > 0 || 
        localFilters.dateRange.start || localFilters.dateRange.end || localFilters.minScore > 0) && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
          <button
            onClick={handleClearFilters}
            className="text-red-600 hover:text-red-800 text-sm font-medium"
          >
            Clear All Filters
          </button>
        </div>
      )}
    </div>
  );
};

export default AdvancedSearch;