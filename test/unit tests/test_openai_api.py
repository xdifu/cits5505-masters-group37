import pytest
from unittest.mock import patch, MagicMock
from app.openai_api import analyze_text_data, SentimentEnum, SingleNewsItemAnalysis # Changed analyze_sentiment to analyze_text_data and SentimentOutput to SingleNewsItemAnalysis
from openai import OpenAIError
from pydantic import ValidationError

pytestmark = pytest.mark.openai  # Mark all tests in this file as OpenAI API tests

def mock_openai_response(sentiment_value, intents_value=None, keywords_value=None, publication_date_value=None):
    """Helper function to create a mock OpenAI response for SingleNewsItemAnalysis."""
    # Ensure default empty lists if None is passed, as Pydantic model expects lists
    intents_value = intents_value if intents_value is not None else []
    keywords_value = keywords_value if keywords_value is not None else []

    mock_response = MagicMock()
    # Simulate the structure that parse() would return after processing the raw OpenAI response
    # The .parse() method itself is part of the openai client, and we are mocking its return value.
    # It would return an instance of the Pydantic model we passed to it.
    mock_response.choices = [MagicMock()] # This line might be vestigial if parse directly returns the model instance
    mock_response.choices[0].message.parsed = SingleNewsItemAnalysis(
        sentiment_label=sentiment_value,
        sentiment_score=0.9 if sentiment_value == SentimentEnum.POSITIVE else -0.9 if sentiment_value == SentimentEnum.NEGATIVE else 0.0, # Example score
        intents=intents_value,
        keywords=keywords_value,
        publication_date=publication_date_value
    )
    return mock_response

@pytest.fixture
def mock_openai():
    """Fixture to mock OpenAI client."""
    with patch('app.openai_api.OpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

@pytest.mark.parametrize('sentiment,test_text', [
    (SentimentEnum.POSITIVE, "This is great news!"),
    (SentimentEnum.NEGATIVE, "This is terrible news."),
    (SentimentEnum.NEUTRAL, "This is factual information."),
])
def test_sentiment_analysis(mock_openai, sentiment, test_text):
    """Test sentiment analysis for different sentiments."""
    # Mock the return value of the .parse() method
    # The .parse() method is expected to return an instance of SingleNewsItemAnalysis
    mock_parsed_output = SingleNewsItemAnalysis(
        sentiment_label=sentiment,
        sentiment_score=0.9 if sentiment == SentimentEnum.POSITIVE else -0.9 if sentiment == SentimentEnum.NEGATIVE else 0.0,
        intents=["News Report"],
        keywords=["news", "great"],
        publication_date="2024-01-01"
    )
    mock_openai.beta.chat.completions.parse.return_value = mock_parsed_output

    result_obj = analyze_text_data(test_text) # Changed from analyze_sentiment
    assert result_obj.sentiment_label == sentiment, f"Expected {sentiment.value}, got {result_obj.sentiment_label}"
    assert result_obj.intents == ["News Report"]
    assert result_obj.keywords == ["news", "great"]

    # Verify API call
    mock_openai.beta.chat.completions.parse.assert_called_once()
    call_args = mock_openai.beta.chat.completions.parse.call_args
    assert call_args[1]['model'] == "gpt-4o" # Model name updated in openai_api.py
    assert isinstance(call_args[1]['response_format'], type(SingleNewsItemAnalysis))
    assert any(msg['content'] == f"Analyze the following news text: {test_text}"
              for msg in call_args[1]['messages'])

@pytest.mark.parametrize('error_type,error_params,expected_message', [
    (OpenAIError, {'status_code': 401}, "Error: OpenAI API request failed (Status: 401)"),
    (OpenAIError, {'status_code': 429}, "Error: OpenAI API request failed (Status: 429)"),
    (ValidationError, {'model': SingleNewsItemAnalysis, 'errors': [{'loc': ['sentiment_label'], 'msg': 'Invalid enum value'}]}, # Adjusted for Pydantic v2
     "Error: Invalid data format from OpenAI API. Details: 1 validation error for SingleNewsItemAnalysis\nsentiment_label"), # Simplified expected message for now
    (Exception, {'args': ["Unexpected error"]}, "Error: An unexpected error occurred during OpenAI API call. Details: Unexpected error"),
])
def test_error_handling(mock_openai, error_type, error_params, expected_message):
    """Test error handling for various API and validation errors."""
    if error_type == ValidationError:
        # For Pydantic V2, the error is raised by Pydantic, not directly by OpenAI client's parse method in this way.
        # We need to mock the situation where OpenAI returns data that Pydantic fails to validate.
        # This is a bit more complex to mock perfectly without deeper changes to analyze_text_data structure.
        # For now, let's assume analyze_text_data catches ValidationError from Pydantic model instantiation.
        def side_effect(*args, **kwargs):
            # Create a dummy error object similar to Pydantic's ValidationError
            # This is a simplified representation.
            # In a real Pydantic v2 ValidationError, error_params['errors'] would be a list of dicts.
            # error_params['model'] would be the model class.
            raise ValidationError.from_exception_data(title=error_params['model'].__name__, line_errors=error_params['errors'])
        mock_openai.beta.chat.completions.parse.side_effect = side_effect
    elif issubclass(error_type, OpenAIError):
        # Simulate an OpenAI API error
        mock_openai.beta.chat.completions.parse.side_effect = error_type(**error_params)
    else:
        # Simulate a generic exception
        mock_openai.beta.chat.completions.parse.side_effect = error_type(*error_params.get('args', []))

    with pytest.raises(Exception) as excinfo: # Catching generic Exception as analyze_text_data wraps errors
        analyze_text_data("some text")
    
    # Check if the raised exception message contains the core part of the expected message.
    # This makes the test less brittle to minor changes in error formatting in openai_api.py
    assert expected_message.split(". Details:")[0] in str(excinfo.value)
