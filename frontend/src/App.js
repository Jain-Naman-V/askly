import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SearchInterface from './components/SearchInterface/SearchInterface';
import DataManager from './components/DataManager/DataManager';
import AIChat from './components/AIChat/AIChat';
import InsightsDashboard from './components/DataVisualization/InsightsDashboard';

function App() {
  return (
    <div className="App min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              AI Data Agent
            </h1>
            <nav className="space-x-4">
              <a href="/" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                Dashboard
              </a>
              <a href="/search" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                AI Search
              </a>
              <a href="/chat" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                AI Chat
              </a>
              <a href="/insights" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                Insights
              </a>
              <a href="/data" className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                Data
              </a>
            </nav>
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Welcome to AI Data Agent
              </h2>
              <p className="text-gray-600 dark:text-gray-300 mb-8">
                Your intelligent assistant for structured data management and insights
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    🔍 AI Search
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Use natural language to search through your data with advanced AI
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    🤖 AI Chat
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Chat with AI to get insights and answers from your data
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    📊 Real-time Insights
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Get real-time analytics and insights from your structured data
                  </p>
                </div>
              </div>
            </div>
          } />
          <Route path="/search" element={<SearchInterface />} />
          <Route path="/chat" element={
            <div className="h-[600px]">
              <AIChat />
            </div>
          } />
          <Route path="/insights" element={<InsightsDashboard />} />
          <Route path="/data" element={<DataManager />} />
          <Route path="*" element={
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                404 - Page Not Found
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                The page you're looking for doesn't exist.
              </p>
            </div>
          } />
        </Routes>
      </main>
    </div>
  );
}

export default App;