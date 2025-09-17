import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { performSearch, getSearchFacets } from '../../store/slices/searchSlice';
import SearchSuggestions from './SearchSuggestions';
import SearchResults from './SearchResults';
import AdvancedSearch from './AdvancedSearch';
import AIChat from '../AIChat/AIChat';
import InsightsDashboard from '../DataVisualization/InsightsDashboard';

const SearchInterface = () => {
  const dispatch = useDispatch();
  const { results, isLoading, error, query, totalCount, filters } = useSelector(state => state.search);
  
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('hybrid');
  const [viewMode, setViewMode] = useState('list'); // 'list', 'grid', 'table'
  const [activeTab, setActiveTab] = useState('search'); // 'search', 'ai-chat', 'insights'
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [sortBy, setSortBy] = useState('relevance');
  const [sortOrder, setSortOrder] = useState('desc');
  const [searchHistory, setSearchHistory] = useState([]);
  const [isRealTimeSearch, setIsRealTimeSearch] = useState(false);
  const [searchFilters, setSearchFilters] = useState({});
  const [savedSearches, setSavedSearches] = useState([]);
  const [exportFormat, setExportFormat] = useState('json');

  // Load facets and search history on component mount
  useEffect(() => {
    dispatch(getSearchFacets());
    loadSearchHistory();
    loadSavedSearches();
  }, [dispatch]);

  // Real-time search effect
  useEffect(() => {
    if (isRealTimeSearch && searchQuery.length > 2) {
      const debounceTimer = setTimeout(() => {
        handleSearch();
      }, 300);
      return () => clearTimeout(debounceTimer);
    }
  }, [searchQuery, isRealTimeSearch]);

  const loadSearchHistory = () => {
    const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    setSearchHistory(history.slice(0, 10)); // Keep last 10 searches
  };

  const loadSavedSearches = () => {
    const saved = JSON.parse(localStorage.getItem('savedSearches') || '[]');
    setSavedSearches(saved);
  };

  const saveSearch = (query, filters) => {
    const searchToSave = {
      id: Date.now(),
      query,
      filters,
      timestamp: new Date().toISOString(),
      resultCount: results.length
    };
    const updatedSaved = [searchToSave, ...savedSearches.slice(0, 9)];
    setSavedSearches(updatedSaved);
    localStorage.setItem('savedSearches', JSON.stringify(updatedSaved));
  };

  const addToSearchHistory = (query) => {
    if (query.trim() && !searchHistory.includes(query)) {
      const updatedHistory = [query, ...searchHistory.slice(0, 9)];
      setSearchHistory(updatedHistory);
      localStorage.setItem('searchHistory', JSON.stringify(updatedHistory));
    }
  };

  const handleSearch = async (queryText = null, options = {}) => {
    const finalQuery = queryText || searchQuery;
    if (!finalQuery.trim()) return;

    // Add to search history
    addToSearchHistory(finalQuery);

    const searchParams = {
      query: finalQuery,
      search_type: searchType,
      filters: { ...filters, ...searchFilters, ...options.filters },
      sort_by: sortBy,
      sort_order: sortOrder,
      limit: 50,
      ...options
    };

    dispatch(performSearch(searchParams));
  };

  const handleAdvancedSearch = (advancedFilters) => {
    setSearchFilters(advancedFilters);
    handleSearch(null, { filters: advancedFilters });
  };

  const handleSaveCurrentSearch = () => {
    if (searchQuery.trim()) {
      saveSearch(searchQuery, { ...filters, ...searchFilters });
    }
  };

  const handleLoadSavedSearch = (savedSearch) => {
    setSearchQuery(savedSearch.query);
    setSearchFilters(savedSearch.filters);
    handleSearch(savedSearch.query, { filters: savedSearch.filters });
  };

  const handleExportResults = (format) => {
    const dataToExport = results.map(result => ({
      title: result.title,
      description: result.description,
      category: result.category,
      tags: result.tags,
      score: result.score,
      created_at: result.created_at
    }));

    if (format === 'json') {
      const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search-results-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } else if (format === 'csv') {
      const csvContent = convertToCSV(dataToExport);
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `search-results-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const convertToCSV = (data) => {
    if (!data.length) return '';
    const headers = Object.keys(data[0]);
    const csvRows = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          if (Array.isArray(value)) return `"${value.join('; ')}"`;
          if (typeof value === 'string') return `"${value.replace(/"/g, '""')}"`;
          return value;
        }).join(',')
      )
    ];
    return csvRows.join('\n');
  };

  const handleSuggestionSelect = (suggestionText, suggestion) => {
    setSearchQuery(suggestionText);
    handleSearch(suggestionText, {
      search_type: suggestion?.search_type || searchType
    });
  };

  const handleResultClick = (result) => {
    // Handle result click - could open modal, navigate, etc.
    console.log('Result clicked:', result);
  };

  const handleExport = (format) => {
    // Export functionality is handled in SearchResults component
    console.log('Export format:', format);
  };

  const handleClear = () => {
    setSearchQuery('');
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          AI Data Agent
        </h1>
        <p className="text-gray-600 dark:text-gray-300">
          Search, analyze, and gain insights from your structured data using AI
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <nav className="flex space-x-8" aria-label="Tabs">
          {[
            { id: 'search', name: 'Smart Search', icon: '🔍' },
            { id: 'ai-chat', name: 'AI Chat', icon: '🤖' },
            { id: 'insights', name: 'Insights', icon: '📊' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Search Controls - Takes 3 columns */}
          <div className="lg:col-span-3 space-y-6">
            {/* Search Interface */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Search Your Data
                </h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    {showAdvanced ? 'Hide Filters' : 'Show Filters'}
                  </button>
                  <div className="flex rounded-lg border border-gray-200 dark:border-gray-600">
                    <button
                      onClick={() => setViewMode('list')}
                      className={`px-3 py-1 text-sm rounded-l-lg ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                    >
                      List
                    </button>
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`px-3 py-1 text-sm rounded-r-lg ${viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                    >
                      Grid
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Search Form */}
              <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }} className="mb-6">
                <div className="flex flex-col gap-4">
                  {/* Smart Search Input */}
                  <SearchSuggestions
                    currentQuery={searchQuery}
                    onQueryChange={setSearchQuery}
                    onSuggestionSelect={handleSuggestionSelect}
                    placeholder="Ask a question or search your data..."
                  />
                  
                  {/* Search Options */}
                  <div className="flex flex-wrap items-center gap-4">
                    <select
                      value={searchType}
                      onChange={(e) => setSearchType(e.target.value)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                      disabled={isLoading}
                    >
                      <option value="hybrid">🔀 Hybrid Search</option>
                      <option value="semantic">🧠 Semantic Search</option>
                      <option value="keyword">🔤 Keyword Search</option>
                      <option value="fuzzy">🔍 Fuzzy Search</option>
                    </select>
                    
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    >
                      <option value="relevance">Sort by Relevance</option>
                      <option value="date">Sort by Date</option>
                      <option value="title">Sort by Title</option>
                      <option value="category">Sort by Category</option>
                    </select>
                    
                    <button
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </button>
                    
                    <button
                      type="submit"
                      disabled={isLoading || !searchQuery.trim()}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoading ? 'Searching...' : 'Search'}
                    </button>
                    
                    {searchQuery && (
                      <button
                        type="button"
                        onClick={handleClear}
                        className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                      >
                        Clear
                      </button>
                    )}
                  </div>
                </div>
              </form>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg">
                  <p className="text-red-800 dark:text-red-200">
                    Error: {error}
                  </p>
                </div>
              )}

              {/* Search Results */}
              <SearchResults
                results={results}
                totalCount={totalCount}
                isLoading={isLoading}
                query={query}
                viewMode={viewMode}
                onResultClick={handleResultClick}
                onExport={handleExport}
              />
            </div>
          </div>

          {/* Sidebar - Advanced Search Filters */}
          <div className="lg:col-span-1">
            {showAdvanced && <AdvancedSearch />}
          </div>
        </div>
      )}

      {/* AI Chat Tab */}
      {activeTab === 'ai-chat' && (
        <div className="h-[600px]">
          <AIChat />
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div>
          <InsightsDashboard />
        </div>
      )}
    </div>
  );
};

// Add performance monitoring
SearchInterface.displayName = 'SearchInterface';

export default SearchInterface;