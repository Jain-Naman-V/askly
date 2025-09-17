import React, { useState, useEffect } from 'react';

const DataManager = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [pagination, setPagination] = useState({
    current_page: 1,
    total_pages: 1,
    page_size: 10,
    total_count: 0,
    has_next: false,
    has_prev: false
  });
  const [newRecord, setNewRecord] = useState({
    title: '',
    description: '',
    content: '',
    tags: '',
    category: ''
  });

  // Fetch records on component mount
  useEffect(() => {
    fetchRecords(1); // Start with page 1
  }, []);

  const fetchRecords = async (page = pagination.current_page) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/v1/data/?page=${page}&limit=10`);
      if (!response.ok) throw new Error('Failed to fetch records');
      const data = await response.json();
      setRecords(data.data || []);
      setPagination(data.pagination || {
        current_page: 1,
        total_pages: 1,
        page_size: 10,
        total_count: 0,
        has_next: false,
        has_prev: false
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRecord = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const recordData = {
        title: newRecord.title,
        description: newRecord.description,
        content: newRecord.content ? JSON.parse(newRecord.content) : {},
        tags: newRecord.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        category: newRecord.category
      };

      const response = await fetch('/api/v1/data/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(recordData),
      });

      if (!response.ok) throw new Error('Failed to create record');
      
      // Reset form and refresh records
      setNewRecord({
        title: '',
        description: '',
        content: '',
        tags: '',
        category: ''
      });
      setShowAddForm(false);
      fetchRecords(1); // Go back to first page after adding
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm('Are you sure you want to delete this record?')) return;

    try {
      const response = await fetch(`/api/v1/data/${recordId}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Failed to delete record');
      fetchRecords(); // Refresh current page
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Data Manager
          </h2>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showAddForm ? 'Cancel' : 'Add Record'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg">
            <p className="text-red-800 dark:text-red-200">
              Error: {error}
            </p>
          </div>
        )}

        {/* Add Record Form */}
        {showAddForm && (
          <form onSubmit={handleAddRecord} className="mb-6 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Add New Record
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={newRecord.title}
                  onChange={(e) => setNewRecord({...newRecord, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Category
                </label>
                <input
                  type="text"
                  value={newRecord.category}
                  onChange={(e) => setNewRecord({...newRecord, category: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                value={newRecord.description}
                onChange={(e) => setNewRecord({...newRecord, description: e.target.value})}
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Content (JSON format)
              </label>
              <textarea
                value={newRecord.content}
                onChange={(e) => setNewRecord({...newRecord, content: e.target.value})}
                rows="5"
                placeholder='{"name": "John Doe", "email": "john@example.com"}'
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={newRecord.tags}
                onChange={(e) => setNewRecord({...newRecord, tags: e.target.value})}
                placeholder="tag1, tag2, tag3"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Record'}
            </button>
          </form>
        )}

        {/* Records List */}
        {loading && records.length === 0 ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Records ({pagination.total_count} total, showing {records.length} of page {pagination.current_page})
              </h3>
              <button
                onClick={() => fetchRecords()}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Refresh
              </button>
            </div>

            {records.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-600 dark:text-gray-300">
                  No records found. Create your first record above.
                </p>
              </div>
            ) : (
              records.map((record) => (
                <div
                  key={record.id}
                  className="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-lg font-medium text-gray-900 dark:text-white">
                      {record.title}
                    </h4>
                    <button
                      onClick={() => handleDeleteRecord(record.id)}
                      className="text-red-600 hover:text-red-800 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                  
                  {record.description && (
                    <p className="text-gray-600 dark:text-gray-300 mb-2">
                      {record.description}
                    </p>
                  )}
                  
                  {record.content && (
                    <div className="bg-gray-50 dark:bg-gray-700 rounded p-3 mb-2">
                      <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                        {JSON.stringify(record.content, null, 2)}
                      </pre>
                    </div>
                  )}
                  
                  <div className="flex flex-wrap gap-2 mb-2">
                    {record.tags && record.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded"
                      >
                        {tag}
                      </span>
                    ))}
                    {record.category && (
                      <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded">
                        {record.category}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Created: {new Date(record.created_at).toLocaleString()}
                  </p>
                </div>
              ))
            )}
            
            {/* Pagination Controls */}
            {pagination.total_pages > 1 && (
              <div className="flex items-center justify-between border-t border-gray-200 dark:border-gray-600 pt-4">
                <div className="flex-1 flex justify-between sm:hidden">
                  {/* Mobile pagination */}
                  <button
                    onClick={() => fetchRecords(pagination.current_page - 1)}
                    disabled={!pagination.has_prev}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => fetchRecords(pagination.current_page + 1)}
                    disabled={!pagination.has_next}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
                
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      Showing page{' '}
                      <span className="font-medium">{pagination.current_page}</span>
                      {' '}of{' '}
                      <span className="font-medium">{pagination.total_pages}</span>
                      {' '}({pagination.total_count} total records)
                    </p>
                  </div>
                  
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                      {/* Previous button */}
                      <button
                        onClick={() => fetchRecords(pagination.current_page - 1)}
                        disabled={!pagination.has_prev}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <span className="sr-only">Previous</span>
                        <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                          <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                      
                      {/* Page numbers */}
                      {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
                        let pageNum;
                        if (pagination.total_pages <= 5) {
                          pageNum = i + 1;
                        } else if (pagination.current_page <= 3) {
                          pageNum = i + 1;
                        } else if (pagination.current_page >= pagination.total_pages - 2) {
                          pageNum = pagination.total_pages - 4 + i;
                        } else {
                          pageNum = pagination.current_page - 2 + i;
                        }
                        
                        const isCurrentPage = pageNum === pagination.current_page;
                        
                        return (
                          <button
                            key={pageNum}
                            onClick={() => fetchRecords(pageNum)}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                              isCurrentPage
                                ? 'z-10 bg-blue-50 dark:bg-blue-900 border-blue-500 text-blue-600 dark:text-blue-200'
                                : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600'
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                      
                      {/* Next button */}
                      <button
                        onClick={() => fetchRecords(pagination.current_page + 1)}
                        disabled={!pagination.has_next}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <span className="sr-only">Next</span>
                        <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DataManager;