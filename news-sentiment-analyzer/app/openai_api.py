# Handles interaction with the OpenAI API for sentiment analysis using Structured Outputs.

import os
import json # Import json for parsing the response
from openai import OpenAI, OpenAIError # Use OpenAIError for specific exceptions

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the provided text using the OpenAI API with Structured Outputs.

    Args:
        text (str): The news text to analyze.

    Returns:
        str: The sentiment classification ('Positive', 'Neutral', 'Negative') or an error message.
             Returns "Error: API Refusal" if the model refuses to respond.
             Returns "Error: Incomplete Response" if the response was cut short.
    """
    try:
        # Initialize the OpenAI client using the API key from environment variables
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Define the JSON schema for the expected response
        sentiment_schema = {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "description": "The sentiment classification of the text.",
                    "enum": ["Positive", "Neutral", "Negative"] # Strict allowed values
                }
            },
            "required": ["sentiment"], # Sentiment field is mandatory
            "additionalProperties": False # No other properties allowed
        }

        # Make the API call using the responses endpoint with structured output format
        response = client.responses.create(
            model="gpt-4.1-nano", # Ensure this model supports structured outputs
            input=[
                {"role": "system", "content": "You are a sentiment analyzer. Classify the sentiment of the user's text strictly as Positive, Neutral, or Negative according to the provided JSON schema."},
                {"role": "user", "content": f"Analyze this text: {text}"}
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "sentiment_analysis_result", # A name for the schema usage
                    "schema": sentiment_schema,
                    "strict": True # Enforce schema adherence strictly
                }
            },
            # Consider adding max_output_tokens if needed, e.g., max_output_tokens=50
        )

        # Check response status and content type
        if response.status == "completed":
            # Access the structured output content
            output_content = response.output[0].content[0]

            if output_content.type == "output_text":
                # The SDK should ideally parse this automatically if the schema is valid
                try:
                    # The output_text should be the JSON string when using json_schema
                    parsed_json = json.loads(output_content.text)
                    sentiment = parsed_json.get("sentiment")
                    if sentiment in ["Positive", "Neutral", "Negative"]:
                        return sentiment
                    else:
                        # This case should be rare with strict schema enforcement
                        print(f"Unexpected sentiment value in response: {sentiment}")
                        return "Error: Invalid sentiment value received."
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON response: {output_content.text}")
                    return "Error: API returned invalid JSON."
                except AttributeError:
                     # Fallback if direct access fails or structure is unexpected
                     print(f"Unexpected response structure: {output_content}")
                     return "Error: Could not extract sentiment from response structure."

            elif output_content.type == "refusal":
                # Handle cases where the model refused to answer for safety reasons
                print(f"API Refusal: {output_content.refusal}")
                return "Error: API Refusal"
            else:
                # Handle other unexpected content types
                print(f"Unexpected content type: {output_content.type}")
                return "Error: Unexpected response content type."

        elif response.status == "incomplete":
            # Handle incomplete responses (e.g., due to max_output_tokens)
            reason = response.incomplete_details.reason if response.incomplete_details else "unknown"
            print(f"Incomplete response from API. Reason: {reason}")
            return f"Error: Incomplete Response ({reason})"
        else:
            # Handle other statuses like 'failed'
            print(f"API call failed with status: {response.status}")
            return f"Error: API call failed ({response.status})"

    except OpenAIError as e:
        # Handle API-specific errors (e.g., authentication, rate limits, invalid schema)
        print(f"OpenAI API error: {e}")
        if "invalid json schema" in str(e).lower():
             return "Error: Invalid JSON schema provided to API."
        return f"Error: OpenAI API request failed ({e})"
    except Exception as e:
        # Catch any other potential exceptions during the process
        print(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred."