# Handles interaction with the OpenAI API for sentiment analysis using Pydantic and Structured Outputs.

from enum import Enum
from pydantic import BaseModel, ValidationError, Field
from openai import OpenAI, OpenAIError
import os
from typing import List, Optional
import datetime # For date parsing attempt

# Define the allowed sentiment values using an Enum for strict validation
class SentimentEnum(str, Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"

# Define predefined intent tags
# This list can be expanded based on common news categories or analysis needs.
PREDEFINED_INTENT_TAGS = [
    "News Report", "Market Analysis", "Product Review", "Opinion Piece", "Interview",
    "Investigative Report", "Feature Story", "Press Release", "Advertisement",
    "Political Commentary", "Economic Forecast", "Technology Update", "Health & Wellness",
    "Environmental News", "Social Issue Discussion", "Complaint", "Recommendation", "Inquiry",
    "Discussion/Commentary", "Satire/Humor", "Obituary", "Event Announcement", "Travelogue",
    "Educational Content", "Legal Notice", "Sports Report", "Cultural Review", "Scientific Discovery",
    "Stock Market Update", "Financial Regulation News", "Company Earnings Report", "Economic Policy Analysis",
    "International Trade News", "Cryptocurrency News", "Real Estate Market Trends", "Startup Funding Announcement"
]

# Define the Pydantic model that represents the expected structured output from OpenAI for a single news item

class KeywordSentiment(BaseModel):
    text: str = Field(description="The extracted keyword.")
    # It's often hard for models to assign a reliable, distinct sentiment to *each* keyword out of context.
    # For now, we'll aim to get keywords, and associate them with the article's overall sentiment later.
    # If direct keyword sentiment is crucial and achievable, this model can be expanded.
    # sentiment_score: Optional[float] = Field(default=None, description="Sentiment score of the keyword itself, if determinable.")

class SingleNewsItemAnalysis(BaseModel):
    sentiment_label: SentimentEnum = Field(description="Overall sentiment label of the text (Positive, Neutral, or Negative).")
    sentiment_score: float = Field(description="Overall sentiment score from -1.0 (very negative) to +1.0 (very positive). Ensure this is a numeric value.")
    intents: Optional[List[str]] = Field(default_factory=list, description=f"List of up to 5 most relevant intent tags from the predefined list: {PREDEFINED_INTENT_TAGS}")
    keywords: Optional[List[str]] = Field(default_factory=list, description="List of up to 10-15 most relevant extracted keywords from the text. These should be single words or short multi-word phrases.") # Changed from KeywordSentiment for now
    publication_date: Optional[str] = Field(default=None, description="Estimated publication date of the news item in YYYY-MM-DD format. Return null if not found or ambiguous.")

def analyze_text_data(text: str) -> SingleNewsItemAnalysis:
    """
    Analyzes the sentiment, intents, keywords, and publication date of the provided text 
    using the OpenAI API's structured output parsing feature with Pydantic validation.

    Args:
        text (str): The news text to analyze.

    Returns:
        SingleNewsItemAnalysis: A Pydantic model containing sentiment label, sentiment score,
                                a list of intents, and a list of keywords. Returns an instance 
                                with default/empty values and neutral sentiment if analysis 
                                or validation fails or input text is too short.
    """
    # Add a check for empty or very short input text
    if not text or len(text.strip()) < 10: # Minimum 10 characters for meaningful analysis
        print(f"Input text is too short or empty. Skipping OpenAI analysis. Text (first 50 chars): '{text[:50]}...'")
        return SingleNewsItemAnalysis(
            sentiment_label=SentimentEnum.NEUTRAL,
            sentiment_score=0.0,
            intents=[],
            keywords=[],
            publication_date=None
        )
    
    # Ensure OPENAI_API_KEY is set, otherwise raise an error or handle appropriately
    # For example, by checking os.environ.get("OPENAI_API_KEY")
    # This part is assumed to be handled by the app's configuration.
    
    # Initialize OpenAI client (consider initializing it once globally in your app)
    # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    client = OpenAI() # Assuming API key is set in environment variables

    system_prompt = f"""You are an expert news text analyzer. Analyze the provided text and return a JSON object with the following fields:
    - "sentiment_label": Must be one of "Positive", "Neutral", or "Negative".
    - "sentiment_score": A float between -1.0 (very negative) and +1.0 (very positive).
    - "intents": A list of up to 5 most relevant intent tags. Choose from this predefined list: {PREDEFINED_INTENT_TAGS}. If no specific intent from the list is highly relevant, you can return an empty list or a general tag like "News Report".
    - "keywords": A list of 10-15 most relevant and distinct keywords or key phrases from the text.
    - "publication_date": The estimated publication date in YYYY-MM-DD format. If not found or ambiguous, return null.
    
    Ensure the output is a valid JSON object matching this structure.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", # Or your preferred model that supports JSON mode
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
        )
        
        response_content = response.choices[0].message.content
        if response_content is None:
            # Handle cases where response_content is None, perhaps log an error or return a default object
            print("OpenAI response content is None.")
            return SingleNewsItemAnalysis(sentiment_label=SentimentEnum.NEUTRAL, sentiment_score=0.0, intents=[], keywords=[], publication_date=None)

        analysis_data = SingleNewsItemAnalysis.model_validate_json(response_content)
        return analysis_data

    except ValidationError as ve:
        # Log the validation error details for debugging
        print(f"Pydantic Validation Error: {ve.errors()}")
        # Fallback to a neutral default if validation fails
        return SingleNewsItemAnalysis(sentiment_label=SentimentEnum.NEUTRAL, sentiment_score=0.0, intents=[], keywords=[], publication_date=None)

    except OpenAIError as e:
        # Log the OpenAI API error
        print(f"OpenAI API Error: {e}")
        # Fallback to a neutral default
        return SingleNewsItemAnalysis(sentiment_label=SentimentEnum.NEUTRAL, sentiment_score=0.0, intents=[], keywords=[], publication_date=None)

    except Exception as e:
        # Log any other unexpected errors
        print(f"Unexpected error during OpenAI analysis: {e}")
        # Fallback to a neutral default
        return SingleNewsItemAnalysis(sentiment_label=SentimentEnum.NEUTRAL, sentiment_score=0.0, intents=[], keywords=[], publication_date=None)

# The original `AnalysisOutput` class is replaced by `SingleNewsItemAnalysis`.
# The `analyze_sentiment` function can be kept for simple sentiment label retrieval if needed,
# or deprecated if all use cases now require the full analysis data.

def analyze_sentiment(text: str) -> str:
    """
    Analyzes the sentiment of the provided text, returning only the label.
    This function now acts as a wrapper around analyze_text_data for backward compatibility
    or for cases where only the sentiment label is needed.

    Args:
        text (str): The text to analyze.

    Returns:
        str: The sentiment label (e.g., "Positive", "Neutral", "Negative").
    """
    analysis_result = analyze_text_data(text)
    return analysis_result.sentiment_label.value # Return the string value of the Enum

# Example usage (for testing purposes):
if __name__ == '__main__':
    # Ensure OPENAI_API_KEY is set as an environment variable before running this
    sample_text_positive = "The new product launch was a massive success, exceeding all expectations. Customers love the new features!"
    sample_text_negative = "The company's recent performance has been disappointing, with profits plummeting and stocks taking a dive after the scandal."
    sample_text_mixed = "While the economic outlook shows some signs of improvement in manufacturing, the retail sector continues to struggle with low consumer confidence."
    sample_text_dated = "Stock markets surged yesterday, January 5th, 2024, following positive inflation news. Analysts are optimistic."
    
    print("--- Analyzing Positive Text ---")
    result_pos = analyze_text_data(sample_text_positive)
    print(f"Label: {result_pos.sentiment_label.value}, Score: {result_pos.sentiment_score}")
    print(f"Intents: {result_pos.intents}")
    print(f"Keywords: {result_pos.keywords}")
    print(f"Publication Date: {result_pos.publication_date}")
    print("-----------------------------")

    print("--- Analyzing Negative Text ---")
    result_neg = analyze_text_data(sample_text_negative)
    print(f"Label: {result_neg.sentiment_label.value}, Score: {result_neg.sentiment_score}")
    print(f"Intents: {result_neg.intents}")
    print(f"Keywords: {result_neg.keywords}")
    print(f"Publication Date: {result_neg.publication_date}")
    print("-----------------------------")

    print("--- Analyzing Mixed Text ---")
    result_mix = analyze_text_data(sample_text_mixed)
    print(f"Label: {result_mix.sentiment_label.value}, Score: {result_mix.sentiment_score}")
    print(f"Intents: {result_mix.intents}")
    print(f"Keywords: {result_mix.keywords}")
    print(f"Publication Date: {result_mix.publication_date}")
    print("-----------------------------")

    print("--- Analyzing Dated Text ---")
    result_dated = analyze_text_data(sample_text_dated)
    print(f"Label: {result_dated.sentiment_label.value}, Score: {result_dated.sentiment_score}")
    print(f"Intents: {result_dated.intents}")
    print(f"Keywords: {result_dated.keywords}")
    print(f"Publication Date: {result_dated.publication_date}")
    print("-----------------------------")

    # Test the legacy analyze_sentiment function
    # print("\n--- Legacy Sentiment Function Test ---")
    # print(f"Positive text sentiment: {analyze_sentiment(sample_text_positive)}")
    # print(f"Negative text sentiment: {analyze_sentiment(sample_text_negative)}")
    # print("----------------------------------")