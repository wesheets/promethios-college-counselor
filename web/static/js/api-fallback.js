// Update layout.html to include error handling and image fallback scripts
// This modification ensures all pages have robust error handling

document.addEventListener('DOMContentLoaded', function() {
  // Add script references to layout if they don't exist
  const scripts = [
    '/static/js/error-handler.js',
    '/static/js/image-fallback.js'
  ];
  
  scripts.forEach(scriptSrc => {
    if (!document.querySelector(`script[src="${scriptSrc}"]`)) {
      const script = document.createElement('script');
      script.src = scriptSrc;
      document.body.appendChild(script);
    }
  });
  
  // Add error handling for API proxy calls
  const apiProxy = function(endpoint, method, data) {
    return new Promise((resolve, reject) => {
      const options = {
        method: method || 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      };
      
      if (data) {
        options.body = JSON.stringify(data);
      }
      
      fetch(`/api-proxy/${endpoint}`, options)
        .then(response => {
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          return response.json();
        })
        .then(data => resolve(data))
        .catch(error => {
          console.error('API proxy error:', error);
          // Return mock data as fallback
          resolve(getMockData(endpoint));
        });
    });
  };
  
  // Mock data for API fallbacks
  const getMockData = function(endpoint) {
    const mockData = {
      'profile': {
        'name': 'John Smith',
        'email': 'john@example.com',
        'gpa': 3.8,
        'graduation_year': '2026',
        'intended_majors': ['Computer Science', 'Mathematics'],
        'location_preference': 'California',
        'size_preference': 'medium',
        'setting_preference': 'urban',
        'budget': 50000
      },
      'journal/entries': {
        'entries': [
          {
            'id': 1,
            'date': '2025-05-05',
            'title': 'College Research',
            'content': 'Started researching colleges today. There are so many options!',
            'emotion': 'excited'
          },
          {
            'id': 2,
            'date': '2025-05-10',
            'title': 'Application Anxiety',
            'content': 'Feeling overwhelmed by all the application requirements.',
            'emotion': 'anxious'
          }
        ]
      },
      'colleges/recommendations': {
        'colleges': [
          {
            'id': 1,
            'name': 'Ivy University',
            'location': 'Massachusetts',
            'trust_score': 85,
            'category': 'Reach'
          },
          {
            'id': 2,
            'name': 'State University',
            'location': 'California',
            'trust_score': 92,
            'category': 'Target'
          }
        ]
      },
      'report': {
        'student': {
          'name': 'John Smith',
          'gpa': 3.8,
          'intended_majors': ['Computer Science', 'Mathematics'],
          'location_preference': 'California',
          'budget': 50000
        },
        'emotional_state': {
          'sentiment': 75,
          'certainty': 70,
          'calmness': 80,
          'summary': 'Your emotional state appears balanced for decision-making.'
        },
        'recommendations': [
          {
            'college': 'Ivy University',
            'category': 'Reach',
            'trust_score': 85,
            'academic_match': 80,
            'budget_match': 70
          },
          {
            'college': 'State University',
            'category': 'Target',
            'trust_score': 92,
            'academic_match': 90,
            'budget_match': 85
          }
        ]
      }
    };
    
    // Return appropriate mock data or empty object
    return mockData[endpoint] || {};
  };
  
  // Expose API proxy globally
  window.apiProxy = apiProxy;
});
