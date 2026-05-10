document.addEventListener('DOMContentLoaded', () => {
  // Setup Intersection Observer for subtle fade-in animations
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Add visibility class when element comes into view
        entry.target.classList.add('is-visible');
        // Unobserve to run the animation only once
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Select all elements with the fade-in class and observe them
  const fadeElements = document.querySelectorAll('.fade-in');
  fadeElements.forEach(el => observer.observe(el));
});