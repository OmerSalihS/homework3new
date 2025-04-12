document.addEventListener('DOMContentLoaded', function() {
    const feedbackBtn = document.getElementById('feedback-btn');
    const feedbackContainer = document.getElementById('feedback-form-container');
    const cancelBtn = document.getElementById('cancel-feedback');
    
    feedbackBtn.addEventListener('click', function() {
      feedbackContainer.classList.add('visible');
    });
    
    cancelBtn.addEventListener('click', function() {
      feedbackContainer.classList.remove('visible');
    });
    
    feedbackContainer.addEventListener('click', function(event) {
      if (event.target === feedbackContainer) {
        feedbackContainer.classList.remove('visible');
      }
    });
  });