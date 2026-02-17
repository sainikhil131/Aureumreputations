// Suppress browser extension console errors
(function() {
    // Store original console methods
    const originalError = console.error;
    const originalWarn = console.warn;

    // Filter out extension-related errors
    console.error = function(...args) {
        const message = args.join(' ');
        // Ignore chrome-extension and extension-related errors
        if (message.includes('chrome-extension://') ||
            message.includes('content.js') ||
            message.includes('inpage.js') ||
            message.includes('web_accessible_resources')) {
            return; // Suppress these errors
        }
        originalError.apply(console, args);
    };

    console.warn = function(...args) {
        const message = args.join(' ');
        // Ignore extension-related warnings
        if (message.includes('chrome-extension://') ||
            message.includes('content.js') ||
            message.includes('inpage.js')) {
            return; // Suppress these warnings
        }
        originalWarn.apply(console, args);
    };

    // Suppress LaunchDarkly and other extension logs
    window.addEventListener('error', function(e) {
        if (e.filename && (e.filename.includes('chrome-extension://') ||
            e.filename.includes('content.js') ||
            e.filename.includes('general.js'))) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, true);
})();

// Professional scroll-triggered animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            // Add staggered delay for cards
            if (entry.target.classList.contains('card')) {
                const cards = entry.target.parentElement.querySelectorAll('.card');
                cards.forEach((card, i) => {
                    setTimeout(() => {
                        card.classList.add('visible');
                    }, i * 150);
                });
            } else {
                entry.target.classList.add('visible');
            }
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Page loader - seamless transition
let loaderRemoved = false;

function removeLoader() {
    if (loaderRemoved) return;
    loaderRemoved = true;

    const loader = document.querySelector('.page-loader');
    const body = document.body;

    // Ensure page stays at top
    window.scrollTo(0, 0);
    document.documentElement.scrollTop = 0;

    // Start fade out immediately - no delay
    setTimeout(() => {
        if (loader) loader.classList.add('hidden');
        // Remove loading class immediately to start hero animations
        body.classList.remove('loading');

        // Remove loader from DOM after fade transition completes
        setTimeout(() => {
            if (loader && loader.parentNode) {
                loader.parentNode.removeChild(loader);
            }
        }, 600); // Match the transition duration
    }, 500); // Reduced from 800ms to 500ms
}

// Multiple triggers to ensure loader is removed
window.addEventListener('load', removeLoader);

// Fallback in case load event doesn't fire
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(removeLoader, 1500); // Reduced from 2000ms
});

document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    const sections = document.querySelectorAll('section:not(.hero)');
    const dividers = document.querySelectorAll('.section-divider');

    // Observe sections and dividers
    sections.forEach(section => observer.observe(section));
    dividers.forEach(divider => observer.observe(divider));

    // Observe Aureum Core section
    const coreSection = document.querySelector('.aureum-core-section');
    if (coreSection) observer.observe(coreSection);

    // Observe first card in each grid to trigger all cards
    const cardGrids = document.querySelectorAll('.card-grid');
    cardGrids.forEach(grid => {
        const firstCard = grid.querySelector('.card');
        if (firstCard) observer.observe(firstCard);
    });

    // Observe services CTA container
    const servicesCTA = document.querySelector('.services-cta-container');
    if (servicesCTA) observer.observe(servicesCTA);

    // Observe testimonial cards with staggered animation
    const testimonialCards = document.querySelectorAll('.testimonial-card');
    testimonialCards.forEach((card, index) => {
        setTimeout(() => {
            observer.observe(card);
        }, index * 100);
    });

    // Observe review items on reviews page with staggered animation
    const reviewItems = document.querySelectorAll('.review-item');
    reviewItems.forEach((item, index) => {
        setTimeout(() => {
            observer.observe(item);
        }, index * 150);
    });

    // Smooth scrolling for navigation with offset for fixed header
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Only prevent default and smooth scroll if it's a hash link on the same page
            if (href.startsWith('#')) {
                e.preventDefault();
                const targetSection = document.querySelector(href);

                if (targetSection) {
                    const headerHeight = document.querySelector('header').offsetHeight;
                    const targetPosition = targetSection.offsetTop - headerHeight - 20;

                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            }
            // For links with full URLs (like {{ url_for('index') }}#section), let them navigate normally
        });
    });

    // Advanced scroll effects
    let lastScroll = 0;
    let ticking = false;
    let userHasScrolled = false;

    window.addEventListener('scroll', () => {
        userHasScrolled = true;

        if (!ticking) {
            window.requestAnimationFrame(() => {
                const scrolled = window.pageYOffset;

                // Header scroll effect
                if (scrolled > 50) {
                    header.classList.add('scrolled');
                } else {
                    header.classList.remove('scrolled');
                }

                // Hero fade effect on scroll (subtle, no parallax movement)
                const hero = document.querySelector('.hero');
                if (hero && scrolled > 0 && scrolled < window.innerHeight) {
                    hero.style.opacity = 1 - (scrolled / window.innerHeight) * 0.5;
                }

                lastScroll = scrolled;
                ticking = false;
            });
            ticking = true;
        }
    });

    // Add magnetic effect to button
    const heroBtn = document.querySelector('.hero-btn');
    if (heroBtn) {
        heroBtn.addEventListener('mousemove', (e) => {
            const rect = heroBtn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            heroBtn.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px) scale(1.05)`;
        });

        heroBtn.addEventListener('mouseleave', () => {
            heroBtn.style.transform = 'translate(0, 0) scale(1)';
        });

        // Open consultation modal when hero button is clicked
        heroBtn.addEventListener('click', () => {
            openConsultationModal();
        });
    }

    // Consultation Modal Functionality
    const modal = document.getElementById('consultationModal');
    const closeModalBtn = document.getElementById('closeModal');
    const consultationForm = document.getElementById('consultationForm');
    const navConsultationBtn = document.getElementById('navConsultationBtn');

    function openConsultationModal() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    function closeConsultationModal() {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
        // Reset form after closing
        setTimeout(() => {
            consultationForm.reset();
            const messageDiv = document.querySelector('.form-message-modal');
            if (messageDiv) {
                messageDiv.classList.remove('show', 'success', 'error');
            }
        }, 300);
    }

    // Close modal when clicking the close button
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeConsultationModal);
    }

    // Close modal when clicking outside the modal container
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeConsultationModal();
            }
        });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeConsultationModal();
        }
    });

    // Open modal when navigation consultation button is clicked
    if (navConsultationBtn) {
        navConsultationBtn.addEventListener('click', () => {
            openConsultationModal();
        });
    }

    // Handle consultation form submission
    if (consultationForm) {
        consultationForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitButton = consultationForm.querySelector('button[type="submit"]');
            const messageDiv = document.querySelector('.form-message-modal') || createModalMessageDiv();

            // Get form data
            const formData = {
                name: document.getElementById('consult-name').value,
                business_name: document.getElementById('consult-business').value,
                email: document.getElementById('consult-email').value,
                phone: document.getElementById('consult-phone').value,
                service: document.getElementById('consult-service').value,
                message: document.getElementById('consult-message').value
            };

            // Disable submit button
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

            try {
                // Use APP_ROOT if available for subdirectory deployment
                const appRoot = window.APP_ROOT || '';
                const response = await fetch(`${appRoot}/send-consultation`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    showModalMessage(messageDiv, result.message, 'success');
                    consultationForm.reset();
                    // Close modal after 3 seconds
                    setTimeout(() => {
                        closeConsultationModal();
                    }, 3000);
                } else {
                    showModalMessage(messageDiv, result.message, 'error');
                }
            } catch (error) {
                showModalMessage(messageDiv, 'An error occurred. Please try again later.', 'error');
            } finally {
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Request Free Consultation';
            }
        });
    }

    // Contact form submission
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitButton = contactForm.querySelector('button[type="submit"]');
            const messageDiv = document.querySelector('.form-message') || createMessageDiv();

            // Get form data
            const formData = {
                name: contactForm.querySelector('input[type="text"]').value,
                business_name: contactForm.querySelectorAll('input[type="text"]')[1].value,
                email: contactForm.querySelector('input[type="email"]').value,
                message: contactForm.querySelector('textarea').value
            };

            // Disable submit button
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 8px;"></i>Sending...';

            try {
                // Use APP_ROOT if available for subdirectory deployment
                const appRoot = window.APP_ROOT || '';
                const response = await fetch(`${appRoot}/send-email`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    showMessage(messageDiv, result.message, 'success');
                    contactForm.reset();
                } else {
                    showMessage(messageDiv, result.message, 'error');
                }
            } catch (error) {
                showMessage(messageDiv, 'An error occurred. Please try again later.', 'error');
            } finally {
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.innerHTML = '<i class="fas fa-paper-plane" style="margin-right: 8px;"></i>Request Consultation';
            }
        });
    }
});

function createMessageDiv() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'form-message';
    const contactForm = document.querySelector('.contact-form');
    contactForm.appendChild(messageDiv);
    return messageDiv;
}

function showMessage(messageDiv, text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `form-message ${type}`;
    messageDiv.style.display = 'block';

    // Hide message after 5 seconds
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function createModalMessageDiv() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'form-message-modal';
    const consultationForm = document.getElementById('consultationForm');
    consultationForm.appendChild(messageDiv);
    return messageDiv;
}

function showModalMessage(messageDiv, text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `form-message-modal show ${type}`;

    // Hide message after 5 seconds
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

// Hamburger Menu Toggle
const hamburgerMenu = document.getElementById('hamburgerMenu');
const mainNav = document.getElementById('mainNav');

if (hamburgerMenu && mainNav) {
    hamburgerMenu.addEventListener('click', function() {
        this.classList.toggle('active');
        mainNav.classList.toggle('active');
        document.body.style.overflow = mainNav.classList.contains('active') ? 'hidden' : '';
    });

    // Close menu when clicking on a nav link
    const navLinks = mainNav.querySelectorAll('a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            hamburgerMenu.classList.remove('active');
            mainNav.classList.remove('active');
            document.body.style.overflow = '';
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = mainNav.contains(event.target);
        const isClickOnHamburger = hamburgerMenu.contains(event.target);

        if (!isClickInsideNav && !isClickOnHamburger && mainNav.classList.contains('active')) {
            hamburgerMenu.classList.remove('active');
            mainNav.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && mainNav.classList.contains('active')) {
            hamburgerMenu.classList.remove('active');
            mainNav.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Reviews page consultation button
    const reviewsConsultationBtn = document.getElementById('reviewsConsultationBtn');
    if (reviewsConsultationBtn) {
        reviewsConsultationBtn.addEventListener('click', () => {
            openConsultationModal();
        });
    }
}
