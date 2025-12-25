"""
Chat-related Pydantic schemas.
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # "system", "user", "assistant", "tool"
    content: Optional[str] = None
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ChatDebugRequest(BaseModel):
    """Request for the debug chat endpoint."""
    messages: List[ChatMessage]
    user_id: Optional[int] = None


class ToolCallTrace(BaseModel):
    """Record of a tool call for debugging."""
    id: str
    name: str
    arguments: dict


class ToolResultTrace(BaseModel):
    """Record of a tool result for debugging."""
    tool_call_id: str
    name: str
    success: bool
    result: Optional[Any] = None
    error: Optional[dict] = None


class AgentTrace(BaseModel):
    """Trace of all tool operations during agent execution."""
    tool_calls: List[ToolCallTrace]
    tool_results: List[ToolResultTrace]


class FinalMessage(BaseModel):
    """The final assistant response."""
    role: str
    content: str


class ChatDebugResponse(BaseModel):
    """Response from the debug chat endpoint."""
    final: FinalMessage
    trace: AgentTrace

