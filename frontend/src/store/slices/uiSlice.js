import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // Theme
  theme: 'light', // 'light' | 'dark' | 'system'
  
  // Layout
  sidebarOpen: true,
  sidebarCollapsed: false,
  
  // Modals and dialogs
  activeModal: null,
  modalData: null,
  
  // Notifications
  notifications: [],
  
  // Loading states
  globalLoading: false,
  
  // View preferences
  viewMode: 'grid', // 'grid' | 'list' | 'table'
  resultsPerPage: 50,
  
  // Search UI
  searchInputFocused: false,
  showAdvancedSearch: false,
  showFilters: false,
  
  // Data view
  selectedRecords: [],
  showRecordDetails: false,
  recordDetailsId: null,
  
  // AI Chat
  chatOpen: false,
  chatMinimized: false,
  
  // Settings
  autoSave: true,
  confirmDelete: true,
  showHints: true,
  
  // Performance
  enableAnimations: true,
  enableSounds: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme
    setTheme: (state, action) => {
      state.theme = action.payload;
      localStorage.setItem('theme', action.payload);
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', state.theme);
    },
    
    // Sidebar
    setSidebarOpen: (state, action) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarCollapsed: (state, action) => {
      state.sidebarCollapsed = action.payload;
    },
    toggleSidebarCollapsed: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed;
    },
    
    // Modals
    openModal: (state, action) => {
      state.activeModal = action.payload.type;
      state.modalData = action.payload.data || null;
    },
    closeModal: (state) => {
      state.activeModal = null;
      state.modalData = null;
    },
    
    // Notifications
    addNotification: (state, action) => {
      const notification = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...action.payload,
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        notification => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    // Loading
    setGlobalLoading: (state, action) => {
      state.globalLoading = action.payload;
    },
    
    // View mode
    setViewMode: (state, action) => {
      state.viewMode = action.payload;
      localStorage.setItem('viewMode', action.payload);
    },
    setResultsPerPage: (state, action) => {
      state.resultsPerPage = action.payload;
      localStorage.setItem('resultsPerPage', action.payload.toString());
    },
    
    // Search UI
    setSearchInputFocused: (state, action) => {
      state.searchInputFocused = action.payload;
    },
    setShowAdvancedSearch: (state, action) => {
      state.showAdvancedSearch = action.payload;
    },
    toggleAdvancedSearch: (state) => {
      state.showAdvancedSearch = !state.showAdvancedSearch;
    },
    setShowFilters: (state, action) => {
      state.showFilters = action.payload;
    },
    toggleFilters: (state) => {
      state.showFilters = !state.showFilters;
    },
    
    // Record selection
    selectRecord: (state, action) => {
      const recordId = action.payload;
      if (!state.selectedRecords.includes(recordId)) {
        state.selectedRecords.push(recordId);
      }
    },
    deselectRecord: (state, action) => {
      const recordId = action.payload;
      state.selectedRecords = state.selectedRecords.filter(id => id !== recordId);
    },
    toggleRecordSelection: (state, action) => {
      const recordId = action.payload;
      if (state.selectedRecords.includes(recordId)) {
        state.selectedRecords = state.selectedRecords.filter(id => id !== recordId);
      } else {
        state.selectedRecords.push(recordId);
      }
    },
    selectAllRecords: (state, action) => {
      state.selectedRecords = action.payload; // Array of all record IDs
    },
    clearSelectedRecords: (state) => {
      state.selectedRecords = [];
    },
    
    // Record details
    showRecordDetails: (state, action) => {
      state.showRecordDetails = true;
      state.recordDetailsId = action.payload;
    },
    hideRecordDetails: (state) => {
      state.showRecordDetails = false;
      state.recordDetailsId = null;
    },
    
    // AI Chat
    setChatOpen: (state, action) => {
      state.chatOpen = action.payload;
    },
    toggleChat: (state) => {
      state.chatOpen = !state.chatOpen;
    },
    setChatMinimized: (state, action) => {
      state.chatMinimized = action.payload;
    },
    toggleChatMinimized: (state) => {
      state.chatMinimized = !state.chatMinimized;
    },
    
    // Settings
    updateSettings: (state, action) => {
      const settings = action.payload;
      Object.keys(settings).forEach(key => {
        if (key in state) {
          state[key] = settings[key];
          localStorage.setItem(key, JSON.stringify(settings[key]));
        }
      });
    },
    
    // Initialize from localStorage
    initializeUI: (state) => {
      // Load theme
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme) {
        state.theme = savedTheme;
      }
      
      // Load view mode
      const savedViewMode = localStorage.getItem('viewMode');
      if (savedViewMode) {
        state.viewMode = savedViewMode;
      }
      
      // Load results per page
      const savedResultsPerPage = localStorage.getItem('resultsPerPage');
      if (savedResultsPerPage) {
        state.resultsPerPage = parseInt(savedResultsPerPage, 10);
      }
      
      // Load other settings
      const settingsKeys = ['autoSave', 'confirmDelete', 'showHints', 'enableAnimations', 'enableSounds'];
      settingsKeys.forEach(key => {
        const savedValue = localStorage.getItem(key);
        if (savedValue !== null) {
          state[key] = JSON.parse(savedValue);
        }
      });
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  setSidebarOpen,
  toggleSidebar,
  setSidebarCollapsed,
  toggleSidebarCollapsed,
  openModal,
  closeModal,
  addNotification,
  removeNotification,
  clearNotifications,
  setGlobalLoading,
  setViewMode,
  setResultsPerPage,
  setSearchInputFocused,
  setShowAdvancedSearch,
  toggleAdvancedSearch,
  setShowFilters,
  toggleFilters,
  selectRecord,
  deselectRecord,
  toggleRecordSelection,
  selectAllRecords,
  clearSelectedRecords,
  showRecordDetails,
  hideRecordDetails,
  setChatOpen,
  toggleChat,
  setChatMinimized,
  toggleChatMinimized,
  updateSettings,
  initializeUI,
} = uiSlice.actions;

export default uiSlice.reducer;