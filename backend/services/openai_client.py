"""
OpenAI client wrapper.
Centralizes OpenAI API usage with proper configuration.
"""
from typing import Optional
from openai import OpenAI
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# Initialize OpenAI client (lazy initialization)
_client: Optional[OpenAI] = None


def get_client() -> OpenAI:
    """
    Get the OpenAI client instance.
    Initializes on first use to avoid errors if API key is not set at import time.
    """
    global _client
    
    if _client is None:
        if not settings.openai_configured:
            raise ValueError(
                "OpenAI API key is not configured. "
                "Set OPENAI_API_KEY environment variable."
            )
        
        _client = OpenAI(api_key=settings.openai_api_key)
        logger.info("openai_client_initialized", model=settings.openai_model)
    
    return _client


def create_chat_completion(
    messages: list[dict],
    tools: Optional[list[dict]] = None,
    tool_choice: str = "auto"
) -> dict:
    """
    Create a chat completion using OpenAI API.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        tools: Optional list of tool schemas for function calling
        tool_choice: How to handle tools - "auto", "none", or specific tool
        
    Returns:
        The API response as a dictionary
    """
    client = get_client()
    
    # Build request parameters
    params = {
        "model": settings.openai_model,
        "messages": messages,
    }
    
    # Add tools if provided
    if tools:
        params["tools"] = tools
        params["tool_choice"] = tool_choice
    
    logger.info(
        "openai_request",
        model=settings.openai_model,
        message_count=len(messages),
        has_tools=bool(tools)
    )
    
    try:
        response = client.chat.completions.create(**params)
        
        # Convert response to dict for easier handling
        result = {
            "id": response.id,
            "model": response.model,
            "choices": []
        }
        
        for choice in response.choices:
            choice_data = {
                "index": choice.index,
                "finish_reason": choice.finish_reason,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content,
                }
            }
            
            # Include tool calls if present
            if choice.message.tool_calls:
                choice_data["message"]["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in choice.message.tool_calls
                ]
            
            result["choices"].append(choice_data)
        
        # Add usage info
        if response.usage:
            result["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        logger.info(
            "openai_response",
            finish_reason=result["choices"][0]["finish_reason"] if result["choices"] else None,
            has_tool_calls="tool_calls" in result["choices"][0]["message"] if result["choices"] else False
        )
        
        return result
        
    except Exception as e:
        logger.error("openai_error", error=str(e))
        raise

