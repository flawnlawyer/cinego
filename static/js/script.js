// CINEGO - Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Movie card click handler
    const movieCards = document.querySelectorAll('.movie-card');
    movieCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add click animation
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });

    // Search functionality (if search input exists)
    const searchInput = document.querySelector('#search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const movieCards = document.querySelectorAll('.movie-card');
            
            movieCards.forEach(card => {
                const title = card.querySelector('.movie-title').textContent.toLowerCase();
                if (title.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required]');
            let valid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    valid = false;
                    input.style.borderColor = 'var(--secondary-color)';
                } else {
                    input.style.borderColor = '';
                }
            });

            if (!valid) {
                e.preventDefault();
            }
        });
    });

    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        fadeInObserver.observe(section);
    });

    // Add parallax effect to background
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('body::before');
        if (parallax) {
            parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });

    // Dynamic stats counter animation
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent);
        let current = 0;
        const increment = target / 50;
        
        const updateCounter = () => {
            if (current < target) {
                current += increment;
                stat.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                stat.textContent = target;
            }
        };
        
        // Start animation when element is in view
        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    counterObserver.unobserve(entry.target);
                }
            });
        });
        
        counterObserver.observe(stat);
    });
});

// Add loading indicator for page transitions
window.addEventListener('beforeunload', function() {
    document.body.style.opacity = '0.7';
});

// Movie card hover effect enhancement
document.addEventListener('mousemove', function(e) {
    const cards = document.querySelectorAll('.movie-card:hover');
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    // ESC key to close modals or go back
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.active');
        if (modals.length > 0) {
            modals.forEach(modal => modal.classList.remove('active'));
        }
    }
});

console.log('🎬 CINEGO - Ready to stream!');
