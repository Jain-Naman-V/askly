import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { searchService } from '../../services/searchService';

// Async thunks
export const performSearch = createAsyncThunk(
  'search/performSearch',
  async (searchParams, { rejectWithValue }) => {
    try {
      const response = await searchService.search(searchParams);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const getSearchSuggestions = createAsyncThunk(
  'search/getSuggestions',
  async (query, { rejectWithValue }) => {
    try {
      const response = await searchService.getSuggestions(query);
      return response.suggestions;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const getSearchFacets = createAsyncThunk(
  'search/getFacets',
  async (query, { rejectWithValue }) => {
    try {
      const response = await searchService.getFacets(query);
      return response.facets;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  // Search state
  query: '',
  results: [],
  totalCount: 0,
  returnedCount: 0,
  offset: 0,
  limit: 50,
  searchType: 'hybrid',
  filters: {},
  facets: {},
  suggestions: [],
  insights: null,
  
  // UI state
  isLoading: false,
  error: null,
  
  // Search history
  recentSearches: [],
  savedSearches: [],
  
  // Performance
  processingTime: 0,
};

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    setQuery: (state, action) => {
      state.query = action.payload;
    },
    setSearchType: (state, action) => {
      state.searchType = action.payload;
    },
    setFilters: (state, action) => {
      state.filters = action.payload;
    },
    updateFilter: (state, action) => {
      const { key, value } = action.payload;
      if (value === null || value === undefined || value === '') {
        delete state.filters[key];
      } else {
        state.filters[key] = value;
      }
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setLimit: (state, action) => {
      state.limit = action.payload;
    },
    setOffset: (state, action) => {
      state.offset = action.payload;
    },
    clearResults: (state) => {
      state.results = [];
      state.totalCount = 0;
      state.returnedCount = 0;
      state.insights = null;
    },
    addToRecentSearches: (state, action) => {
      const search = action.payload;
      state.recentSearches = [
        search,
        ...state.recentSearches.filter(s => s.query !== search.query).slice(0, 9)
      ];
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Perform search
      .addCase(performSearch.pending, (state) => {
        state.isLoading = true;
        state.error = null;
        state.query = '';
      })
      .addCase(performSearch.fulfilled, (state, action) => {
        state.isLoading = false;
        state.results = action.payload.results || [];
        state.totalCount = action.payload.total_count || 0;
        state.returnedCount = action.payload.returned_count || 0;
        state.processingTime = action.payload.processing_time || 0;
        state.insights = action.payload.insights || null;
        state.query = action.meta.arg.query;
        
        // Add to recent searches
        const searchRecord = {
          query: action.meta.arg.query,
          searchType: action.meta.arg.search_type || 'hybrid',
          filters: action.meta.arg.filters || {},
          timestamp: new Date().toISOString(),
          resultCount: action.payload.total_count || 0,
        };
        state.recentSearches = [
          searchRecord,
          ...state.recentSearches.filter(s => s.query !== searchRecord.query).slice(0, 9)
        ];
      })
      .addCase(performSearch.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
        state.results = [];
        state.totalCount = 0;
      })
      
      // Get suggestions
      .addCase(getSearchSuggestions.fulfilled, (state, action) => {
        state.suggestions = action.payload;
      })
      
      // Get facets
      .addCase(getSearchFacets.fulfilled, (state, action) => {
        state.facets = action.payload;
      });
  },
});

export const {
  setQuery,
  setSearchType,
  setFilters,
  updateFilter,
  clearFilters,
  setLimit,
  setOffset,
  clearResults,
  addToRecentSearches,
  clearError,
} = searchSlice.actions;

export default searchSlice.reducer;