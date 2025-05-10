import pytest
from unittest.mock import patch, MagicMock
from app.openai_api import analyze_sentiment, SentimentEnum, SentimentOutput
from openai import OpenAIError
from pydantic import ValidationError

pytestmark = pytest.mark.openai  # Mark all tests in this file as OpenAI API tests

def mock_openai_response(sentiment_value):
    """Helper function to create a mock OpenAI response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.parsed = SentimentOutput(sentiment=sentiment_value)
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
    mock_openai.beta.chat.completions.parse.return_value = mock_openai_response(sentiment)

    result = analyze_sentiment(test_text)
    assert result == sentiment.value, f"Expected {sentiment.value}, got {result}"

    # Verify API call
    mock_openai.beta.chat.completions.parse.assert_called_once()
    call_args = mock_openai.beta.chat.completions.parse.call_args
    assert call_args[1]['model'] == "gpt-4.1-nano"
    assert isinstance(call_args[1]['response_format'], type(SentimentOutput))
    assert any(msg['content'] == f"Analyze this text: {test_text}"
              for msg in call_args[1]['messages'])

@pytest.mark.parametrize('error_type,error_params,expected_message', [
    (OpenAIError, {'status_code': 401}, "Error: OpenAI API request failed (Status: 401)"),
    (OpenAIError, {'status_code': 429}, "Error: OpenAI API request failed (Status: 429)"),
    (ValidationError, {'errors': [{'loc': ['sentiment'], 'msg': 'Invalid enum value'}]}, 
     "Error: Invalid sentiment format"),
    (Exception, {'args': ["Unexpected error"]}, "Error: An unexpected error occurred"),
])
def test_error_handling(mock_openai, error_type, error_params, expected_message):
    """Test various error scenarios in sentiment analysis."""
    if error_type == ValidationError:
        # Create an invalid response that will trigger ValidationError
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.parsed = {"invalid": "response"}
        mock_openai.beta.chat.completions.parse.return_value = mock_response
    else:
        # Create the error with provided parameters
        error = error_type("API Error")
        for key, value in error_params.items():
            setattr(error, key, value)
        mock_openai.beta.chat.completions.parse.side_effect = error

    result = analyze_sentiment("Test text")
    assert expected_message in result

@pytest.mark.parametrize('input_text,should_call_api', [
    ("", False),
    ("  ", False),
    ("Valid input", True),
])
def test_input_validation(mock_openai, input_text, should_call_api):
    """Test input validation in sentiment analysis."""
    if should_call_api:
        mock_openai.beta.chat.completions.parse.return_value = \
            mock_openai_response(SentimentEnum.NEUTRAL)
    
    result = analyze_sentiment(input_text)
    
    if should_call_api:
        mock_openai.beta.chat.completions.parse.assert_called_once()
        assert "Error" not in result
    else:
        mock_openai.beta.chat.completions.parse.assert_not_called()
        assert "Error" in result

def test_model_configuration(mock_openai):
    """Test OpenAI model configuration and parameters."""
    mock_openai.beta.chat.completions.parse.return_value = \
        mock_openai_response(SentimentEnum.NEUTRAL)
    
    analyze_sentiment("Test text")
    
    call_args = mock_openai.beta.chat.completions.parse.call_args
    assert call_args is not None, "API not called"
    
    # Verify model and configuration
    assert call_args[1]['model'] == "gpt-4.1-nano"
    assert call_args[1]['response_format'] == SentimentOutput
    
    # Verify message structure
    messages = call_args[1]['messages']
    assert len(messages) == 2, "Incorrect number of messages"
    assert messages[0]['role'] == 'system', "Missing system message"
    assert messages[1]['role'] == 'user', "Missing user message"
    assert all(isinstance(msg['content'], str) for msg in messages), \
        "Invalid message content type"
