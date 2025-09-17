import React, { useState, useEffect, useCallback } from 'react';
import { useSelector } from 'react-redux';
import { aiService } from '../../services/aiService';
import { dataService } from '../../services/dataService';

const InsightsDashboard = () => {
  const { results, query } = useSelector(state => state.search);
  
  const [insights, setInsights] = useState({
    summary: null,
    trends: [],
    categories: {},
    topTerms: [],
    timeDistribution: {},
    sentimentAnalysis: null,
    recommendations: []
  });
  
  const [isLoading, setIsLoading] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Generate insights from current data
  const generateInsights = useCallback(async (forceRefresh = false) => {
    if (isLoading && !forceRefresh) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Generate insights from search results if available
      let insightsData;
      if (results && results.length > 0) {
        insightsData = await aiService.generateInsights({
          recordIds: results.slice(0, 20).map(r => r.id),
          searchQuery: query
        });
      } else {
        // Generate general dataset insights
        insightsData = await aiService.analyzeData('summary');
      }
      
      // Get category distribution
      const categoryStats = await dataService.getCategoryStats();
      
      // Get time distribution
      const timeStats = await dataService.getTimeDistribution();
      
      setInsights({
        summary: insightsData.summary || 'No summary available',
        trends: insightsData.trends || [],
        categories: categoryStats.categories || {},
        topTerms: insightsData.top_terms || [],
        timeDistribution: timeStats.distribution || {},
        sentimentAnalysis: insightsData.sentiment || null,
        recommendations: insightsData.recommendations || []
      });
      
      setLastUpdated(new Date());
      
    } catch (err) {
      console.error('Error generating insights:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [results, query, isLoading]);

  // Auto-refresh insights
  useEffect(() => {
    if (autoRefresh && refreshInterval > 0) {
      const interval = setInterval(() => {
        generateInsights();
      }, refreshInterval);
      
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval, generateInsights]);

  // Initial load
  useEffect(() => {
    generateInsights();
  }, []);

  // Render metrics card
  const renderMetricCard = (title, value, subtitle = null, trend = null) => (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</h3>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
        {trend && (
          <div className={`text-sm font-medium ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
          </div>
        )}
      </div>
    </div>
  );

  // Render category distribution
  const renderCategoryChart = () => {
    const categories = Object.entries(insights.categories)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    const maxCount = Math.max(...categories.map(([,count]) => count));
    
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Category Distribution
        </h3>
        <div className="space-y-3">
          {categories.map(([category, count]) => (
            <div key={category} className="flex items-center">
              <div className="w-24 text-sm text-gray-600 dark:text-gray-400 truncate">
                {category}
              </div>
              <div className="flex-1 mx-3">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-12 text-sm text-gray-900 dark:text-white text-right">
                {count}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render time distribution
  const renderTimeChart = () => {
    const timeData = Object.entries(insights.timeDistribution)
      .sort(([a], [b]) => new Date(a) - new Date(b))
      .slice(-30); // Last 30 time periods
    
    if (timeData.length === 0) return null;
    
    const maxCount = Math.max(...timeData.map(([,count]) => count));
    
    return (
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Data Timeline
        </h3>
        <div className="space-y-2">
          {timeData.map(([date, count]) => (
            <div key={date} className="flex items-center text-sm">
              <div className="w-20 text-gray-600 dark:text-gray-400">
                {new Date(date).toLocaleDateString()}
              </div>
              <div className="flex-1 mx-2">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
                  <div
                    className="bg-green-600 h-1 rounded-full"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-8 text-gray-900 dark:text-white text-right">
                {count}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Data Insights Dashboard
          </h2>
          {lastUpdated && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Last updated: {lastUpdated.toLocaleString()}
            </p>
          )}
        </div>
        
        <div className="flex items-center space-x-2 mt-4 sm:mt-0">
          <label className="flex items-center space-x-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-gray-600 dark:text-gray-300">Auto-refresh</span>
          </label>
          
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm dark:bg-gray-700 dark:text-white"
            disabled={!autoRefresh}
          >
            <option value={10000}>10s</option>
            <option value={30000}>30s</option>
            <option value={60000}>1m</option>
            <option value={300000}>5m</option>
          </select>
          
          <button
            onClick={() => generateInsights(true)}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">
            Error loading insights: {error}
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && !insights.summary && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {renderMetricCard(
          'Total Records',
          Object.values(insights.categories).reduce((sum, count) => sum + count, 0).toLocaleString(),
          'Across all categories'
        )}
        
        {renderMetricCard(
          'Categories',
          Object.keys(insights.categories).length,
          'Distinct categories'
        )}
        
        {renderMetricCard(
          'Top Terms',
          insights.topTerms.length,
          'Most frequent terms'
        )}
        
        {insights.sentimentAnalysis && renderMetricCard(
          'Avg Sentiment',
          insights.sentimentAnalysis.average?.toFixed(2) || 'N/A',
          insights.sentimentAnalysis.distribution?.positive > insights.sentimentAnalysis.distribution?.negative ? 'Positive' : 'Negative'
        )}
      </div>

      {/* Summary and Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Summary */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            AI Summary
          </h3>
          <div className="text-gray-700 dark:text-gray-300 leading-relaxed">
            {insights.summary ? (
              <p>{insights.summary}</p>
            ) : (
              <p className="text-gray-500 italic">Generating summary...</p>
            )}
          </div>
        </div>

        {/* Top Terms */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Top Terms
          </h3>
          <div className="flex flex-wrap gap-2">
            {insights.topTerms.slice(0, 20).map((term, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                style={{
                  fontSize: `${Math.max(0.7, 1 - index * 0.05)}rem`
                }}
              >
                {typeof term === 'object' ? term.term : term}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {renderCategoryChart()}
        {renderTimeChart()}
      </div>

      {/* Trends and Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trends */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Trends
          </h3>
          <div className="space-y-3">
            {insights.trends.length > 0 ? (
              insights.trends.map((trend, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
                  <p className="text-gray-700 dark:text-gray-300 text-sm">
                    {typeof trend === 'object' ? trend.description : trend}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 italic">No trends detected</p>
            )}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-600">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Recommendations
          </h3>
          <div className="space-y-3">
            {insights.recommendations.length > 0 ? (
              insights.recommendations.map((rec, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-green-600 rounded-full mt-2"></div>
                  <p className="text-gray-700 dark:text-gray-300 text-sm">
                    {typeof rec === 'object' ? rec.text : rec}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-gray-500 italic">No recommendations available</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsightsDashboard;