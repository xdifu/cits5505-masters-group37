// Custom JavaScript for the News Sentiment Analyzer application.
// Includes chart rendering for results visualization, particle effects, 3D tilt effects, and AJAX enhancements.

/**
 * Executes when the DOM is fully loaded.
 * Initializes components, event listeners, and charts.
 */
document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap components (e.g., tooltips, popovers)
    initializeBootstrapComponents();

    // Initialize advanced visual effects
    initializeParticleEffects();
    initialize3DTiltEffects();
    initializeTextAnimations();

    // Render the sentiment analysis chart on the results page if the canvas exists
    renderSentimentChart();

    // Add event listeners for AJAX interactions
    setupAjaxFormSubmissions();
    setupAjaxToggleShare();
    
    // Add scroll effects for navbar
    initializeScrollEffects();

    console.log('Sentiment Analyzer custom script loaded and initialized.');

}); // End of DOMContentLoaded

/**
 * Initializes scroll-based effects for elements like the navbar
 */
function initializeScrollEffects() {
    // Variables to track scroll state
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    const scrollThreshold = 50; // Threshold in pixels
    
    // Add event listener for scroll
    window.addEventListener('scroll', function() {
        let currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        // Check if we've scrolled past the threshold
        if (currentScroll > scrollThreshold) {
            // Scrolling down
            navbar.classList.add('navbar-scrolled');
        } else {
            // At top or scrolling up to top
            navbar.classList.remove('navbar-scrolled');
        }
        
        // Update last scroll position
        lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
    }, false);
}

/**
 * Initializes Bootstrap components that require JavaScript activation.
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Highlight the active navigation link based on current URL path
    highlightCurrentNavLink();
    
    console.log('Bootstrap components initialized.');
}

/**
 * Highlights the current active navigation link based on URL path
 */
function highlightCurrentNavLink() {
    // Get current path from window location
    const currentPath = window.location.pathname;
    
    // Find all navigation links
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    // Loop through each link
    navLinks.forEach(link => {
        // Get the href attribute
        const href = link.getAttribute('href');
        
        // Remove any previous active class
        link.classList.remove('active');
        
        // Check if this link's href matches the current path
        if (href === currentPath) {
            link.classList.add('active');
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
        particlesJS('particles-js', {
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
        });
        console.log('Particles.js initialized');
    } else {
        // Fallback: Create particles container if it doesn't exist
        if (!document.getElementById('particles-js')) {
            const particlesContainer = document.createElement('div');
            particlesContainer.id = 'particles-js';
            document.body.prepend(particlesContainer);
            
            // Create simple custom particle effect
            createSimpleParticleEffect(particlesContainer);
            console.log('Custom particle effect initialized');
        }
    }
}

/**
 * Creates a simple particle effect as a fallback when particles.js is not available.
 * @param {HTMLElement} container - The container element for particles
 */
function createSimpleParticleEffect(container) {
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'simple-particle';
        
        // Random positioning and properties
        const size = Math.random() * 5 + 1;
        const posX = Math.random() * 100;
        const posY = Math.random() * 100;
        const duration = Math.random() * 20 + 10;
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
    
    // Add the animation keyframes if they don't exist
    if (!document.getElementById('particle-keyframes')) {
        const style = document.createElement('style');
        style.id = 'particle-keyframes';
        style.innerHTML = `
            @keyframes floatParticle {
                0% { transform: translate(0, 0); }
                25% { transform: translate(10px, 10px); }
                50% { transform: translate(0, 20px); }
                75% { transform: translate(-10px, 10px); }
                100% { transform: translate(0, 0); }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Initializes 3D tilt effects for cards and result containers.
 * Uses vanilla-tilt.js if available, but only on narrow elements
 * to avoid excessive rotation on large panels.
 */
function initialize3DTiltEffects() {
    if (typeof VanillaTilt !== 'undefined') {
        // Find all tilt-card elements
        document.querySelectorAll('.tilt-card').forEach(el => {
            // Only initialize on elements narrower than 600px
            if (el.offsetWidth < 600) {
                VanillaTilt.init(el, {
                    max: 5,           // smaller max tilt angle
                    speed: 300,
                    glare: true,
                    'max-glare': 0.2,
                    scale: 1.02
                });
            }
        });
    } else {
        // Fallback: Apply a simple JS-driven tilt on hover for .tilt-card elements
        // that are narrower than 600px.
        document.querySelectorAll('.tilt-card').forEach(card => {
            // ADDED: Width check for the fallback mechanism
            if (card.offsetWidth < 600) {
                card.addEventListener('mousemove', function(e) {
                    const cardRect = card.getBoundingClientRect();
                    const cardCenterX = cardRect.left + cardRect.width / 2;
                    const cardCenterY = cardRect.top + cardRect.height / 2;
                    
                    const mouseX = e.clientX - cardCenterX;
                    const mouseY = e.clientY - cardCenterY;
                    
                    // Calculate the rotation values (limited to -5 to 5 degrees)
                    const rotateY = mouseX / (cardRect.width / 2) * 5;
                    const rotateX = -mouseY / (cardRect.height / 2) * 5;
                    
                    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                });
                
                card.addEventListener('mouseleave', function() {
                    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
                });
            }
        });
        console.log('Simple tilt effect initialized as fallback for narrow cards.');
    }
}

/**
 * Initializes text animations for headings and important content.
 * Adds typing effects, cyberpunk glitch effects, etc.
 */
function initializeTextAnimations() {
    // Add cyberpunk title effect
    document.querySelectorAll('h1.display-5').forEach(heading => {
        if (!heading.classList.contains('cyberpunk-title')) {
            heading.classList.add('cyberpunk-title');
            heading.setAttribute('data-text', heading.textContent);
        }
    });
    
    // Add typing animation to secondary headings
    document.querySelectorAll('h2:not(.typing-active)').forEach(heading => {
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
        }, 100);
    });
    
    console.log('Text animations initialized');
}

/**
 * Renders the sentiment distribution chart on the results page.
 * Assumes Chart.js library is loaded and data is available.
 */
function renderSentimentChart() {
    const ctx = document.getElementById('sentimentChart'); // Get the canvas element

    // Check if the canvas element exists (i.e., we are on the results page)
    // and if the chart data is provided
    if (ctx && typeof sentimentData !== 'undefined') {
        console.log('Rendering sentiment chart with data:', sentimentData);
        try {
            new Chart(ctx, {
                type: 'doughnut', // Changed from pie to doughnut for a more modern look
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
            console.error("Error rendering chart:", error);
            // Display a user-friendly message
            if (ctx.parentNode) {
                const errorMsg = document.createElement('div');
                errorMsg.className = 'alert alert-warning';
                errorMsg.textContent = 'Could not render the chart. Please try refreshing the page.';
                ctx.parentNode.appendChild(errorMsg);
            }
        }
    } else {
        if (!ctx) console.log('Sentiment chart canvas not found.');
        if (typeof sentimentData === 'undefined') console.log('Sentiment data not found for chart.');
    }
}

/**
 * Sets up AJAX submission for the main analysis form.
 */
function setupAjaxFormSubmissions() {
    const form = document.getElementById('analysis-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultDisplay = document.getElementById('ajax-result-display');
    
    if (form) {
        form.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            // Show loading indicator
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            if (resultDisplay) resultDisplay.innerHTML = ''; // Clear previous results
            
            try {
                const formData = new FormData(form);
                
                // Submit form data via AJAX
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'  // 添加这个头部以标识 AJAX 请求
                    }
                });
                
                // Hide loading indicator
                if (loadingIndicator) loadingIndicator.style.display = 'none';
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json(); // Expect JSON response from Flask

                // Display result with animation
                let resultHtml = `<h2>Analysis Result:</h2>`;
                resultHtml += `<p class="result-sentiment"><strong>${data.sentiment || 'N/A'}</strong></p>`;
                
                // Add badge based on sentiment
                if (data.sentiment === 'Positive') {
                    resultHtml += `<span class="badge bg-success mb-3">Positive</span>`;
                } else if (data.sentiment === 'Negative') {
                    resultHtml += `<span class="badge bg-danger mb-3">Negative</span>`;
                } else {
                    resultHtml += `<span class="badge bg-secondary mb-3">Neutral</span>`;
                }
                
                if (data.message) {
                    resultHtml += `<p><small>${data.message}</small></p>`;
                }
                
                resultDisplay.innerHTML = resultHtml;
                resultDisplay.className = 'result mt-4 p-4 border rounded'; // Apply styling
                
                // Add tilt effect to the result
                if (typeof VanillaTilt !== 'undefined') {
                    VanillaTilt.init(resultDisplay, {
                        max: 5,
                        speed: 400,
                        glare: true,
                        "max-glare": 0.2,
                    });
                }
                
                // Add fade-in animation
                resultDisplay.style.animation = 'fadeInUp 0.5s forwards';

            } catch (error) {
                console.error('AJAX analysis submission failed:', error);
                resultDisplay.innerHTML = `<div class="alert alert-danger">Analysis failed. Please try again. ${error.message}</div>`;
            } finally {
                loadingIndicator.style.display = 'none'; // Hide loading
            }
        });
    }
}

/**
 * Sets up AJAX handling for share/unshare buttons.
 */
function setupAjaxToggleShare() {
    // Add a common class to all share/unshare forms
    const shareForms = document.querySelectorAll('.toggle-share-form');

    shareForms.forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
            console.log('Intercepting share toggle form submission for AJAX.');

            const button = form.querySelector('button[type="submit"]');
            const resultId = form.action.split('/').pop(); // Extract result ID from action URL
            const sharedStatusCell = form.closest('tr').querySelector('.shared-status-cell');

            // Disable button temporarily
            button.disabled = true;
            const originalButtonText = button.textContent;
            button.textContent = 'Updating...';
            
            // Add pulsing animation to indicate processing
            button.classList.add('pulse-animation');

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

                const data = await response.json(); // Expect { shared: true/false, message: '...' }

                // Update button text and style with transition
                button.style.transition = 'all 0.3s ease';
                button.textContent = data.shared ? 'Unshare' : 'Share';
                button.classList.remove(data.shared ? 'btn-info' : 'btn-warning');
                button.classList.add(data.shared ? 'btn-warning' : 'btn-info');

                // Update shared status text with a highlight effect
                if (sharedStatusCell) {
                    sharedStatusCell.textContent = data.shared ? 'Yes' : 'No';
                    sharedStatusCell.style.animation = 'highlight 1.5s';
                }

                // Show success message with toast notification
                showToastNotification(data.message || 'Share status updated.', 'success');

            } catch (error) {
                console.error('AJAX share toggle failed:', error);
                button.textContent = originalButtonText; // Restore original text on error
                
                // Show error message with toast notification
                showToastNotification('Failed to update share status. Please try again.', 'error');
            } finally {
                button.disabled = false; // Re-enable button
                button.classList.remove('pulse-animation'); // Remove pulse animation
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
    let toastContainer = document.getElementById('toast-container');
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
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        animation: true,
        autohide: true,
        delay: 3000
    });
    toast.show();
    
    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

// Add this to make the toast animations available in the CSS
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.innerHTML = `
        .toast {
            transition: all 0.3s ease;
            animation: toastFadeIn 0.3s forwards;
        }
        @keyframes toastFadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes highlight {
            0%, 100% { background-color: transparent; }
            50% { background-color: rgba(0, 102, 255, 0.2); }
        }
        .pulse-animation {
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    `;
    document.head.appendChild(style);
}