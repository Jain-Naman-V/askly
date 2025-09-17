import api from './api';

export const searchService = {
  // Basic search
  async search(params) {
    const {
      query,
      searchType = 'hybrid',
      filters = {},
      sortBy,
      sortOrder = 'desc',
      limit = 50,
      offset = 0,
      includeScore = true
    } = params;

    const payload = {
      query,
      search_type: searchType,
      filters,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit,
      offset,
      include_score: includeScore
    };

    return await api.post('/api/v1/search/', payload);
  },

  // Advanced search
  async advancedSearch(params) {
    const {
      query,
      searchType = 'hybrid',
      filters = [],
      dateRange,
      categories,
      tags,
      sortBy,
      sortOrder = 'desc',
      limit = 50,
      offset = 0,
      minScore = 0.0
    } = params;

    const payload = {
      query,
      search_type: searchType,
      filters,
      date_range: dateRange,
      categories,
      tags,
      sort_by: sortBy,
      sort_order: sortOrder,
      limit,
      offset,
      min_score: minScore
    };

    return await api.post('/api/v1/search/advanced', payload);
  },

  // Smart search with AI processing
  async smartSearch(params) {
    const {
      query,
      searchType = 'hybrid',
      filters = {},
      limit = 50,
      offset = 0
    } = params;

    const payload = {
      query,
      search_type: searchType,
      filters,
      limit,
      offset
    };

    return await api.post('/api/v1/smart-search', payload);
  },

  // Get search suggestions
  async getSuggestions(query, limit = 5) {
    const params = new URLSearchParams({
      query,
      limit: limit.toString()
    });

    return await api.get(`/api/v1/search/suggestions?${params}`);
  },

  // Get search facets
  async getFacets(query = '') {
    const params = new URLSearchParams({ query });
    return await api.get(`/api/v1/search/facets?${params}`);
  },

  // Save search
  async saveSearch(searchData) {
    return await api.post('/api/v1/search/save', searchData);
  },

  // Get saved searches
  async getSavedSearches() {
    return await api.get('/api/v1/search/saved');
  },

  // Delete saved search
  async deleteSavedSearch(searchId) {
    return await api.delete(`/api/v1/search/saved/${searchId}`);
  },

  // Get search analytics
  async getSearchAnalytics() {
    return await api.get('/api/v1/search/analytics');
  }
};