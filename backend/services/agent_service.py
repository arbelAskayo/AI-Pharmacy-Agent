"""
Agent orchestration service.
Implements the tool-calling loop for the pharmacy assistant.
"""
import json
from typing import Optional
from services.openai_client import create_chat_completion
from tools.registry import TOOLS_SCHEMA, execute_tool
from prompts.system_prompt import get_system_prompt
from logging_config import get_logger

logger = get_logger(__name__)

# Maximum number of tool-calling iterations to prevent infinite loops
MAX_TOOL_ITERATIONS = 10


def run_agent(
    messages: list[dict],
    user_id: Optional[int] = None
) -> dict:
    """
    Run the pharmacy assistant agent with tool-calling loop.
    
    Args:
        messages: Conversation history (stateless - includes all context)
        user_id: Optional user ID for tool operations
        
    Returns:
        Dict containing:
        - final: The final assistant response message
        - trace: Tool calls and results for debugging
    """
    logger.info("agent_run_start", message_count=len(messages), user_id=user_id)
    
    # Prepare messages with system prompt
    full_messages = _prepare_messages(messages)
    
    # Track tool calls and results for the trace
    trace = {
        "tool_calls": [],
        "tool_results": []
    }
    
    # Tool-calling loop
    iteration = 0
    while iteration < MAX_TOOL_ITERATIONS:
        iteration += 1
        logger.info("agent_iteration", iteration=iteration)
        
        # Call OpenAI
        response = create_chat_completion(
            messages=full_messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )
        
        # Get the assistant message
        if not response.get("choices"):
            logger.error("agent_no_choices")
            return _create_error_response("No response from AI model", trace)
        
        choice = response["choices"][0]
        assistant_message = choice["message"]
        finish_reason = choice["finish_reason"]
        
        # Check if we need to execute tools
        tool_calls = assistant_message.get("tool_calls", [])
        
        if tool_calls:
            # Execute each tool call
            logger.info("agent_tool_calls", count=len(tool_calls))
            
            # Add assistant message with tool calls to conversation
            full_messages.append(assistant_message)
            
            for tool_call in tool_calls:
                tool_call_id = tool_call["id"]
                function_name = tool_call["function"]["name"]
                
                # Parse arguments
                try:
                    arguments = json.loads(tool_call["function"]["arguments"])
                except json.JSONDecodeError:
                    arguments = {}
                
                # Record tool call in trace
                trace["tool_calls"].append({
                    "id": tool_call_id,
                    "name": function_name,
                    "arguments": arguments
                })
                
                logger.info(
                    "agent_executing_tool",
                    tool_name=function_name,
                    tool_call_id=tool_call_id
                )
                
                # Execute the tool
                result = execute_tool(function_name, arguments)
                
                # Record result in trace
                trace["tool_results"].append({
                    "tool_call_id": tool_call_id,
                    "name": function_name,
                    "success": result.get("success", False),
                    "result": result.get("data") if result.get("success") else None,
                    "error": result.get("error") if not result.get("success") else None
                })
                
                logger.info(
                    "agent_tool_result",
                    tool_name=function_name,
                    success=result.get("success", False)
                )
                
                # Add tool result to conversation
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(result)
                }
                full_messages.append(tool_message)
            
            # Continue loop to let model process tool results
            continue
        
        # No tool calls - we have a final response
        logger.info("agent_final_response", finish_reason=finish_reason)
        
        final_response = {
            "role": "assistant",
            "content": assistant_message.get("content", "")
        }
        
        return {
            "final": final_response,
            "trace": trace
        }
    
    # Hit max iterations
    logger.warning("agent_max_iterations", max=MAX_TOOL_ITERATIONS)
    return _create_error_response(
        "I apologize, but I'm having trouble completing this request. Please try again.",
        trace
    )


def _prepare_messages(messages: list[dict]) -> list[dict]:
    """
    Prepare messages for the API call.
    Ensures system prompt is present and messages are properly formatted.
    """
    full_messages = []
    
    # Check if system prompt already exists
    has_system = any(m.get("role") == "system" for m in messages)
    
    if not has_system:
        full_messages.append({
            "role": "system",
            "content": get_system_prompt()
        })
    
    # Add user messages
    for msg in messages:
        # Skip empty messages
        if not msg.get("content") and not msg.get("tool_calls"):
            continue
        
        # Ensure proper format
        formatted = {"role": msg["role"]}
        
        if msg.get("content"):
            formatted["content"] = msg["content"]
        
        if msg.get("tool_calls"):
            formatted["tool_calls"] = msg["tool_calls"]
        
        if msg.get("tool_call_id"):
            formatted["tool_call_id"] = msg["tool_call_id"]
        
        if msg.get("name"):
            formatted["name"] = msg["name"]
        
        full_messages.append(formatted)
    
    return full_messages


def _create_error_response(message: str, trace: dict) -> dict:
    """Create an error response structure."""
    return {
        "final": {
            "role": "assistant",
            "content": message
        },
        "trace": trace
    }

