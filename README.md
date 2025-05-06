# News Sentiment Analysis MVP

A minimal Flask application that leverages the OpenAI GPT-4.1-nano API to analyze the sentiment of news text.

## Overview

This MVP (Minimum Viable Product) demonstrates a straightforward implementation of sentiment analysis through a clean web interface. Users can input news text, and the application will classify the sentiment as Positive, Neutral, or Negative using OpenAI's language model capabilities.

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Frontend**: HTML with minimal CSS
- **API**: OpenAI GPT-4.1-nano
- **Environment Management**: python-dotenv

## Prerequisites

- Python 3.8+
- OpenAI API key

## Installation

1. **Clone the repository and checkout the `feature/project-structure-setup` branch**:
   The code for this specific version of the project is on the `feature/project-structure-setup` branch.
   You can browse this branch on GitHub at [https://github.com/xdifu/cits5505-masters-group37/tree/feature/project-structure-setup](https://github.com/xdifu/cits5505-masters-group37/tree/feature/project-structure-setup).

   To set up the project locally:
   ```bash
   # Clone the main repository
   git clone https://github.com/xdifu/cits5505-masters-group37.git
   
   # Navigate into the cloned repository directory
   cd cits5505-masters-group37
   
   # Switch to the feature branch
   git checkout feature/project-structure-setup
   ```
   *(Alternatively, you can clone the branch directly: `git clone --branch feature/project-structure-setup https://github.com/xdifu/cits5505-masters-group37.git` and then `cd cits5505-masters-group37`)*

2. **Create and activate a virtual environment** (from the `cits5505-masters-group37` directory):
   ```bash
   python -m venv mvp-env  # You can choose a different name for your environment
   
   # On Linux/macOS
   source mvp-env/bin/activate
   
   # On Windows
   mvp-env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to include your OpenAI API key:
   ```
   OPENAI_API_KEY='your-openai-api-key-here'
   ```
## Running the Application

Execute the following command from the project root:
```bash
python run.py
```

The application will be available at: `http://127.0.0.1:5000/`

## Project Structure

```
MVP/
├── app/
│   ├── __init__.py      # Flask application factory
│   ├── openai_api.py    # OpenAI API integration
│   ├── routes.py        # Flask route definitions
│   └── templates/       
│       └── index.html   # Main page template
├── .env                 # Environment variables (not tracked by git)
├── .env.example         # Template for environment variables
├── .gitignore           # Git ignore configuration
└── run.py               # Application entry point
```

## Usage

1. Navigate to `http://127.0.0.1:5000/` in your web browser
2. Enter or paste news text into the text area
3. Click "Analyze Sentiment"
4. The sentiment result (Positive, Neutral, or Negative) will be displayed below the form

## Technical Implementation Notes

- The application employs a **Flask factory pattern** for better modularity and testability
- **Response handling** includes regex pattern matching to extract sentiment classifications from potentially verbose API responses
- **Error handling** is implemented at multiple levels to provide meaningful feedback during API failures
- **Temperature setting** of 0.1 ensures more deterministic, consistent results from the language model

## Limitations

This MVP is intentionally minimalistic and lacks:
- User authentication
- Result persistence
- Advanced error handling
- Production deployment configurations

## Next Steps

To move beyond this MVP, consider implementing:
1. Database integration for storing analysis results
2. User authentication and profile management
3. Advanced result visualization
4. Batch analysis capabilities

---

*This MVP was developed as part of CITS5505 Agile Web Development.*