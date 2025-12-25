# Pharmacy Assistant Frontend

## Overview

This is the React frontend for the Pharmacy Assistant chat application. It provides a chat interface where users can interact with the pharmacy assistant to check medication availability, manage prescriptions, and get information about medications.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`.

## Current Status: Mock Mode

**Important:** This version uses a mock streaming hook (`useMockChatStream`) instead of connecting to the real backend. This allows UI development and testing without needing the backend running.

In **Milestone 5**, we will replace the mock hook with a real SSE client that connects to `POST /api/chat`.

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
│   │   └── useMockChatStream.ts  # Mock streaming hook (replaced in Milestone 5)
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
- Header with title and "Clear Chat" button
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

## How the Mock Streaming Hook Works

`useMockChatStream` simulates the backend's SSE behavior:

1. When `sendMessage(text)` is called:
   - Adds user message to state
   - Selects a mock scenario based on keywords in the message
   - Creates a sequence of mock `StreamEvent` objects

2. Events are "streamed" with 50ms delays between each:
   - `tool_call` → Adds to toolEvents.calls
   - `tool_result` → Updates call status, adds to toolEvents.results
   - `assistant_token` → Accumulates in the assistant message
   - `final_message` → Finalizes the message, stops streaming

3. Mock scenarios:
   - **Stock check**: Keywords "stock", "available", "aspirin"
   - **Hebrew stock**: Keywords "מלאי", "אספירין"
   - **Prescription refill**: Keywords "refill", "prescription"
   - **Default**: Safety refusal (no tools, redirects to pharmacist)

## Styling

- Uses plain CSS (no Tailwind or CSS-in-JS)
- CSS files are co-located with components
- Color scheme: Blue (#4A90D9) for user messages, light gray for assistant
- Font stack includes Hebrew fonts (Heebo, Assistant, Rubik)
- `dir="auto"` enables automatic RTL for Hebrew text

## Next Steps (Milestone 5)

In the next milestone, we will:
1. Create `src/hooks/useChatStream.ts` - Real SSE client
2. Connect to `POST /api/chat` using fetch streaming
3. Parse SSE events and update state
4. Replace `useMockChatStream` with `useChatStream` in ChatPage

