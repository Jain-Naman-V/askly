import api from './api';

export const dataService = {
  // Create record
  async createRecord(recordData) {
    return await api.post('/api/v1/data/', recordData);
  },

  // Get record by ID
  async getRecord(recordId) {
    return await api.get(`/api/v1/data/${recordId}`);
  },

  // Update record
  async updateRecord(recordId, updates) {
    return await api.put(`/api/v1/data/${recordId}`, updates);
  },

  // Delete record
  async deleteRecord(recordId, softDelete = true) {
    const params = new URLSearchParams({ soft_delete: softDelete.toString() });
    return await api.delete(`/api/v1/data/${recordId}?${params}`);
  },

  // Bulk operations
  async bulkOperation(operationData) {
    return await api.post('/api/v1/data/bulk', operationData);
  },

  // Import data
  async importData(file, format, mapping = null) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_format', format);
    if (mapping) {
      formData.append('mapping', JSON.stringify(mapping));
    }

    return await api.post('/api/v1/data/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Export data
  async exportData(exportRequest) {
    return await api.post('/api/v1/data/export', exportRequest, {
      responseType: 'blob',
    });
  },

  // Get analytics
  async getAnalytics() {
    return await api.get('/api/v1/data/analytics/summary');
  },

  // Validate record
  async validateRecord(recordData) {
    return await api.post('/api/v1/data/validate', recordData);
  },

  // Get data schema
  async getDataSchema() {
    return await api.get('/api/v1/data/schema');
  },

  // Get categories
  async getCategories() {
    return await api.get('/api/v1/data/categories');
  },

  // Get tags
  async getTags(limit = 100) {
    const params = new URLSearchParams({ limit: limit.toString() });
    return await api.get(`/api/v1/data/tags?${params}`);
  },

  // Health check
  async healthCheck() {
    return await api.get('/health');
  },

  // Get category statistics
  async getCategoryStats() {
    return await api.get('/api/v1/data/analytics/categories');
  },

  // Get time distribution
  async getTimeDistribution() {
    return await api.get('/api/v1/data/analytics/time-distribution');
  }
};