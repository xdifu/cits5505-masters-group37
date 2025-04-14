# Handles interaction with the OpenAI API for sentiment analysis.

import os
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

        # Make the API call to the chat completions endpoint
        completion = client.chat.completions.create(
            model="gpt-4.1-nano", # Specify the desired model
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to analyze the sentiment of news text. Classify the sentiment as Positive, Neutral, or Negative."},
                {"role": "user", "content": f"Analyze the sentiment of the following news text: {text}"}
            ],
            max_tokens=10, # Limit response length
            temperature=0.1 # Lower temperature for more deterministic output
        )

        # Extract the sentiment from the response
        sentiment = completion.choices[0].message.content.strip().capitalize()

        # Basic validation to ensure the response is one of the expected categories
        if sentiment in ['Positive', 'Neutral', 'Negative']:
            return sentiment
        else:
            # Handle unexpected responses from the API
            print(f"Unexpected API response: {sentiment}")
            return "Error: Unexpected response format from API."

    except OpenAIError as e:
        # Handle potential errors during the API call (e.g., network issues, authentication errors)
        print(f"OpenAI API error: {e}")
        return f"Error: Could not connect to OpenAI API. {e}"
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred during analysis."
