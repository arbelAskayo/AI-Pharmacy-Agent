"""
SSE streaming chat endpoint.
POST /api/chat - Main chat endpoint with Server-Sent Events streaming.
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Iterator

from schemas.chat import ChatDebugRequest
from services.agent_service import run_agent_stream
from utils.sse import format_sse
from logging_config import get_logger

router = APIRouter(prefix="/api", tags=["chat"])
logger = get_logger(__name__)


def _generate_sse_events(messages: list[dict], user_id: int | None) -> Iterator[str]:
    """
    Generator that produces SSE-formatted events from the agent.
    
    Args:
        messages: Conversation history
        user_id: Optional user ID
        
    Yields:
        SSE-formatted strings (data: {...}\n\n)
    """
    try:
        for event in run_agent_stream(messages, user_id):
            yield format_sse(event)
    except Exception as e:
        logger.error("sse_generation_error", error=str(e))
        error_event = {
            "type": "error",
            "message": f"Internal server error: {str(e)}",
            "code": "INTERNAL_ERROR"
        }
        yield format_sse(error_event)


@router.post("/chat")
async def chat_stream(request: ChatDebugRequest):
    """
    Main chat endpoint with SSE streaming.
    
    Streams structured events as the agent processes the request:
    - tool_call: When the agent calls a tool
    - tool_result: Result of a tool execution
    - assistant_token: Text token being streamed
    - final_message: Complete response with tool trace
    - error: Error events
    
    Request body:
    {
        "messages": [{"role": "user", "content": "..."}],
        "user_id": optional int
    }
    
    Response: text/event-stream with SSE events
    Each event is formatted as: data: {json}\n\n
    """
    logger.info(
        "chat_stream_request",
        message_count=len(request.messages),
        user_id=request.user_id
    )
    
    # Convert Pydantic models to dicts
    messages = [msg.model_dump(exclude_none=True) for msg in request.messages]
    
    return StreamingResponse(
        _generate_sse_events(messages, request.user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )

