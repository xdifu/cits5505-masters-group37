// Custom JavaScript for the News Sentiment Analyzer application.
// Includes chart rendering for results visualization and structure for AJAX enhancements.

/**
 * Executes when the DOM is fully loaded.
 * Initializes components, event listeners, and charts.
 */
document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap components (e.g., tooltips if used)
    initializeBootstrapComponents();

    // Render the sentiment analysis chart on the results page if the canvas exists
    renderSentimentChart();

    // Add event listeners for AJAX interactions (optional enhancements)
    setupAjaxFormSubmissions(); // Example for analysis form
    setupAjaxToggleShare();    // Example for share buttons

    console.log('Sentiment Analyzer custom script loaded and initialized.');

}); // End of DOMContentLoaded

/**
 * Initializes Bootstrap components that require JavaScript activation.
 */
function initializeBootstrapComponents() {
    // Example: Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    console.log('Bootstrap components initialized.');
}

/**
 * Renders the sentiment distribution chart on the results page.
 * Assumes Chart.js library is loaded and data is available.
 */
function renderSentimentChart() {
    const ctx = document.getElementById('sentimentChart'); // Get the canvas element

    // Check if the canvas element exists (i.e., we are on the results page)
    // and if the chart data is provided (e.g., via a global JS variable or data attribute)
    if (ctx && typeof sentimentData !== 'undefined') {
        console.log('Rendering sentiment chart with data:', sentimentData);
        try {
            new Chart(ctx, {
                type: 'pie', // Or 'bar', 'doughnut', etc.
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        label: 'Sentiment Distribution',
                        // Access data passed from Flask (e.g., sentimentData = { positive: 5, neutral: 10, negative: 2 };)
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
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'Your Sentiment Analysis Results Distribution'
                        }
                    }
                }
            });
        } catch (error) {
            console.error("Error rendering chart:", error);
            // Optionally display a user-friendly message on the page
        }
    } else {
        if (!ctx) console.log('Sentiment chart canvas not found.');
        if (typeof sentimentData === 'undefined') console.log('Sentiment data not found for chart.');
    }
}

/**
 * Sets up AJAX submission for the main analysis form (Optional Enhancement).
 */
function setupAjaxFormSubmissions() {
    // Assume the form in analyze.html has id="analysis-form"
    const analysisForm = document.getElementById('analysis-form');
    // Assume there's an element to display results/errors, e.g., id="ajax-result-display"
    const resultDisplay = document.getElementById('ajax-result-display');
    // Assume a loading indicator, e.g., id="loading-indicator"
    const loadingIndicator = document.getElementById('loading-indicator');

    if (analysisForm && resultDisplay && loadingIndicator) {
        analysisForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default synchronous submission
            console.log('Intercepting analysis form submission for AJAX.');

            loadingIndicator.style.display = 'block'; // Show loading
            resultDisplay.innerHTML = ''; // Clear previous results

            const formData = new FormData(analysisForm);
            const url = analysisForm.action; // Get URL from form's action attribute

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest' // Identify as AJAX request
                        // Include CSRF token header if not using WTForms hidden field method
                        // 'X-CSRFToken': '{{ csrf_token() }}' // This needs Flask context if added here
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json(); // Expect JSON response from Flask

                // Display result
                let resultHtml = `<h2>Analysis Result:</h2><p><strong>${data.sentiment || 'N/A'}</strong></p>`;
                if (data.message) {
                    resultHtml += `<p><small>${data.message}</small></p>`;
                }
                resultDisplay.innerHTML = resultHtml;
                resultDisplay.className = 'result mt-4 p-3 border rounded bg-light'; // Apply styling

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
 * Sets up AJAX handling for share/unshare buttons (Optional Enhancement).
 */
function setupAjaxToggleShare() {
    // Add a common class e.g., 'toggle-share-form' to all share/unshare forms in results.html
    const shareForms = document.querySelectorAll('.toggle-share-form');

    shareForms.forEach(form => {
        form.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission
            console.log('Intercepting share toggle form submission for AJAX.');

            const button = form.querySelector('button[type="submit"]');
            const resultId = form.action.split('/').pop(); // Extract result ID from action URL
            const sharedStatusCell = form.closest('tr').querySelector('.shared-status-cell'); // Add class="shared-status-cell" to the <td>

            // Disable button temporarily
            button.disabled = true;
            const originalButtonText = button.textContent;
            button.textContent = 'Updating...';

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    // Include CSRF token if needed (WTForms hidden field usually handles this)
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json(); // Expect { shared: true/false, message: '...' }

                // Update button text and style
                button.textContent = data.shared ? 'Unshare' : 'Share';
                button.classList.remove(data.shared ? 'btn-info' : 'btn-warning');
                button.classList.add(data.shared ? 'btn-warning' : 'btn-info');

                // Update shared status text
                if (sharedStatusCell) {
                    sharedStatusCell.textContent = data.shared ? 'Yes' : 'No';
                }

                // Optionally show a success message (e.g., using a temporary alert or toast)
                console.log(data.message || 'Share status updated.');


            } catch (error) {
                console.error('AJAX share toggle failed:', error);
                button.textContent = originalButtonText; // Restore original text on error
                // Optionally show an error message to the user
                alert('Failed to update share status. Please try again.');
            } finally {
                button.disabled = false; // Re-enable button
            }
        });
    });
}