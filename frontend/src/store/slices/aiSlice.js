import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { aiService } from '../../services/aiService';

// Async thunks
export const sendChatMessage = createAsyncThunk(
  'ai/sendChatMessage',
  async ({ message, contextRecords }, { rejectWithValue }) => {
    try {
      const response = await aiService.chat(message, contextRecords);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const generateInsights = createAsyncThunk(
  'ai/generateInsights',
  async (params, { rejectWithValue }) => {
    try {
      const response = await aiService.generateInsights(params);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const analyzeData = createAsyncThunk(
  'ai/analyzeData',
  async ({ analysisType, filters, limit }, { rejectWithValue }) => {
    try {
      const response = await aiService.analyzeData(analysisType, filters, limit);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const processQuery = createAsyncThunk(
  'ai/processQuery',
  async (query, { rejectWithValue }) => {
    try {
      const response = await aiService.processQuery(query);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  // Chat state
  messages: [],
  isTyping: false,
  
  // Insights
  insights: null,
  isGeneratingInsights: false,
  
  // Analysis
  analysisResults: {},
  isAnalyzing: false,
  
  // Query processing
  processedQuery: null,
  isProcessingQuery: false,
  
  // WebSocket connection
  isConnected: false,
  connectionStatus: 'disconnected',
  
  // General state
  isLoading: false,
  error: null,
  
  // AI service health
  serviceHealth: null,
};

const aiSlice = createSlice({
  name: 'ai',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...action.payload,
      });
    },
    updateMessage: (state, action) => {
      const { id, updates } = action.payload;
      const messageIndex = state.messages.findIndex(msg => msg.id === id);
      if (messageIndex !== -1) {
        state.messages[messageIndex] = {
          ...state.messages[messageIndex],
          ...updates,
        };
      }
    },
    setTyping: (state, action) => {
      state.isTyping = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    setConnectionStatus: (state, action) => {
      state.connectionStatus = action.payload;
      state.isConnected = action.payload === 'connected';
    },
    clearError: (state) => {
      state.error = null;
    },
    setServiceHealth: (state, action) => {
      state.serviceHealth = action.payload;
    },
    setAnalysisResult: (state, action) => {
      const { analysisType, result } = action.payload;
      state.analysisResults[analysisType] = result;
    },
  },
  extraReducers: (builder) => {
    builder
      // Send chat message
      .addCase(sendChatMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        // Add AI response to messages
        state.messages.push({
          id: Date.now(),
          type: 'ai',
          content: action.payload.response,
          timestamp: action.payload.timestamp,
          contextCount: action.payload.context_count,
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Generate insights
      .addCase(generateInsights.pending, (state) => {
        state.isGeneratingInsights = true;
      })
      .addCase(generateInsights.fulfilled, (state, action) => {
        state.isGeneratingInsights = false;
        state.insights = action.payload;
      })
      .addCase(generateInsights.rejected, (state, action) => {
        state.isGeneratingInsights = false;
        state.error = action.payload;
      })
      
      // Analyze data
      .addCase(analyzeData.pending, (state) => {
        state.isAnalyzing = true;
      })
      .addCase(analyzeData.fulfilled, (state, action) => {
        state.isAnalyzing = false;
        const { analysis_type } = action.payload;
        state.analysisResults[analysis_type] = action.payload;
      })
      .addCase(analyzeData.rejected, (state, action) => {
        state.isAnalyzing = false;
        state.error = action.payload;
      })
      
      // Process query
      .addCase(processQuery.pending, (state) => {
        state.isProcessingQuery = true;
      })
      .addCase(processQuery.fulfilled, (state, action) => {
        state.isProcessingQuery = false;
        state.processedQuery = action.payload;
      })
      .addCase(processQuery.rejected, (state, action) => {
        state.isProcessingQuery = false;
        state.error = action.payload;
      });
  },
});

export const {
  addMessage,
  updateMessage,
  setTyping,
  clearMessages,
  setConnectionStatus,
  clearError,
  setServiceHealth,
  setAnalysisResult,
} = aiSlice.actions;

export default aiSlice.reducer;