# Handles interaction with the OpenAI API for sentiment analysis using Pydantic and Structured Outputs.

import os
from enum import Enum
from pydantic import BaseModel, ValidationError
from openai import OpenAI, OpenAIError # Keep OpenAIError for API-level issues

# Define the allowed sentiment values using an Enum for strict validation
class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

# Define the Pydantic model that represents the expected structured output
class SentimentOutput(BaseModel):
    sentiment: SentimentEnum # Use the Enum type for the sentiment field

def analyze_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of the provided text using the OpenAI API's
    structured output parsing feature with Pydantic validation.

    Args:
        text (str): The news text to analyze.

    Returns:
        str: The sentiment classification ('Positive', 'Neutral', 'Negative')
             or an error message if analysis or validation fails.
    """
    try:
        # Initialize the OpenAI client using the API key from environment variables
        # Ensure the API key is set in your .env file
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Use the beta parse method with the Pydantic model for response_format
        # Note: Using gpt-4o as suggested, as gpt-4.1-nano might not support this
        # or might have access restrictions with your key. Adjust if needed.
        response_model = client.beta.chat.completions.parse(
            model="gpt-4.1-nano", 
            messages=[
                # System message guides the model on the task and expected output format implicitly via Pydantic
                {"role": "system", "content": f"You are a sentiment analyzer. Classify the sentiment of the user's text strictly as one of the allowed values: {', '.join([e.value for e in SentimentEnum])}."},
                {"role": "user", "content": f"Analyze this text: {text}"}
            ],
            response_format=SentimentOutput # Pass the Pydantic class directly
        )

        # If parsing is successful, return the validated sentiment value from the Enum
        return response_model.sentiment.value

    except ValidationError as ve:
        # Handle cases where the API response doesn't match the Pydantic model
        print(f"Pydantic Validation Error: The API response did not match the expected format. Details: {ve}")
        # You might want to inspect 've.json()' for more details on the failure
        return "Error: Invalid sentiment format received from API."

    except OpenAIError as e:
        # Handle API-specific errors (e.g., authentication, rate limits, model not found)
        print(f"OpenAI API error: {e}")
        # Check for specific error types if needed, e.g., AuthenticationError, RateLimitError
        return f"Error: OpenAI API request failed ({e.status_code if hasattr(e, 'status_code') else 'N/A'})" # Provide status code if available

    except Exception as e:
        # Catch any other potential exceptions during the process
        print(f"An unexpected error occurred during sentiment analysis: {e}")
        return "Error: An unexpected error occurred."