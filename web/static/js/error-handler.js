// Error handler for College Counselor app
// This script adds robust error handling to prevent 500 errors from breaking the UI

document.addEventListener('DOMContentLoaded', function() {
  // Global error handler for API requests
  window.handleApiError = function(error, fallbackData, elementId) {
    console.error('API Error:', error);
    
    // Show notification to user
    if (window.notificationSystem) {
      window.notificationSystem.error('Error loading data. Using fallback data instead.');
    }
    
    // If fallback data and element ID provided, update the element
    if (fallbackData && elementId) {
      const element = document.getElementById(elementId);
      if (element && typeof fallbackData === 'function') {
        fallbackData(element);
      }
    }
    
    // Return fallback data
    return fallbackData || {};
  };
  
  // Add global error handler for all fetch requests
  const originalFetch = window.fetch;
  window.fetch = function() {
    return originalFetch.apply(this, arguments)
      .catch(error => {
        console.error('Fetch error:', error);
        if (window.notificationSystem) {
          window.notificationSystem.error('Network request failed. Please try again later.');
        }
        // Return empty response to prevent unhandled promise rejections
        return new Response(JSON.stringify({
          error: true,
          message: 'Network request failed',
          data: {}
        }));
      });
  };
  
  // Add global error handler for all API client requests
  if (window.apiClient) {
    const originalGet = window.apiClient.get;
    window.apiClient.get = function(endpoint) {
      return originalGet.call(this, endpoint)
        .catch(error => {
          console.error('API GET error:', error);
          return window.handleApiError(error, {});
        });
    };
    
    const originalPost = window.apiClient.post;
    window.apiClient.post = function(endpoint, data) {
      return originalPost.call(this, endpoint, data)
        .catch(error => {
          console.error('API POST error:', error);
          return window.handleApiError(error, {});
        });
    };
  }
  
  // Add fallback for missing elements
  const checkMissingElements = function() {
    // Check for notification container
    if (!document.getElementById('notification-container')) {
      const container = document.createElement('div');
      container.id = 'notification-container';
      container.className = 'position-fixed top-0 end-0 p-3';
      container.style.zIndex = '1050';
      document.body.appendChild(container);
    }
  };
  
  // Run checks
  checkMissingElements();
  
  // Add window error handler
  window.addEventListener('error', function(event) {
    console.error('Global error caught:', event.error);
    if (window.notificationSystem) {
      window.notificationSystem.error('An error occurred. Some features may not work correctly.');
    }
    // Prevent the error from breaking the entire page
    event.preventDefault();
  });
});
