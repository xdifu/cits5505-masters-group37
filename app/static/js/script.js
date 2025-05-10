/**
 * News Sentiment Analyzer Application
 * Enhanced script with improved maintainability and performance
 * 
 * @description Chart rendering, particle effects, 3D tilt effects, AJAX enhancements
 * @version 2.0.0
 */

// Immediately Invoked Function Expression (IIFE) to avoid global namespace pollution
(function() {
    // Configuration constants
    const CONFIG = {
        SELECTORS: {
            sentimentChart: '#sentimentChart',
            analysisForm: '#analysis-form',
            loadingIndicator: '#loading-indicator',
            resultDisplay: '#ajax-result-display',
            navbar: '.navbar',
            navLinks: '.navbar-nav .nav-link',
            tiltCards: '.tilt-card',
            shareForms: '.toggle-share-form',
            particlesContainer: '#particles-js',
            headings: {
                primary: 'h1.display-5',
                secondary: 'h2:not(.typing-active)'
            }
        },
        ANIMATION: {
            TYPING_SPEED: 100,
            TOAST_DELAY: 3000,
            FADE_DURATION: 500
        },
        TILT: {
            MAX_WIDTH: 600,
            SETTINGS: {
                max: 5,
                speed: 300,
                glare: true,
                'max-glare': 0.2,
                scale: 1.02
            }
        },
        SCROLL: {
            THRESHOLD: 50
        },
        PARTICLES: {
            COUNT: 50,
            SIMPLE_SIZE_RANGE: [1, 5],
            ANIMATION_DURATION_RANGE: [10, 30]
        }
    };
    
    // Particles.js configuration
    const PARTICLES_CONFIG = {
        "particles": {
            "number": {
                "value": 80,
                "density": {
                    "enable": true,
                    "value_area": 800
                }
            },
            "color": {
                "value": "#0066ff"
            },
            "shape": {
                "type": "circle",
            },
            "opacity": {
                "value": 0.5,
                "random": true,
            },
            "size": {
                "value": 3,
                "random": true,
            },
            "line_linked": {
                "enable": true,
                "distance": 150,
                "color": "#0066ff",
                "opacity": 0.2,
                "width": 1
            },
            "move": {
                "enable": true,
                "speed": 2,
                "direction": "none",
                "random": true,
                "straight": false,
                "out_mode": "out",
                "bounce": false,
            }
        },
        "interactivity": {
            "detect_on": "canvas",
            "events": {
                "onhover": {
                    "enable": true,
                    "mode": "grab"
                },
                "onclick": {
                    "enable": true,
                    "mode": "push"
                },
                "resize": true
            },
            "modes": {
                "grab": {
                    "distance": 140,
                    "line_linked": {
                        "opacity": 0.8
                    }
                },
                "push": {
                    "particles_nb": 4
                }
            }
        },
        "retina_detect": true
    };
    
    // Environment detection
    const DEBUG = window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';
    
    /**
     * Conditional logging - only logs in development environment
     * @param {...any} args - Arguments to log
     */
    function log(...args) {
        if (DEBUG) {
            console.log(...args);
        }
    }
    
    /**
     * DOM helper functions for common operations
     */
    const DOM = {
        /**
         * Get element by selector
         * @param {string} selector - CSS selector
         * @returns {HTMLElement|null} - Element or null if not found
         */
        get: (selector) => document.querySelector(selector),
        
        /**
         * Get all elements by selector
         * @param {string} selector - CSS selector
         * @returns {NodeList} - Collection of matching elements
         */
        getAll: (selector) => document.querySelectorAll(selector),
        
        /**
         * Show an element
         * @param {HTMLElement} element - Element to show
         * @param {string} display - Display value, defaults to 'block'
         */
        show: (element, display = 'block') => {
            if (element) element.style.display = display;
        },
        
        /**
         * Hide an element
         * @param {HTMLElement} element - Element to hide
         */
        hide: (element) => {
            if (element) element.style.display = 'none';
        },
        
        /**
         * Add class to element
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class to add
         */
        addClass: (element, className) => {
            if (element) element.classList.add(className);
        },
        
        /**
         * Remove class from element
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class to remove
         */
        removeClass: (element, className) => {
            if (element) element.classList.remove(className);
        },
        
        /**
         * Set animation on element
         * @param {HTMLElement} element - Target element
         * @param {string} animation - Animation name
         */
        animate: (element, animation) => {
            if (element) element.style.animation = animation;
        }
    };
    
    /**
     * Standardized error handling
     */
    const ErrorHandler = {
        /**
         * Log an error (both technical and user-friendly)
         * @param {Error} error - Error object
         * @param {string} userMessage - User-friendly message
         */
        handle: (error, userMessage) => {
            // Log technical error details
            log('Error:', error);
            
            // Show user-friendly message
            showToastNotification(userMessage, 'error');
        }
    };
    
    /**
     * Initializes Bootstrap components that require JavaScript activation.
     */
    function initializeBootstrapComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(DOM.getAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(DOM.getAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
        
        // Highlight the active navigation link based on current URL path
        highlightCurrentNavLink();
        
        log('Bootstrap components initialized.');
    }

    /**
     * Highlights the current active navigation link based on URL path
     */
    function highlightCurrentNavLink() {
        // Get current path from window location
        const currentPath = window.location.pathname;
        
        // Find all navigation links
        const navLinks = DOM.getAll(CONFIG.SELECTORS.navLinks);
        
        // Loop through each link
        navLinks.forEach(link => {
            // Get the href attribute
            const href = link.getAttribute('href');
            
            // Remove any previous active class
            DOM.removeClass(link, 'active');
            
            // Check if this link's href matches the current path
            if (href === currentPath) {
                DOM.addClass(link, 'active');
            }
        });
    }

    /**
     * Initializes particle animations for background effects.
     * Uses particles.js library if available, otherwise creates a simple custom effect.
     */
    function initializeParticleEffects() {
        // Check if particles.js is available
        if (typeof particlesJS !== 'undefined') {
            particlesJS(CONFIG.SELECTORS.particlesContainer.substring(1), PARTICLES_CONFIG);
            log('Particles.js initialized');
        } else {
            // Fallback: Create particles container if it doesn't exist
            if (!DOM.get(CONFIG.SELECTORS.particlesContainer)) {
                const particlesContainer = document.createElement('div');
                particlesContainer.id = CONFIG.SELECTORS.particlesContainer.substring(1);
                document.body.prepend(particlesContainer);
                
                // Create simple custom particle effect
                createSimpleParticleEffect(particlesContainer);
                log('Custom particle effect initialized');
            }
        }
    }

    /**
     * Creates a simple particle effect as a fallback when particles.js is not available.
     * @param {HTMLElement} container - The container element for particles
     */
    function createSimpleParticleEffect(container) {
        const particleCount = CONFIG.PARTICLES.COUNT;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'simple-particle';
            
            // Random positioning and properties
            const sizeMin = CONFIG.PARTICLES.SIMPLE_SIZE_RANGE[0];
            const sizeMax = CONFIG.PARTICLES.SIMPLE_SIZE_RANGE[1];
            const size = Math.random() * (sizeMax - sizeMin) + sizeMin;
            
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            
            const durationMin = CONFIG.PARTICLES.ANIMATION_DURATION_RANGE[0];
            const durationMax = CONFIG.PARTICLES.ANIMATION_DURATION_RANGE[1];
            const duration = Math.random() * (durationMax - durationMin) + durationMin;
            
            const delay = Math.random() * 5;
            
            // Apply styles
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.top = `${posY}%`;
            particle.style.position = 'absolute';
            particle.style.borderRadius = '50%';
            particle.style.backgroundColor = 'rgba(0, 102, 255, 0.2)';
            particle.style.animation = `floatParticle ${duration}s ${delay}s infinite linear`;
            
            container.appendChild(particle);
        }
    }

    /**
     * Initializes 3D tilt effects for cards and result containers.
     * Uses vanilla-tilt.js if available, but only on narrow elements
     * to avoid excessive rotation on large panels.
     */
    function initialize3DTiltEffects() {
        const maxWidth = CONFIG.TILT.MAX_WIDTH;
        
        if (typeof VanillaTilt !== 'undefined') {
            // Find all tilt-card elements
            DOM.getAll(CONFIG.SELECTORS.tiltCards).forEach(el => {
                // Only initialize on elements narrower than the max width
                if (el.offsetWidth < maxWidth) {
                    VanillaTilt.init(el, CONFIG.TILT.SETTINGS);
                }
            });
        } else {
            // Fallback: Apply a simple JS-driven tilt on hover for .tilt-card elements
            DOM.getAll(CONFIG.SELECTORS.tiltCards).forEach(card => {
                // Width check for the fallback mechanism
                if (card.offsetWidth < maxWidth) {
                    card.addEventListener('mousemove', function(e) {
                        const cardRect = card.getBoundingClientRect();
                        const cardCenterX = cardRect.left + cardRect.width / 2;
                        const cardCenterY = cardRect.top + cardRect.height / 2;
                        
                        const mouseX = e.clientX - cardCenterX;
                        const mouseY = e.clientY - cardCenterY;
                        
                        // Calculate the rotation values (limited to -5 to 5 degrees)
                        const maxRotation = CONFIG.TILT.SETTINGS.max;
                        const rotateY = mouseX / (cardRect.width / 2) * maxRotation;
                        const rotateX = -mouseY / (cardRect.height / 2) * maxRotation;
                        const scale = CONFIG.TILT.SETTINGS.scale;
                        
                        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${scale}, ${scale}, ${scale})`;
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
                    });
                }
            });
            log('Simple tilt effect initialized as fallback for narrow cards.');
        }
    }

    /**
     * Initializes text animations for headings and important content.
     * Adds typing effects, cyberpunk glitch effects, etc.
     */
    function initializeTextAnimations() {
        // Add cyberpunk title effect
        DOM.getAll(CONFIG.SELECTORS.headings.primary).forEach(heading => {
            if (!heading.classList.contains('cyberpunk-title')) {
                DOM.addClass(heading, 'cyberpunk-title');
                heading.setAttribute('data-text', heading.textContent);
            }
        });
        
        // Add typing animation to secondary headings
        DOM.getAll(CONFIG.SELECTORS.headings.secondary).forEach(heading => {
            const text = heading.textContent;
            heading.textContent = '';
            
            let i = 0;
            const typeInterval = setInterval(() => {
                if (i < text.length) {
                    heading.textContent += text.charAt(i);
                    i++;
                } else {
                    clearInterval(typeInterval);
                    
                    // Add cursor element after typing is complete
                    const cursor = document.createElement('span');
                    cursor.className = 'typing-cursor';
                    heading.appendChild(cursor);
                }
            }, CONFIG.ANIMATION.TYPING_SPEED);
        });
        
        log('Text animations initialized');
    }

    /**
     * Renders the sentiment distribution chart on the results page.
     * Assumes Chart.js library is loaded and data is available.
     */
    function renderSentimentChart() {
        const ctx = DOM.get(CONFIG.SELECTORS.sentimentChart);

        // Check if the canvas element exists and if the chart data is provided
        if (ctx && typeof sentimentData !== 'undefined') {
            log('Rendering sentiment chart with data:', sentimentData);
            try {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Positive', 'Neutral', 'Negative'],
                        datasets: [{
                            label: 'Sentiment Distribution',
                            data: [
                                sentimentData.positive || 0,
                                sentimentData.neutral || 0,
                                sentimentData.negative || 0
                            ],
                            backgroundColor: [
                                'rgba(40, 167, 69, 0.7)',  // Success (Positive)
                                'rgba(108, 117, 125, 0.7)', // Secondary (Neutral)
                                'rgba(220, 53, 69, 0.7)'   // Danger (Negative)
                            ],
                            borderColor: [
                                'rgba(40, 167, 69, 1)',
                                'rgba(108, 117, 125, 1)',
                                'rgba(220, 53, 69, 1)'
                            ],
                            borderWidth: 2,
                            hoverOffset: 15
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        animation: {
                            animateScale: true,
                            animateRotate: true
                        },
                        plugins: {
                            legend: {
                                position: 'top',
                                labels: {
                                    padding: 20,
                                    font: {
                                        size: 14
                                    }
                                }
                            },
                            title: {
                                display: true,
                                text: 'Your Sentiment Analysis Results Distribution',
                                font: {
                                    size: 16,
                                    weight: 'bold'
                                },
                                padding: {
                                    top: 10,
                                    bottom: 30
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            }
                        }
                    }
                });
            } catch (error) {
                ErrorHandler.handle(error, 'Could not render the chart. Please try refreshing the page.');
                
                // Display a user-friendly message
                if (ctx.parentNode) {
                    const errorMsg = document.createElement('div');
                    errorMsg.className = 'alert alert-warning';
                    errorMsg.textContent = 'Could not render the chart. Please try refreshing the page.';
                    ctx.parentNode.appendChild(errorMsg);
                }
            }
        } else {
            if (!ctx) log('Sentiment chart canvas not found.');
            if (typeof sentimentData === 'undefined') log('Sentiment data not found for chart.');
        }
    }

    /**
     * Initializes scroll-based effects for elements like the navbar
     */
    function initializeScrollEffects() {
        // Variables to track scroll state
        let lastScrollTop = 0;
        const navbar = DOM.get(CONFIG.SELECTORS.navbar);
        const scrollThreshold = CONFIG.SCROLL.THRESHOLD;
        
        // Add event listener for scroll
        window.addEventListener('scroll', function() {
            let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
            
            // Check if we've scrolled past the threshold
            if (currentScroll > scrollThreshold) {
                // Scrolling down
                DOM.addClass(navbar, 'navbar-scrolled');
            } else {
                // At top or scrolling up to top
                DOM.removeClass(navbar, 'navbar-scrolled');
            }
            
            // Update last scroll position
            lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
        }, false);
    }

    /**
     * Sets up AJAX submission for the main analysis form.
     */
    function setupAjaxFormSubmissions() {
        const form = DOM.get(CONFIG.SELECTORS.analysisForm);
        const loadingIndicator = DOM.get(CONFIG.SELECTORS.loadingIndicator);
        const resultDisplay = DOM.get(CONFIG.SELECTORS.resultDisplay);
        
        if (form) {
            form.addEventListener('submit', async function(event) {
                event.preventDefault();
                
                // Show loading indicator, clear previous results
                DOM.show(loadingIndicator);
                if (resultDisplay) resultDisplay.innerHTML = '';
                
                try {
                    const formData = new FormData(form);
                    
                    // Form validation
                    const textInput = formData.get('text');
                    if (!textInput || textInput.trim().length < 10) {
                        throw new Error('Please enter at least 10 characters for analysis.');
                    }
                    
                    // Submit form data via AJAX
                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    // Hide loading indicator
                    DOM.hide(loadingIndicator);
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    // Validate response data
                    if (!data || !data.sentiment) {
                        throw new Error('Invalid response from server.');
                    }

                    // Display result with animation
                    displayAnalysisResult(data, resultDisplay);
                    
                } catch (error) {
                    ErrorHandler.handle(error, 'Analysis failed. Please try again.');
                    if (resultDisplay) {
                        resultDisplay.innerHTML = `<div class="alert alert-danger">Analysis failed. Please try again.</div>`;
                    }
                } finally {
                    DOM.hide(loadingIndicator);
                }
            });
        }
    }
    
    /**
     * Displays analysis result with proper formatting and animations
     * @param {Object} data - The result data from the server
     * @param {HTMLElement} container - The container to display results in
     */
    function displayAnalysisResult(data, container) {
        if (!container) return;
        
        let resultHtml = `<h2>Analysis Result:</h2>`;
        resultHtml += `<p class="result-sentiment"><strong>${data.sentiment || 'N/A'}</strong></p>`;
        
        // Add badge based on sentiment
        let badgeClass = 'bg-secondary';
        if (data.sentiment === 'Positive') {
            badgeClass = 'bg-success';
        } else if (data.sentiment === 'Negative') {
            badgeClass = 'bg-danger';
        }
        
        resultHtml += `<span class="badge ${badgeClass} mb-3">${data.sentiment}</span>`;
        
        if (data.message) {
            resultHtml += `<p><small>${data.message}</small></p>`;
        }
        
        container.innerHTML = resultHtml;
        container.className = 'result mt-4 p-4 border rounded';
        
        // Add tilt effect to the result
        if (typeof VanillaTilt !== 'undefined' && container.offsetWidth < CONFIG.TILT.MAX_WIDTH) {
            VanillaTilt.init(container, CONFIG.TILT.SETTINGS);
        }
        
        // Add fade-in animation
        DOM.animate(container, `fadeInUp ${CONFIG.ANIMATION.FADE_DURATION / 1000}s forwards`);
    }

    /**
     * Sets up AJAX handling for share/unshare buttons.
     */
    function setupAjaxToggleShare() {
        // Add a common class to all share/unshare forms
        const shareForms = DOM.getAll(CONFIG.SELECTORS.shareForms);

        shareForms.forEach(form => {
            form.addEventListener('submit', async function(event) {
                event.preventDefault();
                log('Intercepting share toggle form submission for AJAX.');

                const button = form.querySelector('button[type="submit"]');
                const resultId = form.action.split('/').pop();
                const sharedStatusCell = form.closest('tr').querySelector('.shared-status-cell');

                // Disable button temporarily
                button.disabled = true;
                const originalButtonText = button.textContent;
                button.textContent = 'Updating...';
                
                // Add pulsing animation to indicate processing
                DOM.addClass(button, 'pulse-animation');

                try {
                    const response = await fetch(form.action, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();
                    
                    // Validate response data
                    if (data === null || typeof data.shared !== 'boolean') {
                        throw new Error('Invalid response from server.');
                    }

                    // Update button text and style with transition
                    button.style.transition = 'all 0.3s ease';
                    button.textContent = data.shared ? 'Unshare' : 'Share';
                    DOM.removeClass(button, data.shared ? 'btn-info' : 'btn-warning');
                    DOM.addClass(button, data.shared ? 'btn-warning' : 'btn-info');

                    // Update shared status text with a highlight effect
                    if (sharedStatusCell) {
                        sharedStatusCell.textContent = data.shared ? 'Yes' : 'No';
                        DOM.animate(sharedStatusCell, 'highlight 1.5s');
                    }

                    // Show success message with toast notification
                    showToastNotification(data.message || 'Share status updated.', 'success');

                } catch (error) {
                    ErrorHandler.handle(error, 'Failed to update share status. Please try again.');
                    button.textContent = originalButtonText;
                } finally {
                    button.disabled = false;
                    DOM.removeClass(button, 'pulse-animation');
                }
            });
        });
    }

    /**
     * Displays a toast notification.
     * @param {string} message - The message to display
     * @param {string} type - The type of notification ('success', 'error', 'info')
     */
    function showToastNotification(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = DOM.get('#toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create a unique ID for this toast
        const toastId = 'toast-' + Date.now();
        
        // Determine toast class based on type
        let bgClass = 'bg-info';
        if (type === 'success') bgClass = 'bg-success';
        if (type === 'error') bgClass = 'bg-danger';
        
        // Create toast HTML
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center ${bgClass} text-white border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        // Add toast to container
        toastContainer.innerHTML += toastHtml;
        
        // Initialize and show the toast
        const toastElement = DOM.get(`#${toastId}`);
        const toast = new bootstrap.Toast(toastElement, {
            animation: true,
            autohide: true,
            delay: CONFIG.ANIMATION.TOAST_DELAY
        });
        toast.show();
        
        // Remove toast from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    }

    /**
     * Main initialization function
     */
    function init() {
        // Initialize components, event listeners, and charts
        initializeBootstrapComponents();
        initializeParticleEffects();
        initialize3DTiltEffects();
        initializeTextAnimations();
        renderSentimentChart();
        setupAjaxFormSubmissions();
        setupAjaxToggleShare();
        initializeScrollEffects();

        log('Sentiment Analyzer custom script loaded and initialized.');
    }

    // Initialize when the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', init);
})();