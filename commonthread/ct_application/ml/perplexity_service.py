import requests
import json
import logging

logger = logging.getLogger(__name__)

def get_perplexity_chat_response(api_key: str, context: str, user_message: str) -> dict:
    """
    Calls the Perplexity API with the given context and user message.

    Args:
        api_key: The Perplexity API key.
        context: The project context (concatenated stories).
        user_message: The user's message/question.

    Returns:
        A dictionary containing the Perplexity API JSON response or an error message.
    """
    perplexity_api_url = "https://api.perplexity.ai/chat/completions"
    model_name = "sonar-medium-chat"  # Or any other suitable model

    perplexity_payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant. Use the following project stories to answer questions about the project:\n\n{context}"},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(perplexity_api_url, json=perplexity_payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Perplexity API HTTPError: {e.response.status_code} {e.response.reason}. Response: {e.response.text}")
        error_detail = "No additional detail from server."
        try:
            error_detail = e.response.json().get('error', {}).get('message', e.response.text)
        except json.JSONDecodeError:
            error_detail = e.response.text
        return {"error": f"API request failed: {e.response.status_code} {e.response.reason}", "details": error_detail, "status_code": e.response.status_code}
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Perplexity API ConnectionError: {e}")
        return {"error": "Could not connect to Perplexity API.", "details": str(e), "status_code": 503} # Service Unavailable
    except requests.exceptions.Timeout as e:
        logger.error(f"Perplexity API Timeout: {e}")
        return {"error": "Request to Perplexity API timed out.", "details": str(e), "status_code": 504} # Gateway Timeout
    except requests.exceptions.RequestException as e:
        logger.error(f"Perplexity API RequestException: {e}")
        return {"error": "An unexpected error occurred while communicating with Perplexity API.", "details": str(e), "status_code": 500}
    except json.JSONDecodeError as e: # Should not happen if Perplexity API is consistent, but good to have
        logger.error(f"Failed to decode Perplexity API JSON response: {e}")
        return {"error": "Failed to decode Perplexity API response.", "details": str(e), "status_code": 500}

if __name__ == '__main__':
    # This part is for testing the service directly, if needed.
    # You'd need to set a dummy API key and provide some context/message.
    # For example:
    # test_api_key = "YOUR_TEST_API_KEY"
    # test_context = "Story 1: The project is about cats. Story 2: Cats are fluffy."
    # test_user_message = "What is the project about?"
    # response = get_perplexity_chat_response(test_api_key, test_context, test_user_message)
    # print(response)
    pass
