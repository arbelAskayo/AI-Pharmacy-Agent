/**
 * Real Chat Stream Hook
 * 
 * This hook connects to the backend's SSE endpoint (POST /api/chat)
 * and handles real-time streaming of assistant responses.
 * 
 * HOW IT WORKS:
 * 1. When sendMessage() is called, it adds the user message to the conversation.
 * 2. It sends a POST request to /api/chat with the full message history.
 * 3. It reads the SSE stream using fetch() + ReadableStream.
 * 4. For each SSE event, it updates the UI state accordingly.
 * 
 * SSE FORMAT:
 * Each event is a line: "data: {json}\n\n"
 * Event types: tool_call, tool_result, assistant_token, final_message, error
 */

import { useState, useCallback, useRef } from 'react';
import {
  ChatMessage,
  ToolCallDisplay,
  ToolEvents,
  StreamEvent,
} from '../types/chat';

// ============================================================
// Configuration
// ============================================================

/**
 * Get the API base URL.
 * 
 * In development, we use a relative URL so the Vite proxy can forward
 * requests to the backend. This avoids CORS issues.
 * 
 * In production or if VITE_API_BASE_URL is explicitly set, we use
 * the configured URL.
 */
const getApiBaseUrl = (): string => {
  // If explicitly set in env, use that
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // In development, use relative URL for Vite proxy
  if (import.meta.env.DEV) {
    return ''; // Relative URL, Vite proxy handles /api/*
  }
  
  // Default fallback
  return 'http://127.0.0.1:8000';
};

// Check if we're in development mode for debug logging
const isDev = import.meta.env.DEV;

// ============================================================
// Helper: Generate unique IDs
// ============================================================
let idCounter = 0;
const generateId = (prefix: string = 'msg'): string => {
  idCounter += 1;
  return `${prefix}_${Date.now()}_${idCounter}`;
};

// ============================================================
// SSE Parser
// ============================================================

/**
 * Parse a single SSE data line into a StreamEvent.
 * Returns null if parsing fails or line is empty/comment.
 */
function parseSSELine(line: string): StreamEvent | null {
  // Ignore empty lines and comments
  if (!line || line.startsWith(':')) {
    return null;
  }
  
  // SSE data lines start with "data: "
  if (!line.startsWith('data: ')) {
    return null;
  }
  
  const jsonStr = line.slice(6); // Remove "data: " prefix
  
  try {
    const event = JSON.parse(jsonStr) as StreamEvent;
    
    if (isDev) {
      console.log('[SSE Event]', event.type, event);
    }
    
    return event;
  } catch (err) {
    console.error('[SSE Parse Error]', err, 'Line:', line);
    return null;
  }
}

// ============================================================
// The Hook
// ============================================================

export interface UseChatStreamReturn {
  messages: ChatMessage[];
  toolEvents: ToolEvents;
  isStreaming: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
  clearMessages: () => void;
}

export function useChatStream(): UseChatStreamReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [toolEvents, setToolEvents] = useState<ToolEvents>({ calls: [], results: [] });
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Ref to track the current assistant message ID during streaming
  const currentAssistantIdRef = useRef<string | null>(null);
  // Ref to track accumulated tool call IDs for the current turn
  const currentToolCallIdsRef = useRef<string[]>([]);
  // Ref to abort ongoing requests
  const abortControllerRef = useRef<AbortController | null>(null);
  
  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isStreaming) return;
    
    // Clear any previous error
    setError(null);
    
    // Add user message
    const userMessage: ChatMessage = {
      id: generateId('user'),
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    };
    
    // Update messages with the new user message
    setMessages(prev => [...prev, userMessage]);
    
    // Clear previous tool events for new turn
    setToolEvents({ calls: [], results: [] });
    currentToolCallIdsRef.current = [];
    
    // Create placeholder for assistant message
    const assistantMessageId = generateId('assistant');
    currentAssistantIdRef.current = assistantMessageId;
    
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      toolCallIds: [],
    };
    setMessages(prev => [...prev, assistantMessage]);
    
    setIsStreaming(true);
    
    // Build request body
    // Get current messages including the new user message for the API call
    const apiMessages = [...messages, userMessage].map(msg => ({
      role: msg.role,
      content: msg.content,
    }));
    
    // Create abort controller for this request
    abortControllerRef.current = new AbortController();
    
    try {
      const baseUrl = getApiBaseUrl();
      const url = `${baseUrl}/api/chat`;
      
      if (isDev) {
        console.log('[Chat Request]', url, { messages: apiMessages });
      }
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'text/event-stream',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: apiMessages }),
        signal: abortControllerRef.current.signal,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      if (!response.body) {
        throw new Error('No response body');
      }
      
      // Read the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';
      
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Split buffer by double newlines (SSE event separator)
        const parts = buffer.split('\n\n');
        
        // Keep the last incomplete part in the buffer
        buffer = parts.pop() || '';
        
        // Process complete events
        for (const part of parts) {
          // Each part may have multiple lines, but we only care about "data:" lines
          const lines = part.split('\n');
          
          for (const line of lines) {
            const event = parseSSELine(line);
            
            if (!event) continue;
            
            switch (event.type) {
              case 'tool_call':
                // Add tool call to display
                const toolCall: ToolCallDisplay = {
                  id: event.tool_call_id,
                  name: event.name,
                  arguments: event.arguments,
                  status: 'pending',
                };
                currentToolCallIdsRef.current.push(event.tool_call_id);
                setToolEvents(prev => ({
                  ...prev,
                  calls: [...prev.calls, toolCall],
                }));
                break;
                
              case 'tool_result':
                // Update tool call status and add result
                setToolEvents(prev => ({
                  calls: prev.calls.map(tc =>
                    tc.id === event.tool_call_id
                      ? { ...tc, status: event.success ? 'success' : 'error' }
                      : tc
                  ),
                  results: [...prev.results, {
                    toolCallId: event.tool_call_id,
                    name: event.name,
                    success: event.success,
                    result: event.result,
                    error: event.error,
                  }],
                }));
                break;
                
              case 'assistant_token':
                // Accumulate content and update message
                accumulatedContent += event.content;
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { ...msg, content: accumulatedContent }
                      : msg
                  )
                );
                break;
                
              case 'final_message':
                // Finalize the message with complete content and tool call IDs
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { 
                          ...msg, 
                          content: event.content, 
                          toolCallIds: currentToolCallIdsRef.current 
                        }
                      : msg
                  )
                );
                setIsStreaming(false);
                currentAssistantIdRef.current = null;
                break;
                
              case 'error':
                // Handle error event
                setError(event.message);
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === assistantMessageId
                      ? { 
                          ...msg, 
                          content: `Error: ${event.message}` 
                        }
                      : msg
                  )
                );
                setIsStreaming(false);
                currentAssistantIdRef.current = null;
                break;
            }
          }
        }
      }
      
      // If we reach here without a final_message, ensure streaming is stopped
      if (isStreaming) {
        setIsStreaming(false);
        currentAssistantIdRef.current = null;
      }
      
    } catch (err) {
      // Handle fetch errors
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      
      // Don't show error for aborted requests
      if (err instanceof Error && err.name === 'AbortError') {
        console.log('[Chat Request] Aborted');
        return;
      }
      
      console.error('[Chat Request Error]', err);
      setError(`Failed to connect: ${errorMessage}`);
      
      // Update the assistant message with error
      if (currentAssistantIdRef.current) {
        setMessages(prev =>
          prev.map(msg =>
            msg.id === currentAssistantIdRef.current
              ? { ...msg, content: `Sorry, I couldn't connect to the server. Please try again.` }
              : msg
          )
        );
      }
      
      setIsStreaming(false);
      currentAssistantIdRef.current = null;
    }
  }, [isStreaming, messages]);
  
  const clearMessages = useCallback(() => {
    // Abort any ongoing request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    setMessages([]);
    setToolEvents({ calls: [], results: [] });
    setError(null);
    setIsStreaming(false);
    currentAssistantIdRef.current = null;
    currentToolCallIdsRef.current = [];
  }, []);
  
  return {
    messages,
    toolEvents,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
  };
}

