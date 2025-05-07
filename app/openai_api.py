# Handles interaction with g4f for sentiment analysis using Pydantic and Structured Outputs.

import os # os is kept if other parts of the app might use env vars, but not for g4f client init
from enum import Enum
from pydantic import BaseModel, ValidationError
# Remove OpenAI, OpenAIError imports, add g4f Client
from g4f.client import Client
# import json # Not strictly needed if Pydantic's model_validate_json handles the string directly

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
    Analyzes the sentiment of the provided text using the g4f client
    and Pydantic validation for structured output.

    Args:
        text (str): The news text to analyze.

    Returns:
        str: The sentiment classification ('Positive', 'Neutral', 'Negative')
             or an error message if analysis or validation fails.
    """
    try:
        # Initialize the g4f client
        # No API key is typically passed directly to the g4f Client constructor
        g4f_client = Client()

        allowed_sentiments = ', '.join([e.value for e in SentimentEnum])
        # System message guides the model to output JSON matching SentimentOutput
        system_content = (
            f"You are a sentiment analyzer. Classify the sentiment of the user's text. "
            f"Respond ONLY with a JSON object formatted as {{\'sentiment\': \'<sentiment_value>\'}}, "
            f"where <sentiment_value> is one of: {allowed_sentiments}."
        )
        
        # Use a model supported by g4f. "gpt-4o-mini" is an example from g4f docs.
        # You may need to experiment with different models available through g4f.
        response = g4f_client.chat.completions.create(
            model="gpt-4o-mini", # Or another model supported by g4f
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"Analyze this text: {text}"}
            ],
            # g4f's create method does not have a 'response_format' for Pydantic.
            # We expect a string response that we will then parse.
        )

        # Extract the raw string content from the g4f response
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            raw_response_content = response.choices[0].message.content.strip()
        else:
            print("Error: Received an empty or invalid response structure from g4f.")
            return "Error: Invalid response structure from g4f."

        # Attempt to parse the string response using the Pydantic model
        parsed_output = SentimentOutput.model_validate_json(raw_response_content)
        return parsed_output.sentiment.value

    except ValidationError as ve:
        # Handle cases where the API response doesn't match the Pydantic model
        print(f"Pydantic Validation Error: The g4f response did not match the expected JSON format. Details: {ve}")
        print(f"Raw response from g4f: {raw_response_content if 'raw_response_content' in locals() else 'N/A'}")
        return "Error: Invalid sentiment format received from API."

    # Catch g4f specific errors if known, or general exceptions.
    # OpenAIError is no longer relevant here.
    except Exception as e:
        # Catch any other potential exceptions during the process
        print(f"An unexpected error occurred during sentiment analysis with g4f: {e}")
        print(f"Exception Type: {type(e).__name__}")
        return "Error: An unexpected error occurred."