# Main entry point for the Flask application.
# This script imports the Flask app instance and runs the development server.

from app import create_app

# Create the Flask app instance using the factory function
app = create_app()

if __name__ == '__main__':
    # Run the Flask development server
    # Debug mode is enabled for development, providing auto-reloading and detailed error pages.
    # Host '0.0.0.0' makes the server accessible externally (e.g., within a local network).
    # Port 5000 is the default Flask port.
    app.run(host='0.0.0.0', port=5000, debug=True)