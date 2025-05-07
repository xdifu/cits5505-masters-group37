# News Sentiment Analysis Web Application

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask Version](https://img.shields.io/badge/flask-3.1-brightgreen.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Assuming MIT License -->

A full-featured Flask web application designed for analyzing the sentiment of news text using the OpenAI gpt-4.1-nano API. Users can register, submit text for analysis, view their history, and share results with others.

## Overview

This application provides a platform for users to perform sentiment analysis on provided text snippets, typically news articles. It leverages the power of OpenAI's gpt-4.1-nano model to classify text as Positive, Neutral, or Negative. The system includes user authentication, data persistence, result visualization, and sharing capabilities, built with a standard Flask project structure.

## Features

*   **User Authentication:** Secure user registration, login, logout, and session management via Flask-Login. Passwords are securely stored using salted hashes.
*   **Sentiment Analysis:** Users can submit text through a dedicated form. The backend interacts with the OpenAI API (gpt-4.1-nano) to obtain a sentiment classification.
*   **Database Storage:** Analysis results (original text, sentiment, timestamp, user ID, shared status) are stored persistently in an SQLite database using SQLAlchemy ORM.
*   **Result Visualization:** Users can view their personal history of analyzed texts. A pie chart visualizes the distribution of sentiments (Positive, Neutral, Negative) for their results.
*   **Result Sharing:** Users have the option to mark their individual analysis results as "shared".
*   **Public Shared View:** A dedicated page allows all users (including anonymous visitors) to browse results that have been marked as "shared" by others.
*   **CSRF Protection:** All forms are protected against Cross-Site Request Forgery attacks using Flask-WTF.
*   **Secure API Key Handling:** OpenAI API keys are managed securely using environment variables loaded via `python-dotenv`.

## Technology Stack

*   **Backend:** Python 3, Flask
*   **Database:** SQLite with Flask-SQLAlchemy (ORM)
*   **Authentication:** Flask-Login
*   **Forms:** Flask-WTF (with CSRF protection)
*   **Frontend:** HTML5, Bootstrap 5, CSS3, JavaScript (Vanilla)
*   **Charting:** Chart.js
*   **API Integration:** OpenAI Python Client Library (`openai`)
*   **Environment Variables:** `python-dotenv`
*   **Testing:**
    *   Unit Testing: `pytest`
    *   Functional Testing: `selenium`
*   **Development Server:** Werkzeug (via Flask CLI)

## Project Structure

```
news-sentiment-analyzer/
├── instance/             # SQLite database and instance-specific files (created automatically)
│   └── app.db
├── app/                  # Main application package
│   ├── __init__.py       # Application factory, initializes extensions
│   ├── models.py         # SQLAlchemy database models (User, Result)
│   ├── forms.py          # WTForms definitions (Login, Register, Analysis)
│   ├── openai_api.py     # Logic for interacting with OpenAI API
│   ├── auth/             # Authentication blueprint
│   │   ├── __init__.py
│   │   └── routes.py     # Login, logout, register routes
│   ├── main/             # Core application blueprint
│   │   ├── __init__.py
│   │   └── routes.py     # Index, analyze, results, shared routes
│   ├── static/           # Static files (CSS, JavaScript, Images)
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── script.js # Includes Chart.js integration
│   └── templates/        # Jinja2 templates
│       ├── auth/         # Auth-related templates
│       │   ├── login.html
│       │   └── register.html
│       ├── base.html         # Base layout template
│       ├── index.html        # Home page
│       ├── analyze.html      # Text submission form page
│       ├── results.html      # User's results history and chart
│       ├── shared_results.html # Public shared results page
│       └── bootstrap_wtf.html # Macro for rendering Bootstrap forms
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_basic.py     # Example unit tests
│   └── test_selenium.py  # Example functional tests
├── venv/                 # Virtual environment directory (excluded by .gitignore)
├── .env                  # Environment variables (API Key, Secret Key - excluded)
├── .env.example          # Example environment file template
├── .gitignore            # Specifies intentionally untracked files
├── requirements.txt      # Python package dependencies
├── run.py                # Application entry point script
└── README.md             # This file
```

## Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   `virtualenv` (Recommended for isolating project dependencies)
*   An OpenAI API Key

## Setup and Installation
1.  **Clone the Repository and Checkout Branch:**
   ```bash
   # Clone the repository
   git clone https://github.com/xdifu/cits5505-masters-group37.git
   cd cits5505-masters-group37

   # Check out the specific feature branch
   git checkout feature/xdifu/news-sentiment-analyzer

   # Navigate into the project directory
   cd news-sentiment-analyzer
   ```

2.  **Create and Activate a Virtual Environment:**
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and add your credentials:
        ```dotenv
        # .env
        SECRET_KEY='a-very-strong-random-secret-key-please-change' # Replace with a real secret key
        OPENAI_API_KEY='your-openai-api-key-here'
        # DATABASE_URL='sqlite:///instance/app.db' # Optional: Defaults to this if not set
        ```
        *   **`SECRET_KEY`**: Used by Flask for session security and CSRF protection. Generate a strong random key.
        *   **`OPENAI_API_KEY`**: Your API key obtained from OpenAI.

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Start the Flask Development Server:**
    ```bash
    flask run
    ```
    *   The application will typically be available at `http://127.0.0.1:5000/` or `http://localhost:5000/`.
    *   The server runs in debug mode by default (as configured in `run.py`), providing auto-reloading on code changes and detailed error pages. **Do not use debug mode in production.**

## Running Tests

### Unit Tests (`pytest`)

1.  **Ensure your virtual environment is activated and dependencies are installed.**
2.  **Run pytest from the project root directory (`news-sentiment-analyzer/`):**
    ```bash
    pytest
    ```
    *   Pytest will automatically discover and run tests in the `tests/` directory.

### Functional Tests (`selenium`)

**Prerequisites:**

*   **WebDriver:** You need the appropriate WebDriver for the browser you intend to test with (e.g., `chromedriver` for Chrome, `geckodriver` for Firefox). Ensure the WebDriver executable is in your system's PATH or specify its location in the test configuration.
*   **Running Application:** The Flask application must be running in a separate terminal instance before executing Selenium tests.

**Execution:**

1.  **Start the Flask application:**
    ```bash
    flask run
    ```
2.  **Open a *new* terminal window/tab.**
3.  **Activate the virtual environment in the new terminal:**
    *   Linux/macOS: `source venv/bin/activate`
    *   Windows: `.\venv\Scripts\activate`
4.  **Run the Selenium tests using pytest:**
    ```bash
    pytest tests/test_selenium.py
    ```
    *(Note: Depending on test configuration, you might run all tests with `pytest` and it will include Selenium tests if properly set up, but running them specifically can be useful.)*

## Usage

1.  **Navigate** to the application URL (e.g., `http://localhost:5000/`).
2.  **Register** for a new account or **Login** if you already have one.
3.  Go to the **"Analyze Text"** page.
4.  **Paste** the news text or any text snippet into the text area.
5.  Click **"Analyze Sentiment"**. The result (Positive, Neutral, or Negative) will be displayed, and the analysis will be saved to your history.
6.  Go to the **"My Results"** page to view your past analyses, see the sentiment distribution chart, and optionally **Share/Unshare** specific results.
7.  Go to the **"Shared Results"** page to view analyses shared publicly by other users.
8.  **Logout** when finished.

## Team Members

| UWA ID      | Name             | GitHub Username |
| :---------- | :--------------- | :-------------- |
| `24473616`  | `Difu Xiao`      | `xdifu`         |
| `24212167`  | `Nandana Shine`  | ` Nandana098 `  |
| `24134929`  | `Tobin Yao    `  | ` tobinyao `    |
| `24117922`  | `Zhengxu Jin  `  | ` joshjin11 `   |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (if a LICENSE file exists, otherwise state the license directly).