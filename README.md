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
*   **Database Migrations:** Evolve the database schema safely with Flask-Migrate.

## Technology Stack

*   **Backend:** Python 3, Flask
*   **Database:** SQLite with Flask-SQLAlchemy (ORM)
*   **Authentication:** Flask-Login
*   **Forms:** Flask-WTF (with CSRF protection)
*   **Frontend:** HTML5, Bootstrap 5, CSS3, JavaScript (Vanilla)
*   **Charting:** Chart.js
*   **API Integration:** OpenAI Python Client Library (`openai`)
*   **Environment Variables:** `python-dotenv`
*   **Database Migrations:** Flask-Migrate (with Alembic)
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
│   ├── models.py         # SQLAlchemy database models (User, AnalysisReport, NewsItem)
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
├── clear_database.py     # DEV-ONLY: Script to clear data from tables
├── reset_database.py     # DEV-ONLY: Script to drop and recreate all tables
└── README.md             # This file
```

## Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   `virtualenv` (Recommended for isolating project dependencies)
*   An OpenAI API Key

## Setup and Installation
1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/xdifu/cits5505-masters-group37.git
    cd cits5505-masters-group37
    ```

2.  **Create and Activate a Virtual Environment:**
    *   **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
        
        **Windows**

        ```bash
        # Create the venv (once per project)
        python -m venv venv

        # Option A: using cmd.exe (no policy change needed)
        .\venv\Scripts\activate.bat
         ```

        ````powershell
        # Create the venv (once per project)
        python -m venv venv

        # Option B: using PowerShell (may need to relax execution policy)
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
        .\venv\Scripts\Activate.ps1
        ````

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
        FLASK_APP=run.py # Essential for Flask CLI (flask db, flask run)
        FLASK_ENV=development # Set to 'production' for production deployments
        SECRET_KEY='a-very-strong-random-secret-key-please-change' # Replace with a real secret key
        OPENAI_API_KEY='your-openai-api-key-here'
        # For development, DEV_DATABASE_URL in config.py defaults to 'sqlite:///instance/app-dev.db'
        # For production, DATABASE_URL in config.py defaults to 'sqlite:///instance/app.db'
        # You can override these here if needed, e.g.:
        # DEV_DATABASE_URL='postgresql://user:pass@host:port/dbname'
        # DATABASE_URL='postgresql://user:pass@host:port/dbname_prod'
        ```
        *   **`FLASK_APP`**: Tells the `flask` command how to load your application.
        *   **`FLASK_ENV`**: Sets the environment (e.g., `development`, `production`). Influences which config is loaded.
        *   **`SECRET_KEY`**: Used by Flask for session security and CSRF protection.
        *   **`OPENAI_API_KEY`**: Your API key from OpenAI.

5.  **Initialize/Upgrade the Database:**
    This step ensures your database schema is up-to-date with the models.
    ```bash
    # If this is the very first time setting up the project, initialize the migration environment:
    # flask db init 
    # (This creates the migrations/ folder. Commit this folder to your repository.)

    # Generate a new migration if you've made changes to app/models.py:
    # flask db migrate -m "Brief description of model changes"
    # (Review the generated script in migrations/versions/)

    # Apply migrations to the database:
    flask db upgrade
    ```
    *Note: Ensure `FLASK_APP=run.py` is set in your `.env` file or exported in your shell for `flask db` commands to work correctly.*

## Running the Application

1.  **Ensure your virtual environment is activated.**
2.  **Ensure your database is migrated to the latest version (see `flask db upgrade` above).**
3.  **Start the Flask Development Server:**
    ```bash
    flask run
    ```
    *   The application will typically be available at `http://127.0.0.1:5000/` or `http://localhost:5000/`.
    *   The server runs in debug mode by default (as configured in `run.py`), providing auto-reloading on code changes and detailed error pages. **Do not use debug mode in production.**

## Running Tests

### Unit Tests (`pytest`)

1.  **Ensure your virtual environment is activated and dependencies are installed.**
2.  **The test environment uses an in-memory SQLite database by default.** Migrations should be applied during test setup (see `tests/conftest.py` if customization is needed).
3.  **Run pytest from the project root directory:**
    ```bash
    pytest
    ```

### Unit Tests (unittest)

To run all unit tests (including user model, form validation, analysis API, results page, and visualization page), use the following command:

```bash
c
```

This will automatically discover and run all files in the `test/unit_tests` folder that follow the `test_*.py` naming convention.

### Functional Tests (Selenium)

Automated browser-based tests are implemented using **Selenium**.

Each test case uses `setUp()` and `tearDown()` to automatically start and stop the Flask development server, ensuring an isolated environment for each run.

#### Prerequisites:

- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- Ensure `chromedriver` is installed and available in your system path.

#### Run All Selenium Tests:

```bash
python -m unittest discover -s test/selenium_tests -p "test_*.py"
```

If port `5000` is already in use, please close any previous Flask instance or restart your system. The test suite will launch Flask on port 5000 and terminate it after each test.

## Usage

1.  **Navigate** to the application URL (e.g., `http://localhost:5000/`).
2.  **Register** for a new account or **Login** if you already have one.
3.  Go to the **"Analyze Text"** page.
4.  **Paste** the news text or any text snippet into the text area.
5.  Click **"Analyze Sentiment"**. The result (Positive, Neutral, or Negative) will be displayed, and the analysis will be saved to your history.
6.  Go to the **"My Results"** page to view your past analyses, see the sentiment distribution chart, and optionally **Share/Unshare** specific results.
7.  Go to the **"Shared Results"** page to view analyses shared publicly by other users.
8.  **Logout** when finished.

## Database Migrations (Flask-Migrate)

This project uses [Flask-Migrate](https://flask-migrate.readthedocs.io/) (which builds on [Alembic](https://alembic.sqlalchemy.org/)) to handle database schema migrations. This is the **recommended way** to evolve your database structure over time, especially in production, as it helps preserve existing data.

### Workflow

1.  **Modify Models:** Make changes to your SQLAlchemy models in `app/models.py` (e.g., add a table, add/remove a column, change a data type).
2.  **Generate Migration Script:**
    ```bash
    flask db migrate -m "A short, descriptive message of the changes"
    ```
    This command compares your models to the current database schema (as tracked by previous migrations) and generates a new script in the `migrations/versions/` directory. **Make this message meaningful**, as it helps you and your team understand the purpose of each migration when looking at the history.
3.  **Review Script:** **Always open and review the generated migration script.** Alembic does its best, but for complex changes (e.g., data transformations, renaming columns that SQLite doesn't natively support well), you might need to manually adjust the script. See "Important Notes" below.
4.  **Apply Migration:**
    ```bash
    flask db upgrade
    ```
    This applies the latest (or all pending) migration scripts to your database.
5.  **Commit Changes:** Commit both your model changes (`app/models.py`) and the new migration script (`migrations/versions/your_new_script.py`) to version control. This ensures that other developers and your deployment process can apply the same schema changes.

### Common Migration Commands

Ensure `FLASK_APP=run.py` is set (e.g., in your `.env` file or exported in your shell).

*   **Initialize Migration Environment (run once per project):**
    ```bash
    flask db init
    ```
    Creates `migrations/` directory and configuration. Commit this.

*   **Generate a New Migration Script:**
    ```bash
    flask db migrate -m "description of changes"
    ```
    Remember to provide a clear and descriptive message.

*   **Apply Migrations to Database (Upgrade):**
    ```bash
    flask db upgrade
    ```
    Applies all pending migrations to bring the database to the latest revision. To upgrade to a specific version: `flask db upgrade <revision_id>`

*   **Revert Last Migration (Downgrade):**
    ```bash
    flask db downgrade
    ```
    Reverts the single most recent migration. To downgrade to a specific version (which must be an earlier revision): `flask db downgrade <revision_id>`

*   **View Migration History:**
    ```bash
    flask db history
    ```
    Shows a list of migrations, their IDs, and messages.

*   **View Current Database Revision:**
    ```bash
    flask db current
    ```
    Shows the revision ID currently applied to the database.

*   **Stamp Database with a Revision (Advanced):**
    If the database schema already matches a certain migration (e.g., after a manual setup or restore) but Alembic doesn't know it:
    ```bash
    flask db stamp head  # Marks current schema as up-to-date with the latest migration script
    flask db stamp <revision_id> # Marks current schema as matching a specific revision
    ```
    Use with caution, as this doesn't run any migration code.

### Important Notes for Migrations:

*   **Review Generated Scripts:** This is crucial for preventing unintended changes or data loss. Do not blindly trust auto-generated scripts for complex operations.
*   **Handling Incorrectly Generated Migrations:** If `flask db migrate` generates a script that isn't what you intended (e.g., due to a mistake in model changes or an Alembic misinterpretation), **do not apply it with `flask db upgrade`**. You can simply delete the incorrect migration Python file from the `migrations/versions/` directory, correct your models or the underlying issue, and then re-run `flask db migrate -m "..."` to generate a new, correct script.
*   **Backup Production Data:** Always back up your production database before applying any migrations.
*   **SQLite Limitations:** Alembic's "batch mode" (enabled by default for SQLite in Flask-Migrate) helps work around some SQLite limitations regarding `ALTER TABLE` operations (like dropping columns or altering constraints). However, complex changes like renaming tables/columns or certain type changes with constraints might still require manual adjustments in the migration script or a multi-step migration process.
*   **Development vs. Production:** While `flask db upgrade` is used in all environments to apply migrations, the generation of migrations (`flask db migrate`) is typically a development task. Migration scripts are then committed to version control and applied to staging/production environments.
*   **Migrations in Tests:** Our testing setup (configured in `tests/conftest.py`) automatically runs `flask db upgrade` before tests. This ensures the test database schema is always consistent with the latest migrations, providing a reliable testing environment.
*   **Team Collaboration:** When working in a team, always pull the latest changes (including any new migration files from others) before creating your own migrations to avoid conflicts. If conflicts do occur (e.g., two developers create migrations from the same base revision), they need to be resolved carefully, sometimes involving `flask db merge` or by re-generating one of the migrations on top of the other.

## Development-Only Database Scripts (Use with Caution)

The following scripts are provided for **development convenience only**. They are **destructive** and should **NOT** be used on a production database or if you need to preserve data. For schema evolution, always use the Flask-Migrate workflow described above.

*   **`clear_database.py`**:
    *   **Action:** Deletes all data from all tables but preserves the table structure.
    *   **Use Case:** Quickly empty the database during development without affecting the schema.
    *   **Command:** `python clear_database.py`

*   **`reset_database.py`**:
    *   **Action:** Drops all tables and then recreates them based on the current models (effectively `db.drop_all()` then `db.create_all()`). **This bypasses the migration history.**
    *   **Use Case:** Drastic reset for development if the database or migration state becomes corrupted and you want a completely fresh start based on current models.
    *   **Command:** `python reset_database.py`

**Warning:** Using `reset_database.py` means your database will no longer be in sync with Alembic's migration history. You might need to re-stamp the database (`flask db stamp head`) or re-initialize migrations if you intend to use Flask-Migrate afterwards.

## Team Members

| UWA ID      | Name             | GitHub Username |
| :---------- | :--------------- | :-------------- |
| `24473616`  | `Difu Xiao`      | `xdifu`         |
| `24212167`  | `Nandana Shine`  | ` Nandana098 `  |
| `24134929`  | `Tobin Yao    `  | ` tobinyao `    |
| `24117922`  | `Zhengxu Jin  `  | ` joshjin11 `   |

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (if a LICENSE file exists, otherwise state the license directly).