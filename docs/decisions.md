# Decisions (for Cursor + project context)

## Stack
- Backend: FastAPI (Python), SQLite
- Frontend: React (Vite)
- Streaming: Server-Sent Events (SSE)
- LLM: OpenAI GPT-5 via Responses API (vanilla), with tool/function calling

## Why this stack
- FastAPI is fast to build, clear API contracts, and works well with SSE streaming.
- SQLite is perfect for synthetic data and easy Docker setup.
- React (Vite) is lightweight and ideal for a simple streaming chat UI.
- SSE keeps the streaming model simple: backend emits events; UI renders incrementally.

## Key architecture decisions
- Stateless chat: the browser sends the full relevant conversation history each turn.
- Event-driven UI: backend streams structured SSE events:
  - assistant_token, tool_call, tool_result, final_message, error
- Tool-first facts: any DB-related claim must come from a tool call result.
- Safety-first: refuse medical advice requests and redirect to professionals.

## Non-goals (avoid scope creep)
- No external pharmacy APIs.
- No long-term memory / user sessions on server.
- No agent frameworks (LangChain, etc.).
- No fancy UI/animations; focus on clarity and tool transparency.
