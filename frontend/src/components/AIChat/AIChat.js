import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { aiService } from '../../services/aiService';
import { performSearch } from '../../store/slices/searchSlice';

const AIChat = () => {
  const dispatch = useDispatch();
  const { results } = useSelector(state => state.search);
  
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: 'Hello! I\'m your AI Data Agent. Ask me anything about your data, and I\'ll help you find insights, search for specific information, or analyze patterns.',
      timestamp: new Date().toISOString()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([
    "What are the most recent entries in my data?",
    "Show me data with the highest scores",
    "Analyze trends in my dataset",
    "Find all records from this month"
  ]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (messageText = null) => {
    const message = messageText || inputMessage.trim();
    if (!message || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // First, process the query to understand intent
      const queryResponse = await aiService.processQuery(message);
      
      let aiResponse = '';
      let searchResults = null;
      let insights = null;

      // If the query suggests a search, perform it
      if (queryResponse.suggested_action === 'search' && queryResponse.search_query) {
        const searchParams = {
          query: queryResponse.search_query,
          search_type: queryResponse.search_type || 'hybrid',
          limit: 10
        };
        
        const searchResponse = await dispatch(performSearch(searchParams)).unwrap();
        searchResults = searchResponse.results;
        
        // Generate insights from search results
        if (searchResults && searchResults.length > 0) {
          const insightsResponse = await aiService.generateInsights({
            recordIds: searchResults.slice(0, 5).map(r => r.id),
            searchQuery: message
          });
          insights = insightsResponse.insights;
        }
      }

      // Get AI response with context
      const chatResponse = await aiService.chat(message, searchResults);
      aiResponse = chatResponse.response;

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toISOString(),
        searchResults: searchResults,
        insights: insights,
        metadata: {
          processingTime: chatResponse.processing_time,
          confidence: chatResponse.confidence
        }
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div className={`max-w-3xl px-4 py-3 rounded-lg ${
          isUser 
            ? 'bg-blue-600 text-white' 
            : message.isError 
              ? 'bg-red-50 border border-red-200 text-red-800'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {/* Search Results Preview */}
          {message.searchResults && message.searchResults.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="text-sm font-medium mb-2">Found {message.searchResults.length} results:</div>
              <div className="space-y-2">
                {message.searchResults.slice(0, 3).map((result, index) => (
                  <div key={index} className="bg-white dark:bg-gray-800 p-2 rounded border text-xs">
                    <div className="font-medium">{result.title || 'Untitled'}</div>
                    {result.description && (
                      <div className="text-gray-600 dark:text-gray-400 mt-1">
                        {result.description.substring(0, 100)}...
                      </div>
                    )}
                    {result.score && (
                      <div className="text-blue-600 dark:text-blue-400 mt-1">
                        Score: {result.score.toFixed(3)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Insights */}
          {message.insights && (
            <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
              <div className="text-sm font-medium mb-2">Key Insights:</div>
              <div className="text-sm bg-blue-50 dark:bg-blue-900 p-2 rounded">
                {message.insights}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs opacity-70 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
            {message.metadata && (
              <span className="ml-2">
                • {message.metadata.processingTime}ms
                {message.metadata.confidence && ` • ${Math.round(message.metadata.confidence * 100)}% confidence`}
              </span>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          AI Data Agent
        </h2>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-sm text-gray-600 dark:text-gray-400">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(renderMessage)}
        
        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-100 dark:bg-gray-700 px-4 py-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-gray-600 dark:text-gray-400">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && messages.length <= 1 && (
        <div className="px-4 pb-2">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Try asking:</div>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSendMessage(suggestion)}
                className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                disabled={isLoading}
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-600">
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your data..."
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSendMessage()}
            disabled={isLoading || !inputMessage.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChat;