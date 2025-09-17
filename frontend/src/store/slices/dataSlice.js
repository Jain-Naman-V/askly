import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { dataService } from '../../services/dataService';

// Async thunks
export const fetchRecord = createAsyncThunk(
  'data/fetchRecord',
  async (recordId, { rejectWithValue }) => {
    try {
      const response = await dataService.getRecord(recordId);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const createRecord = createAsyncThunk(
  'data/createRecord',
  async (recordData, { rejectWithValue }) => {
    try {
      const response = await dataService.createRecord(recordData);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const updateRecord = createAsyncThunk(
  'data/updateRecord',
  async ({ recordId, updates }, { rejectWithValue }) => {
    try {
      const response = await dataService.updateRecord(recordId, updates);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const deleteRecord = createAsyncThunk(
  'data/deleteRecord',
  async ({ recordId, softDelete = true }, { rejectWithValue }) => {
    try {
      await dataService.deleteRecord(recordId, softDelete);
      return recordId;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const bulkOperation = createAsyncThunk(
  'data/bulkOperation',
  async (operationData, { rejectWithValue }) => {
    try {
      const response = await dataService.bulkOperation(operationData);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const importData = createAsyncThunk(
  'data/importData',
  async ({ file, format, mapping }, { rejectWithValue }) => {
    try {
      const response = await dataService.importData(file, format, mapping);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchAnalytics = createAsyncThunk(
  'data/fetchAnalytics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await dataService.getAnalytics();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const validateRecord = createAsyncThunk(
  'data/validateRecord',
  async (recordData, { rejectWithValue }) => {
    try {
      const response = await dataService.validateRecord(recordData);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  // Records
  records: {},
  currentRecord: null,
  
  // Analytics
  analytics: null,
  
  // Validation
  validationResult: null,
  
  // Bulk operations
  bulkOperationResult: null,
  
  // Import/Export
  importResult: null,
  isImporting: false,
  
  // UI state
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,
  isFetchingAnalytics: false,
  isValidating: false,
  
  // Errors
  error: null,
  validationErrors: [],
  
  // Form state
  formData: {
    title: '',
    description: '',
    content: {},
    tags: [],
    category: '',
    metadata: {},
  },
  
  // Filters and sorting
  filters: {},
  sortBy: 'created_at',
  sortOrder: 'desc',
};

const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    setCurrentRecord: (state, action) => {
      state.currentRecord = action.payload;
    },
    updateFormData: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    resetFormData: (state) => {
      state.formData = {
        title: '',
        description: '',
        content: {},
        tags: [],
        category: '',
        metadata: {},
      };
    },
    setFormField: (state, action) => {
      const { field, value } = action.payload;
      state.formData[field] = value;
    },
    addTag: (state, action) => {
      const tag = action.payload;
      if (!state.formData.tags.includes(tag)) {
        state.formData.tags.push(tag);
      }
    },
    removeTag: (state, action) => {
      const tag = action.payload;
      state.formData.tags = state.formData.tags.filter(t => t !== tag);
    },
    setContentField: (state, action) => {
      const { key, value } = action.payload;
      state.formData.content[key] = value;
    },
    removeContentField: (state, action) => {
      const key = action.payload;
      delete state.formData.content[key];
    },
    clearError: (state) => {
      state.error = null;
      state.validationErrors = [];
    },
    clearValidationResult: (state) => {
      state.validationResult = null;
      state.validationErrors = [];
    },
    setFilters: (state, action) => {
      state.filters = action.payload;
    },
    setSorting: (state, action) => {
      const { sortBy, sortOrder } = action.payload;
      state.sortBy = sortBy;
      state.sortOrder = sortOrder;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch record
      .addCase(fetchRecord.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchRecord.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentRecord = action.payload;
        state.records[action.payload.id] = action.payload;
      })
      .addCase(fetchRecord.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Create record
      .addCase(createRecord.pending, (state) => {
        state.isCreating = true;
        state.error = null;
      })
      .addCase(createRecord.fulfilled, (state, action) => {
        state.isCreating = false;
        state.records[action.payload.id] = action.payload;
        state.currentRecord = action.payload;
        // Reset form data after successful creation
        state.formData = {
          title: '',
          description: '',
          content: {},
          tags: [],
          category: '',
          metadata: {},
        };
      })
      .addCase(createRecord.rejected, (state, action) => {
        state.isCreating = false;
        state.error = action.payload;
      })
      
      // Update record
      .addCase(updateRecord.pending, (state) => {
        state.isUpdating = true;
        state.error = null;
      })
      .addCase(updateRecord.fulfilled, (state, action) => {
        state.isUpdating = false;
        state.records[action.payload.id] = action.payload;
        if (state.currentRecord?.id === action.payload.id) {
          state.currentRecord = action.payload;
        }
      })
      .addCase(updateRecord.rejected, (state, action) => {
        state.isUpdating = false;
        state.error = action.payload;
      })
      
      // Delete record
      .addCase(deleteRecord.pending, (state) => {
        state.isDeleting = true;
        state.error = null;
      })
      .addCase(deleteRecord.fulfilled, (state, action) => {
        state.isDeleting = false;
        const recordId = action.payload;
        delete state.records[recordId];
        if (state.currentRecord?.id === recordId) {
          state.currentRecord = null;
        }
      })
      .addCase(deleteRecord.rejected, (state, action) => {
        state.isDeleting = false;
        state.error = action.payload;
      })
      
      // Bulk operation
      .addCase(bulkOperation.fulfilled, (state, action) => {
        state.bulkOperationResult = action.payload;
      })
      
      // Import data
      .addCase(importData.pending, (state) => {
        state.isImporting = true;
        state.error = null;
      })
      .addCase(importData.fulfilled, (state, action) => {
        state.isImporting = false;
        state.importResult = action.payload;
      })
      .addCase(importData.rejected, (state, action) => {
        state.isImporting = false;
        state.error = action.payload;
      })
      
      // Fetch analytics
      .addCase(fetchAnalytics.pending, (state) => {
        state.isFetchingAnalytics = true;
      })
      .addCase(fetchAnalytics.fulfilled, (state, action) => {
        state.isFetchingAnalytics = false;
        state.analytics = action.payload;
      })
      .addCase(fetchAnalytics.rejected, (state, action) => {
        state.isFetchingAnalytics = false;
        state.error = action.payload;
      })
      
      // Validate record
      .addCase(validateRecord.pending, (state) => {
        state.isValidating = true;
      })
      .addCase(validateRecord.fulfilled, (state, action) => {
        state.isValidating = false;
        state.validationResult = action.payload;
        if (!action.payload.is_valid) {
          state.validationErrors = action.payload.errors;
        }
      })
      .addCase(validateRecord.rejected, (state, action) => {
        state.isValidating = false;
        state.error = action.payload;
      });
  },
});

export const {
  setCurrentRecord,
  updateFormData,
  resetFormData,
  setFormField,
  addTag,
  removeTag,
  setContentField,
  removeContentField,
  clearError,
  clearValidationResult,
  setFilters,
  setSorting,
} = dataSlice.actions;

export default dataSlice.reducer;