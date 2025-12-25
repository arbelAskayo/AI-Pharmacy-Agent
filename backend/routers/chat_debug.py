"""
Debug chat endpoint for Milestone 2 validation.
Provides a synchronous (non-streaming) chat endpoint with full trace output.
"""
from fastapi import APIRouter, HTTPException
from schemas.chat import ChatDebugRequest, ChatDebugResponse
from services.agent_service import run_agent
from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/debug", response_model=ChatDebugResponse)
async def chat_debug(request: ChatDebugRequest) -> ChatDebugResponse:
    """
    Debug chat endpoint for testing tool calling.
    
    This is a synchronous (non-streaming) endpoint that returns:
    - The final assistant response
    - A trace of all tool calls and results
    
    Use this for Milestone 2 validation. The streaming SSE endpoint
    will be added in Milestone 3.
    """
    # Verify OpenAI is configured
    if not settings.openai_configured:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured. Set OPENAI_API_KEY environment variable."
        )
    
    logger.info(
        "chat_debug_request",
        message_count=len(request.messages),
        user_id=request.user_id
    )
    
    try:
        # Convert Pydantic models to dicts for the agent
        messages = [msg.model_dump(exclude_none=True) for msg in request.messages]
        
        # Run the agent
        result = run_agent(
            messages=messages,
            user_id=request.user_id
        )
        
        logger.info(
            "chat_debug_response",
            tool_call_count=len(result["trace"]["tool_calls"]),
            final_content_length=len(result["final"]["content"]) if result["final"]["content"] else 0
        )
        
        return ChatDebugResponse(
            final=result["final"],
            trace=result["trace"]
        )
        
    except ValueError as e:
        # Configuration errors (e.g., missing API key)
        logger.error("chat_debug_config_error", error=str(e))
        raise HTTPException(status_code=503, detail=str(e))
        
    except Exception as e:
        # Unexpected errors
        logger.error("chat_debug_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

