/**
 * Chat-related TypeScript types for the Pharmacy Assistant.
 * 
 * These types model the SSE events from the backend and the UI state.
 */

// ============================================================
// SSE Stream Event Types (from backend /api/chat)
// ============================================================

/**
 * A single text token being streamed from the assistant.
 * Multiple of these build up the full response.
 */
export interface AssistantTokenEvent {
  type: 'assistant_token';
  content: string;
}

/**
 * Emitted when the assistant decides to call a tool.
 * Shows which tool and with what arguments.
 */
export interface ToolCallEvent {
  type: 'tool_call';
  tool_call_id: string;
  name: string;
  arguments: Record<string, unknown>;
}

/**
 * Emitted after a tool has been executed.
 * Contains the result or error from the tool.
 */
export interface ToolResultEvent {
  type: 'tool_result';
  tool_call_id: string;
  name: string;
  success: boolean;
  result?: unknown;
  error?: { code: string; message: string };
}

/**
 * Emitted when the assistant has finished responding.
 * Contains the complete response and trace of tool operations.
 */
export interface FinalMessageEvent {
  type: 'final_message';
  content: string;
  tool_calls: Array<{
    id: string;
    name: string;
    arguments: Record<string, unknown>;
  }>;
  tool_results: Array<{
    tool_call_id: string;
    name: string;
    success: boolean;
    result?: unknown;
    error?: { code: string; message: string };
  }>;
}

/**
 * Emitted when an error occurs during processing.
 */
export interface ErrorEvent {
  type: 'error';
  message: string;
  code?: string;
}

/**
 * Union type of all possible SSE stream events.
 */
export type StreamEvent =
  | AssistantTokenEvent
  | ToolCallEvent
  | ToolResultEvent
  | FinalMessageEvent
  | ErrorEvent;

// ============================================================
// UI State Types
// ============================================================

/**
 * Role of a message in the conversation.
 */
export type Role = 'user' | 'assistant' | 'system';

/**
 * A single message in the chat conversation.
 */
export interface ChatMessage {
  /** Unique identifier for this message */
  id: string;
  /** Who sent this message */
  role: Role;
  /** The text content of the message */
  content: string;
  /** If this is an assistant message with tool calls, link them */
  toolCallIds?: string[];
  /** Timestamp of when the message was created */
  timestamp: Date;
}

/**
 * Display data for a tool call in the UI.
 */
export interface ToolCallDisplay {
  /** The unique ID of this tool call (from backend) */
  id: string;
  /** Name of the tool being called */
  name: string;
  /** Arguments passed to the tool */
  arguments: Record<string, unknown>;
  /** Current status of this tool call */
  status: 'pending' | 'success' | 'error';
}

/**
 * Display data for a tool result in the UI.
 */
export interface ToolResultDisplay {
  /** The tool_call_id this result corresponds to */
  toolCallId: string;
  /** Name of the tool */
  name: string;
  /** Whether the tool succeeded */
  success: boolean;
  /** The result data if successful */
  result?: unknown;
  /** Error information if failed */
  error?: { code: string; message: string };
}

/**
 * Combined tool events for display.
 */
export interface ToolEvents {
  calls: ToolCallDisplay[];
  results: ToolResultDisplay[];
}

/**
 * State returned by the chat hook.
 */
export interface ChatState {
  /** All messages in the conversation */
  messages: ChatMessage[];
  /** Tool events for the current/recent turn */
  toolEvents: ToolEvents;
  /** Whether the assistant is currently streaming a response */
  isStreaming: boolean;
  /** Current error message, if any */
  error: string | null;
}

