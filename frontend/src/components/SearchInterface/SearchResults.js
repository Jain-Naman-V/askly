import React, { useState, useMemo } from 'react';
import { useSelector } from 'react-redux';

const SearchResults = ({ 
  results = [], 
  totalCount = 0, 
  isLoading = false, 
  query = '',
  onResultClick = null,
  onExport = null,
  viewMode = 'list' // 'list', 'grid', 'table'
}) => {
  const [selectedResults, setSelectedResults] = useState(new Set());
  const [sortBy, setSortBy] = useState('relevance');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showPreview, setShowPreview] = useState(null);

  // Memoized sorted results
  const sortedResults = useMemo(() => {
    if (!results || results.length === 0) return [];
    
    const sorted = [...results].sort((a, b) => {
      let aVal, bVal;
      
      switch (sortBy) {
        case 'relevance':
          aVal = a.score || 0;
          bVal = b.score || 0;
          break;
        case 'date':
          aVal = new Date(a.created_at || 0);
          bVal = new Date(b.created_at || 0);
          break;
        case 'title':
          aVal = (a.title || '').toLowerCase();
          bVal = (b.title || '').toLowerCase();
          break;
        case 'category':
          aVal = (a.category || '').toLowerCase();
          bVal = (b.category || '').toLowerCase();
          break;
        default:
          return 0;
      }
      
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });
    
    return sorted;
  }, [results, sortBy, sortOrder]);

  // Handle result selection
  const handleSelectResult = (resultId) => {
    const newSelected = new Set(selectedResults);
    if (newSelected.has(resultId)) {
      newSelected.delete(resultId);
    } else {
      newSelected.add(resultId);
    }
    setSelectedResults(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedResults.size === results.length) {
      setSelectedResults(new Set());
    } else {
      setSelectedResults(new Set(results.map(r => r.id)));
    }
  };

  // Export functions
  const exportToCSV = () => {
    const headers = ['ID', 'Title', 'Description', 'Category', 'Tags', 'Score', 'Created At'];
    const csvContent = [
      headers.join(','),
      ...sortedResults.map(result => [
        result.id || '',
        `"${(result.title || '').replace(/"/g, '""')}"`,
        `"${(result.description || '').replace(/"/g, '""')}"`,
        result.category || '',
        (result.tags || []).join(';'),
        result.score || '',
        result.created_at || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `search_results_${query.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}.csv`;
    link.click();
  };

  const exportToJSON = () => {
    const exportData = {
      query,
      totalCount,
      exportTime: new Date().toISOString(),
      results: sortedResults
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `search_results_${query.replace(/[^a-zA-Z0-9]/g, '_')}_${Date.now()}.json`;
    link.click();
  };

  // Render functions for different view modes
  const renderListView = () => (
    <div className="space-y-4">
      {sortedResults.map((result, index) => (
        <div
          key={result.id || index}
          className={`border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow ${
            selectedResults.has(result.id) ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <input
                type="checkbox"
                checked={selectedResults.has(result.id)}
                onChange={() => handleSelectResult(result.id)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <h4 
                    className="text-lg font-medium text-gray-900 dark:text-white cursor-pointer hover:text-blue-600"
                    onClick={() => onResultClick && onResultClick(result)}
                  >
                    {result.title || 'Untitled'}
                  </h4>
                  {result.score && (
                    <span className="text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                      {result.score.toFixed(3)}
                    </span>
                  )}
                </div>
                
                {result.description && (
                  <p className="text-gray-600 dark:text-gray-300 mb-2">
                    {result.description}
                  </p>
                )}
                
                <div className="flex flex-wrap gap-2 mb-2">
                  {result.category && (
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded">
                      {result.category}
                    </span>
                  )}
                  {result.tags && result.tags.slice(0, 5).map((tag, tagIndex) => (
                    <span
                      key={tagIndex}
                      className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                  {result.tags && result.tags.length > 5 && (
                    <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded">
                      +{result.tags.length - 5} more
                    </span>
                  )}
                </div>
                
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                  {result.created_at && (
                    <span>Created: {new Date(result.created_at).toLocaleString()}</span>
                  )}
                  <button
                    onClick={() => setShowPreview(showPreview === result.id ? null : result.id)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {showPreview === result.id ? 'Hide Preview' : 'Show Preview'}
                  </button>
                </div>
                
                {showPreview === result.id && result.content && (
                  <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-700 rounded border-l-4 border-blue-500">
                    <div className="text-sm text-gray-800 dark:text-gray-200 max-h-40 overflow-y-auto">
                      <pre className="whitespace-pre-wrap">
                        {typeof result.content === 'object' 
                          ? JSON.stringify(result.content, null, 2)
                          : result.content
                        }
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderGridView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {sortedResults.map((result, index) => (
        <div
          key={result.id || index}
          className={`border border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:shadow-md transition-shadow ${
            selectedResults.has(result.id) ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900' : ''
          }`}
        >
          <div className="flex items-start justify-between mb-2">
            <input
              type="checkbox"
              checked={selectedResults.has(result.id)}
              onChange={() => handleSelectResult(result.id)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            {result.score && (
              <span className="text-sm text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                {result.score.toFixed(3)}
              </span>
            )}
          </div>
          
          <h4 
            className="text-lg font-medium text-gray-900 dark:text-white mb-2 cursor-pointer hover:text-blue-600"
            onClick={() => onResultClick && onResultClick(result)}
          >
            {result.title || 'Untitled'}
          </h4>
          
          {result.description && (
            <p className="text-gray-600 dark:text-gray-300 text-sm mb-2 line-clamp-3">
              {result.description}
            </p>
          )}
          
          <div className="flex flex-wrap gap-1 mb-2">
            {result.category && (
              <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded">
                {result.category}
              </span>
            )}
            {result.tags && result.tags.slice(0, 2).map((tag, tagIndex) => (
              <span
                key={tagIndex}
                className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
              >
                {tag}
              </span>
            ))}
          </div>
          
          {result.created_at && (
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {new Date(result.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
      ))}
    </div>
  );

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 dark:text-gray-400">
          {query ? `No results found for "${query}"` : 'No results to display'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Results Header with Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600 dark:text-gray-300">
            {totalCount.toLocaleString()} results
            {selectedResults.size > 0 && ` • ${selectedResults.size} selected`}
          </span>
          
          {results.length > 0 && (
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={selectedResults.size === results.length}
                onChange={handleSelectAll}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <span className="text-gray-600 dark:text-gray-300">Select all</span>
            </label>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Sort Controls */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-700 dark:text-white"
          >
            <option value="relevance">Sort by Relevance</option>
            <option value="date">Sort by Date</option>
            <option value="title">Sort by Title</option>
            <option value="category">Sort by Category</option>
          </select>
          
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
          
          {/* Export Options */}
          {selectedResults.size > 0 && (
            <div className="flex space-x-1">
              <button
                onClick={exportToCSV}
                className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
              >
                CSV
              </button>
              <button
                onClick={exportToJSON}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                JSON
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Results Display */}
      {viewMode === 'grid' ? renderGridView() : renderListView()}
    </div>
  );
};

export default SearchResults;