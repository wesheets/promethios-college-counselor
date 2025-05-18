// Additional image placeholders for the College Counselor app
// This file creates placeholder images for trust score example and emotion-aware counseling
// These are referenced in the templates and may cause 500 errors if missing

document.addEventListener('DOMContentLoaded', function() {
  // Create fallback images if the actual images fail to load
  const images = document.querySelectorAll('img');
  
  images.forEach(img => {
    img.addEventListener('error', function() {
      // If image fails to load, replace with a colored div
      const placeholder = document.createElement('div');
      placeholder.className = 'image-placeholder';
      placeholder.style.width = '100%';
      placeholder.style.height = '200px';
      placeholder.style.backgroundColor = '#3f51b5';
      placeholder.style.color = 'white';
      placeholder.style.display = 'flex';
      placeholder.style.alignItems = 'center';
      placeholder.style.justifyContent = 'center';
      placeholder.style.borderRadius = '8px';
      
      // Add text based on image alt or src
      const text = document.createElement('span');
      text.textContent = img.alt || img.src.split('/').pop().split('.')[0].replace(/-/g, ' ');
      placeholder.appendChild(text);
      
      // Replace the img with the placeholder
      img.parentNode.replaceChild(placeholder, img);
    });
  });
});
