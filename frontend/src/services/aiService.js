import api from './api';

export const aiService = {
  // Chat with AI
  async chat(message, contextRecords = null) {
    const payload = {
      message,
      context_records: contextRecords
    };

    return await api.post('/api/v1/ai/chat', payload);
  },

  // Process natural language query
  async processQuery(query) {
    const payload = { query };
    return await api.post('/api/v1/ai/process-query', payload);
  },

  // Generate insights
  async generateInsights(params) {
    const {
      recordIds = null,
      searchQuery = null,
      limit = 100
    } = params;

    const payload = {
      record_ids: recordIds,
      search_query: searchQuery,
      limit
    };

    return await api.post('/api/v1/ai/generate-insights', payload);
  },

  // Analyze data
  async analyzeData(analysisType, filters = null, limit = 1000) {
    const payload = {
      analysis_type: analysisType,
      filters,
      limit
    };

    return await api.post('/api/v1/ai/analyze', payload);
  },

  // Generate embeddings
  async generateEmbeddings(texts) {
    const payload = { texts };
    return await api.post('/api/v1/ai/generate-embeddings', payload);
  },

  // Get query suggestions
  async getQuerySuggestions(context = null) {
    const params = context ? new URLSearchParams({ context }) : '';
    return await api.get(`/api/v1/ai/suggestions/queries?${params}`);
  },

  // Health check
  async healthCheck() {
    return await api.get('/api/v1/ai/health');
  },

  // Trigger background analysis
  async triggerAnalysis(analysisType = 'summary') {
    const params = new URLSearchParams({ analysis_type: analysisType });
    return await api.post(`/api/v1/data/analyze?${params}`);
  }
};