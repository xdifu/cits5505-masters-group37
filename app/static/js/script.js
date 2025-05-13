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
            threeJsCanvas: '#threejs-canvas', // ADDED Three.js canvas selector
            headings: {
                animated: '.animated-heading',
                subAnimated: '.animated-subheading'
            }
        },
        ANIMATION: {
            TYPING_SPEED: 100,
            TOAST_DELAY: 3000,
            FADE_DURATION: 500,
            HIGHLIGHT_DURATION: 1500, // Added for highlight animation duration
            BUTTON_TRANSITION_DURATION: '0.3s' // Added for button transition duration
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
         * Create a new element
         * @param {string} tagName - The tag name of the element to create
         * @returns {HTMLElement} - The newly created element
         */
        create: (tagName) => document.createElement(tagName),
        
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
         * Set animation on element by directly manipulating the style.animation property.
         * Prefer using CSS classes for animations where possible.
         * This helper is useful when animation parameters (like duration, delay)
         * are highly dynamic and tied to a CSS-defined @keyframes name.
         * @param {HTMLElement} element - Target element
         * @param {string} animation - Animation string (e.g., "animationName 1s forwards")
         */
        animate: (element, animation) => {
            if (element) element.style.animation = animation;
        },
        
        /**
         * Toggles a class on the element, adding it if not present, removing it if it is.
         * @param {HTMLElement} element - Target element
         * @param {string} className - Class to toggle
         */
        toggleClass: (element, className) => {
            if (element) element.classList.toggle(className);
        },
        
        /**
         * Adds an event listener to an element
         * @param {HTMLElement} element - Target element
         * @param {string} eventType - Type of the event (e.g., 'click')
         * @param {Function} handler - Event handler function
         */
        on: (element, eventType, handler) => {
            if (element) element.addEventListener(eventType, handler);
        },
        
        /**
         * Executes a function when the DOM is fully loaded
         * @param {Function} handler - The function to execute
         */
        ready: (handler) => document.addEventListener('DOMContentLoaded', handler)
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
     * Initializes the Three.js dynamic background.
     */
    function initThreeJSBackground() {
        const canvas = DOM.get(CONFIG.SELECTORS.threeJsCanvas);
        if (!canvas || typeof THREE === 'undefined') {
            log('Three.js canvas not found or THREE library not loaded.');
            return;
        }

        const scene = new THREE.Scene();
        // Cyberpunk background color
        scene.background = new THREE.Color(0x000000); // Black or very dark (e.g., 0x030508)

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000); // Adjusted FOV for a wider view if needed
        camera.position.z = 300; // Adjust Z based on particle spread and desired perspective

        const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Particles
        const particlesGeometry = new THREE.BufferGeometry();
        const particlesCount = 15000; // Adjust count for desired density
        const posArray = new Float32Array(particlesCount * 3);
        const colorsArray = new Float32Array(particlesCount * 3);
        const sizesArray = new Float32Array(particlesCount);
        const velocityArray = new Float32Array(particlesCount); // For individual particle speeds

        // Cyberpunk color palette
        const cyberpunkColors = [
            new THREE.Color(0xff00ff), // Magenta/Pink
            new THREE.Color(0x00ffff), // Cyan
            new THREE.Color(0x00ff00), // Bright Green
            new THREE.Color(0x6600ff), // Electric Purple
            new THREE.Color(0xff3399)  // Hot Pink
        ];

        const spreadWidth = window.innerWidth * 1.5; // Spread particles wider than screen for edges
        const spreadHeight = window.innerHeight * 1.5;

        for (let i = 0; i < particlesCount; i++) {
            const i3 = i * 3;
            // Initial positions - spread out, some starting above the viewport
            posArray[i3]     = (Math.random() - 0.5) * spreadWidth;  // x
            posArray[i3 + 1] = (Math.random() - 0.5) * spreadHeight + spreadHeight / 4; // y, start some above
            posArray[i3 + 2] = (Math.random() - 0.5) * 500;         // z, some depth

            const color = cyberpunkColors[Math.floor(Math.random() * cyberpunkColors.length)];
            colorsArray[i3]     = color.r;
            colorsArray[i3 + 1] = color.g;
            colorsArray[i3 + 2] = color.b;

            sizesArray[i] = Math.random() * 1.5 + 0.5; // Smaller, sharper points: 0.5 to 2.0
            velocityArray[i] = Math.random() * 1.0 + 0.5; // Random speed for each particle (0.5 to 1.5)
        }

        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colorsArray, 3));
        particlesGeometry.setAttribute('size', new THREE.BufferAttribute(sizesArray, 1));
        // Store velocities as a custom attribute if needed for more complex shader logic,
        // or manage them in JS array as done with velocityArray.

        const particlesMaterial = new THREE.PointsMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            sizeAttenuation: true
        });
        
        const particleMesh = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particleMesh);

        let mouseX = 0, mouseY = 0;
        const windowHalfX = window.innerWidth / 2;
        const windowHalfY = window.innerHeight / 2;

        document.addEventListener('mousemove', (event) => {
            mouseX = (event.clientX - windowHalfX);
            mouseY = (event.clientY - windowHalfY);
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            // Update spreadWidth/Height if they are dependent on window size and particles are regenerated
        });

        const clock = new THREE.Clock();
        const fallBoundary = -window.innerHeight / 1.5; // When particles reset (adjust based on camera Z and FOV)
        const resetBoundary = window.innerHeight / 1.5;

        function animate() {
            requestAnimationFrame(animate);

            const elapsedTime = clock.getElapsedTime();
            const positions = particlesGeometry.attributes.position.array;

            for (let i = 0; i < particlesCount; i++) {
                const i3 = i * 3;
                positions[i3 + 1] -= velocityArray[i]; // Move particle down

                // If particle falls below boundary, reset it to the top with a new random X and Z
                if (positions[i3 + 1] < fallBoundary) {
                    positions[i3 + 1] = resetBoundary + Math.random() * 50; // Reset to top, slightly randomized
                    positions[i3]     = (Math.random() - 0.5) * spreadWidth; // New random X
                    // positions[i3 + 2] = (Math.random() - 0.5) * 500; // Optionally, new random Z
                    velocityArray[i] = Math.random() * 1.0 + 0.5; // Optionally, new random speed
                }
            }
            particlesGeometry.attributes.position.needsUpdate = true;

            // Subtle camera movement based on mouse
            camera.position.x += (mouseX * 0.0005 - camera.position.x) * 0.02;
            camera.position.y += (-mouseY * 0.0005 - camera.position.y) * 0.02;
            camera.lookAt(scene.position);

            renderer.render(scene, camera);
        }

        animate();
        log('Three.js Cyberpunk background initialized.');
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
        DOM.getAll(CONFIG.SELECTORS.headings.animated).forEach(heading => {
            if (!heading.classList.contains('cyberpunk-title')) {
                DOM.addClass(heading, 'cyberpunk-title');
                heading.setAttribute('data-text', heading.textContent);
            }
        });
        
        // Add typing animation to secondary headings
        DOM.getAll(CONFIG.SELECTORS.headings.subAnimated).forEach(heading => {
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
                DOM.show(loadingIndicator);
                resultDisplay.innerHTML = '';

                try {
                    const formData = new FormData(form);

                    // ← REMOVE these lines if your input isn't named "text"
                    // const textInput = formData.get('text');
                    // if (!textInput || textInput.trim().length < 10) {
                    //   throw new Error('Please enter at least 10 characters for analysis.');
                    // }

                    const response = await fetch(form.action, {
                        method: 'POST',
                        body: formData,
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    });
                    DOM.hide(loadingIndicator);

                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const data = await response.json();

                    displayAnalysisResult(data, resultDisplay);
                } catch (error) {
                    ErrorHandler.handle(error, 'Analysis failed. Please try again.');
                    resultDisplay.innerHTML =
                      `<div class="alert alert-danger">Analysis failed. Please try again.</div>`;
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
        // Fallback to 'N/A' if sentiment is not directly available
        resultHtml += `<p class="result-sentiment"><strong>${data.sentiment || 'N/A'}</strong></p>`;
        
        // Add badge based on sentiment
        let badgeClass = 'bg-secondary'; // Default badge class
        let sentimentText = data.sentiment || 'Neutral'; // Default sentiment text for badge

        if (data.sentiment === 'Positive') {
            badgeClass = 'bg-success';
        } else if (data.sentiment === 'Negative') {
            badgeClass = 'bg-danger';
        }
        // If data.sentiment was undefined, sentimentText is 'Neutral'. Otherwise, it's the actual sentiment.
        resultHtml += `<span class="badge ${badgeClass} mb-3">${sentimentText}</span>`;
        
        if (data.message) {
            resultHtml += `<p><small>${data.message}</small></p>`;
        }
        
        container.innerHTML = resultHtml;
        container.className = 'result mt-4 p-4 border rounded'; // Base classes
        
        // Add tilt effect to the result
        if (typeof VanillaTilt !== 'undefined' && container.offsetWidth < CONFIG.TILT.MAX_WIDTH) {
            VanillaTilt.init(container, CONFIG.TILT.SETTINGS);
        }
        
        // Add fade-in animation using a CSS class.
        DOM.addClass(container, 'animate-fadeInUp');
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
                // const resultId = form.action.split('/').pop(); // Not used in this snippet
                const sharedStatusCell = form.closest('tr').querySelector('.shared-status-cell');

                // Disable button temporarily
                button.disabled = true;
                const originalButtonText = button.textContent;
                button.textContent = 'Updating...';
                
                // Add pulsing animation to indicate processing.
                // Ensure 'pulse-animation' class and its @keyframes 'pulse' are defined in CSS.
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
                    button.style.transition = `all ${CONFIG.ANIMATION.BUTTON_TRANSITION_DURATION} ease`; // Use constant
                    button.textContent = data.shared ? 'Unshare' : 'Share';
                    DOM.removeClass(button, data.shared ? 'btn-info' : 'btn-warning');
                    DOM.addClass(button, data.shared ? 'btn-warning' : 'btn-info');

                    // Update shared status text with a highlight effect using a CSS class.
                    // Ensure 'animate-highlight' class and its @keyframes 'highlight' are defined in CSS.
                    if (sharedStatusCell) {
                        sharedStatusCell.textContent = data.shared ? 'Yes' : 'No';
                        DOM.addClass(sharedStatusCell, 'animate-highlight');
                        // Remove the class after animation to allow re-triggering or prevent style conflicts
                        setTimeout(() => {
                            DOM.removeClass(sharedStatusCell, 'animate-highlight');
                        }, CONFIG.ANIMATION.HIGHLIGHT_DURATION); // Use constant
                    }

                    // Show success message with toast notification
                    showToastNotification(data.message || 'Share status updated.', 'success');

                } catch (error) {
                    ErrorHandler.handle(error, 'Failed to update share status. Please try again.');
                    button.textContent = originalButtonText; // Restore original button text on error
                } finally {
                    button.disabled = false;
                    DOM.removeClass(button, 'pulse-animation'); // Remove pulse animation
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
        
        // Create a new div element for the toast
        const toastElementDiv = document.createElement('div');
        toastElementDiv.id = toastId;
        toastElementDiv.className = `toast align-items-center ${bgClass} text-white border-0`;
        toastElementDiv.setAttribute('role', 'alert');
        toastElementDiv.setAttribute('aria-live', 'assertive');
        toastElementDiv.setAttribute('aria-atomic', 'true');
        
        // Set inner HTML of the new toast element
        toastElementDiv.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Append the new toast element to the container instead of using innerHTML +=
        toastContainer.appendChild(toastElementDiv);
        
        // Initialize and show the toast using the newly created element
        const toast = new bootstrap.Toast(toastElementDiv, {
            animation: true,
            autohide: true,
            delay: CONFIG.ANIMATION.TOAST_DELAY
        });
        toast.show();
        
        // Remove toast from DOM after it's hidden
        toastElementDiv.addEventListener('hidden.bs.toast', function() {
            toastElementDiv.remove();
        });
    }

    /**
     * Main initialization function
     */
    function init() {
        // Initialize components, event listeners, and charts
        initializeBootstrapComponents();
        initThreeJSBackground(); // Call to Three.js background initialization
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