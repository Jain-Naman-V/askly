import { configureStore } from '@reduxjs/toolkit';
import searchReducer from './slices/searchSlice';
import dataReducer from './slices/dataSlice';
import aiReducer from './slices/aiSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    search: searchReducer,
    data: dataReducer,
    ai: aiReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});