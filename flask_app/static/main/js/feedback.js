document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const feedbackBtn = document.getElementById('feedback-btn');
    const feedbackContainer = document.getElementById('feedback-form-container');
    const cancelBtn = document.getElementById('cancel-feedback');
    
    // Toggle feedback form visibility when button is clicked
    feedbackBtn.addEventListener('click', function() {
      feedbackContainer.classList.add('visible');
    });
    
    // Hide feedback form when cancel button is clicked
    cancelBtn.addEventListener('click', function() {
      feedbackContainer.classList.remove('visible');
    });
    
    // Hide feedback form when clicking outside the form
    feedbackContainer.addEventListener('click', function(event) {
      if (event.target === feedbackContainer) {
        feedbackContainer.classList.remove('visible');
      }
    });
  });