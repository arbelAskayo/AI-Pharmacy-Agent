# Pharmacy Assistant Frontend

## Overview

This is the React frontend for the Pharmacy Assistant chat application. It provides a chat interface where users can interact with the pharmacy assistant to check medication availability, manage prescriptions, and get information about medications.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server (Live mode - connects to backend)
npm run dev

# Start in Mock mode (no backend needed)
VITE_USE_MOCK_STREAM=true npm run dev
```

The app will be available at `http://localhost:5173`.

## Mock vs Live Mode

The frontend supports two modes:

### Live Mode (Default)
- Connects to the real backend at `POST /api/chat`
- Requires the backend to be running with a valid OpenAI API key
- Shows real tool calls and streaming responses

### Mock Mode
- Uses simulated responses (no backend needed)
- Great for UI development and testing
- Responds to keywords like "stock", "aspirin", "refill"

### How to Switch Modes

**Option 1: Environment Variable**
```bash
# Mock mode
VITE_USE_MOCK_STREAM=true npm run dev

# Live mode (default)
npm run dev
```

**Option 2: Runtime Toggle**
Click the mode badge in the header (🔶 Mock / 🟢 Live) to switch at runtime.

## Running End-to-End (Live Mode)

1. **Start the backend** (in the `backend/` directory):
   ```bash
   cd backend
   source .venv/bin/activate  # or create venv if needed
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   Make sure `OPENAI_API_KEY` is set in `backend/.env`.

2. **Start the frontend** (in the `frontend/` directory):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open the app**: http://localhost:5173

4. **Test queries**:
   - "Do you have ibuprofen in stock?" → Tool call + streamed response
   - "Should I take aspirin for my headache?" → Safety refusal (no tools)
   - "יש לכם אספירין במלאי?" → Hebrew response with tool calls

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point - mounts React app
│   ├── App.tsx               # Root component
│   ├── App.css               # App-level styles
│   ├── index.css             # Global styles & CSS reset
│   │
│   ├── types/
│   │   └── chat.ts           # TypeScript interfaces for chat types
│   │
│   ├── hooks/
│   │   ├── useChatStream.ts      # Real SSE client (Live mode)
│   │   └── useMockChatStream.ts  # Mock streaming (Mock mode)
│   │
│   └── components/
│       ├── ChatPage.tsx      # Main chat page layout
│       ├── ChatPage.css
│       ├── MessageList.tsx   # Scrollable message list
│       ├── MessageList.css
│       ├── MessageBubble.tsx # Individual message bubble
│       ├── MessageBubble.css
│       ├── MessageInput.tsx  # Text input with send button
│       ├── MessageInput.css
│       ├── ToolEventList.tsx # Collapsible tool activity panel
│       ├── ToolEventList.css
│       ├── ToolEventCard.tsx # Single tool call/result card
│       └── ToolEventCard.css
│
├── package.json              # Dependencies and scripts
├── tsconfig.json             # TypeScript configuration
├── vite.config.ts            # Vite build configuration
├── index.html                # HTML template
└── .env.example              # Environment variables template
```

## Key Components

### ChatPage
The main container that orchestrates all chat components:
- Header with title, mode toggle, and "Clear Chat" button
- Message list area (scrollable)
- Tool events panel (collapsible, shows tool calls and results)
- Message input footer

### MessageList
Renders the conversation as a scrollable list of `MessageBubble` components. Auto-scrolls to bottom when new messages arrive. Shows an empty state with example prompts when no messages exist.

### MessageBubble
Displays a single message with:
- Role label (You / Pharmacy Assistant)
- Message content (with `dir="auto"` for Hebrew support)
- Timestamp

### ToolEventList & ToolEventCard
Shows the "behind the scenes" activity:
- Which tools were called
- What arguments were passed
- Success/error status
- Result data (JSON formatted)

### MessageInput
Text input with:
- Auto-resizing textarea
- Enter to send (Shift+Enter for new line)
- Disabled state during streaming
- Send button with loading indicator

## Hooks

### useChatStream (Live Mode)

Connects to the real backend via SSE:

```typescript
const { messages, toolEvents, isStreaming, error, sendMessage, clearMessages } = useChatStream();
```

**How it works:**
1. `sendMessage(text)` adds a user message and sends POST to `/api/chat`
2. Reads the SSE stream using `fetch()` + `ReadableStream`
3. Parses `data: {json}\n\n` lines and dispatches to state
4. Handles: `tool_call`, `tool_result`, `assistant_token`, `final_message`, `error`

**Configuration:**
- `VITE_API_BASE_URL`: Backend URL (default: `http://127.0.0.1:8000`)

### useMockChatStream (Mock Mode)

Simulates backend behavior for offline development:

```typescript
const { messages, toolEvents, isStreaming, error, sendMessage, clearMessages } = useMockChatStream();
```

**Mock scenarios:**
- Keywords "stock", "available", "aspirin" → Stock check flow
- Keywords "מלאי", "אספירין" → Hebrew stock check
- Keywords "refill", "prescription" → Prescription refill flow
- Default → Safety refusal

## TypeScript Types

All types are defined in `src/types/chat.ts`:

### Stream Events (from backend)
- `AssistantTokenEvent` - Single streamed token
- `ToolCallEvent` - Tool being called
- `ToolResultEvent` - Tool execution result
- `FinalMessageEvent` - Complete response
- `ErrorEvent` - Error occurred

### UI State
- `ChatMessage` - A message in the conversation
- `ToolCallDisplay` - Tool call for UI display
- `ToolResultDisplay` - Tool result for UI display
- `ToolEvents` - Combined calls and results

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://127.0.0.1:8000` |
| `VITE_USE_MOCK_STREAM` | Use mock mode if `true` | `false` |

## Styling

- Uses plain CSS (no Tailwind or CSS-in-JS)
- CSS files are co-located with components
- Color scheme: Blue (#4A90D9) for user messages, light gray for assistant
- Font stack includes Hebrew fonts (Heebo, Assistant, Rubik)
- `dir="auto"` enables automatic RTL for Hebrew text

## Debugging

In development mode (`npm run dev`), the `useChatStream` hook logs SSE events to the console:
```
[SSE Event] tool_call { type: 'tool_call', tool_call_id: '...', name: '...', arguments: {...} }
[SSE Event] tool_result { type: 'tool_result', ... }
[SSE Event] assistant_token { type: 'assistant_token', content: '...' }
```

Check the browser's Network tab to see the raw SSE stream from `/api/chat`.
