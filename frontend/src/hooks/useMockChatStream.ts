/**
 * Mock Chat Stream Hook
 * 
 * This hook simulates the SSE streaming behavior of the real /api/chat endpoint.
 * It's used during development to test the UI without needing the backend running.
 * 
 * HOW IT WORKS:
 * 1. When sendMessage() is called, it adds the user message to the messages array.
 * 2. It then simulates a sequence of StreamEvents using setTimeout delays:
 *    - tool_call events (if applicable)
 *    - tool_result events (if applicable)
 *    - assistant_token events (building up the response character by character)
 *    - final_message event (marking the response as complete)
 * 3. The hook updates its state as each event "arrives", mimicking real streaming.
 * 
 * MOCK SCENARIOS:
 * - "stock" or "מלאי" keywords → Stock check flow with tool calls
 * - "refill" or "מילוי" keywords → Prescription refill flow with tool calls
 * - Default (including medical advice) → Safety refusal without tools
 */

import { useState, useCallback } from 'react';
import {
  ChatMessage,
  ToolCallDisplay,
  ToolEvents,
  StreamEvent,
} from '../types/chat';

// ============================================================
// Helper: Generate unique IDs
// ============================================================
let idCounter = 0;
const generateId = (prefix: string = 'msg'): string => {
  idCounter += 1;
  return `${prefix}_${Date.now()}_${idCounter}`;
};

// ============================================================
// Mock Event Sequences
// ============================================================

/**
 * Mock scenario: Stock availability check
 * Simulates checking if aspirin is in stock
 */
const createStockCheckEvents = (): StreamEvent[] => {
  const toolCallId = generateId('call');
  return [
    {
      type: 'tool_call',
      tool_call_id: toolCallId,
      name: 'check_medication_stock',
      arguments: { medication_name: 'Aspirin' },
    },
    {
      type: 'tool_result',
      tool_call_id: toolCallId,
      name: 'check_medication_stock',
      success: true,
      result: {
        medication_name: 'Aspirin',
        medication_name_he: 'אספירין',
        branches: [
          { branch: 'Main Street', quantity: 150, available: true },
          { branch: 'Downtown', quantity: 25, available: true },
          { branch: 'Airport', quantity: 10, available: true },
        ],
        total_quantity: 185,
        any_available: true,
      },
    },
    // Stream the response tokens
    ...tokenizeResponse(
      'Yes, Aspirin is available in stock at all our branches:\n\n' +
      '• Main Street: 150 units\n' +
      '• Downtown: 25 units\n' +
      '• Airport: 10 units\n\n' +
      'Would you like me to help you with anything else?'
    ),
  ];
};

/**
 * Mock scenario: Prescription refill request
 * Simulates looking up a user and their prescriptions
 */
const createRefillFlowEvents = (): StreamEvent[] => {
  const userCallId = generateId('call');
  const rxCallId = generateId('call');
  return [
    {
      type: 'tool_call',
      tool_call_id: userCallId,
      name: 'get_user_profile',
      arguments: { phone: '050-1234567' },
    },
    {
      type: 'tool_result',
      tool_call_id: userCallId,
      name: 'get_user_profile',
      success: true,
      result: {
        id: 1,
        name: 'David Cohen',
        name_he: 'דוד כהן',
        phone: '050-1234567',
        email: 'david.cohen@email.com',
      },
    },
    {
      type: 'tool_call',
      tool_call_id: rxCallId,
      name: 'list_user_prescriptions',
      arguments: { user_id: 1, status: 'active' },
    },
    {
      type: 'tool_result',
      tool_call_id: rxCallId,
      name: 'list_user_prescriptions',
      success: true,
      result: {
        user_id: 1,
        user_name: 'David Cohen',
        prescriptions: [
          {
            prescription_id: 1,
            medication_name: 'Omeprazole',
            refills_remaining: 3,
            expiry_date: '2026-10-26',
            can_refill: true,
          },
        ],
        count: 1,
      },
    },
    // Stream the response tokens
    ...tokenizeResponse(
      'Hello David! I found your active prescription:\n\n' +
      '• Omeprazole - 3 refills remaining (expires Oct 2026)\n\n' +
      'Would you like me to submit a refill request for this prescription?'
    ),
  ];
};

/**
 * Mock scenario: Safety refusal (no tools)
 * Used when user asks for medical advice
 */
const createSafetyRefusalEvents = (): StreamEvent[] => {
  return tokenizeResponse(
    'I cannot provide medical advice. Please consult with our pharmacist or ' +
    'your doctor for guidance on medication choices and whether a specific ' +
    'medication is right for you.\n\n' +
    'However, I can help you with:\n' +
    '• Checking medication availability\n' +
    '• Looking up prescription information\n' +
    '• Processing refill requests\n\n' +
    'Is there anything else I can assist you with?'
  );
};

/**
 * Mock scenario: Hebrew stock check
 */
const createHebrewStockEvents = (): StreamEvent[] => {
  const toolCallId = generateId('call');
  return [
    {
      type: 'tool_call',
      tool_call_id: toolCallId,
      name: 'check_medication_stock',
      arguments: { medication_name: 'אספירין' },
    },
    {
      type: 'tool_result',
      tool_call_id: toolCallId,
      name: 'check_medication_stock',
      success: true,
      result: {
        medication_name: 'Aspirin',
        medication_name_he: 'אספירין',
        branches: [
          { branch: 'Main Street', quantity: 150, available: true },
          { branch: 'Downtown', quantity: 25, available: true },
        ],
        total_quantity: 175,
        any_available: true,
      },
    },
    ...tokenizeResponse(
      'כן, אספירין זמין במלאי בסניפים שלנו:\n\n' +
      '• סניף הראשי: 150 יחידות\n' +
      '• סניף דאון טאון: 25 יחידות\n\n' +
      'האם תרצה שאעזור לך עם משהו נוסף?'
    ),
  ];
};

/**
 * Convert a string into a sequence of assistant_token events + final_message.
 * Simulates token-by-token streaming.
 */
function tokenizeResponse(text: string): StreamEvent[] {
  const events: StreamEvent[] = [];
  
  // Split into "tokens" (words for simulation)
  const tokens = text.split(/(\s+)/);
  
  for (const token of tokens) {
    if (token) {
      events.push({
        type: 'assistant_token',
        content: token,
      });
    }
  }
  
  // Add final message
  events.push({
    type: 'final_message',
    content: text,
    tool_calls: [],
    tool_results: [],
  });
  
  return events;
}

/**
 * Select the appropriate mock scenario based on user message content.
 */
function selectMockScenario(userMessage: string): StreamEvent[] {
  const lowerMessage = userMessage.toLowerCase();
  
  // Hebrew stock check
  if (userMessage.includes('מלאי') || userMessage.includes('אספירין')) {
    return createHebrewStockEvents();
  }
  
  // English stock check
  if (lowerMessage.includes('stock') || lowerMessage.includes('available') || 
      lowerMessage.includes('aspirin')) {
    return createStockCheckEvents();
  }
  
  // Refill flow
  if (lowerMessage.includes('refill') || lowerMessage.includes('prescription') ||
      userMessage.includes('מילוי') || userMessage.includes('מרשם')) {
    return createRefillFlowEvents();
  }
  
  // Default: safety refusal (covers medical advice questions)
  return createSafetyRefusalEvents();
}

// ============================================================
// The Hook
// ============================================================

export interface UseMockChatStreamReturn {
  messages: ChatMessage[];
  toolEvents: ToolEvents;
  isStreaming: boolean;
  error: string | null;
  sendMessage: (text: string) => void;
  clearMessages: () => void;
}

export function useMockChatStream(): UseMockChatStreamReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [toolEvents, setToolEvents] = useState<ToolEvents>({ calls: [], results: [] });
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Ref to accumulate streaming content
  const [streamingContent, setStreamingContent] = useState('');
  
  const sendMessage = useCallback((text: string) => {
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
    setMessages(prev => [...prev, userMessage]);
    
    // Clear previous tool events for new turn
    setToolEvents({ calls: [], results: [] });
    setStreamingContent('');
    setIsStreaming(true);
    
    // Get the mock event sequence for this message
    const events = selectMockScenario(text);
    
    // Create a placeholder for the assistant message
    const assistantMessageId = generateId('assistant');
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      toolCallIds: [],
    };
    setMessages(prev => [...prev, assistantMessage]);
    
    // Simulate streaming events with delays
    let accumulatedContent = '';
    const toolCallIds: string[] = [];
    
    events.forEach((event, index) => {
      const delay = index * 50; // 50ms between events
      
      setTimeout(() => {
        switch (event.type) {
          case 'tool_call':
            // Add tool call to display
            const toolCall: ToolCallDisplay = {
              id: event.tool_call_id,
              name: event.name,
              arguments: event.arguments,
              status: 'pending',
            };
            toolCallIds.push(event.tool_call_id);
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
            // Finalize the message
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: event.content, toolCallIds }
                  : msg
              )
            );
            setIsStreaming(false);
            break;
            
          case 'error':
            setError(event.message);
            setIsStreaming(false);
            break;
        }
      }, delay);
    });
  }, [isStreaming]);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
    setToolEvents({ calls: [], results: [] });
    setError(null);
    setStreamingContent('');
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

