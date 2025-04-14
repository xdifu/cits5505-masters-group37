# Handles interaction with the OpenAI API for sentiment analysis.

import os
import re  # Import regex for pattern matching
from openai import OpenAI, OpenAIError # Use OpenAIError for specific exceptions

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the provided text using the OpenAI API.

    Args:
        text (str): The news text to analyze.

    Returns:
        str: The sentiment classification ('Positive', 'Neutral', 'Negative') or an error message.
    """
    try:
        # Initialize the OpenAI client using the API key from environment variables
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Make the API call to the chat completions endpoint with a more explicit prompt
        completion = client.chat.completions.create(
            model="gpt-4.1-nano", # Specify the desired model
            messages=[
                {"role": "system", "content": "You are a sentiment analyzer that classifies text as strictly Positive, Neutral, or Negative. Respond with ONLY ONE WORD: 'Positive', 'Neutral', or 'Negative'."},
                {"role": "user", "content": f"Classify the sentiment of this text: {text}"}
            ],
            max_tokens=25, # Slight increase to allow for explanations but not too verbose
            temperature=0.1 # Lower temperature for more deterministic output
        )

        # Extract the content of the response
        response_text = completion.choices[0].message.content.strip()
        
        # Use regex to extract just the sentiment from a potentially longer response
        # Look for positive, neutral, or negative in the response (case insensitive)
        sentiment_match = re.search(r'positive|neutral|negative', response_text, re.IGNORECASE)
        
        if sentiment_match:
            # If found, capitalize the first letter for consistency
            sentiment = sentiment_match.group(0).capitalize()
            return sentiment
        else:
            # If no match is found, check if the whole response is one of our categories
            if response_text.lower() in ['positive', 'neutral', 'negative']:
                return response_text.capitalize()
            else:
                # Log unexpected response format
                print(f"Unexpected API response: {response_text}")
                return "Error: Could not determine sentiment from API response."

    except OpenAIError as e:
        # Handle API-specific errors (e.g., authentication, rate limits)
        print(f"OpenAI API error: {e}")
        return f"Error: OpenAI API request failed ({e})"
    except Exception as e:
        # Catch any other potential exceptions during the process
        print(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred."
