/**
 * ChatPage Component
 * 
 * The main chat interface that combines all chat-related components.
 * 
 * MOCK vs LIVE MODE:
 * - By default, uses the real backend (useChatStream).
 * - Set VITE_USE_MOCK_STREAM=true in .env to use mock mode (useMockChatStream).
 * - A toggle button in the header allows switching at runtime for testing.
 * 
 * Layout:
 * - Header: App title, mode badge, and controls
 * - Main area: Message list + Tool events panel
 * - Footer: Message input
 */

import { useState } from 'react';
import { useMockChatStream } from '../hooks/useMockChatStream';
import { useChatStream } from '../hooks/useChatStream';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ToolEventList } from './ToolEventList';
import './ChatPage.css';

// Check environment variable for default mode
// If VITE_USE_MOCK_STREAM is 'true', default to mock mode
const defaultUseMock = import.meta.env.VITE_USE_MOCK_STREAM === 'true';

export function ChatPage() {
  // Allow runtime toggle between mock and live mode
  const [useMock, setUseMock] = useState(defaultUseMock);
  
  // Use the appropriate hook based on mode
  // Note: Both hooks have the same interface, so we can use them interchangeably
  const mockHook = useMockChatStream();
  const liveHook = useChatStream();
  
  // Select the active hook
  const { 
    messages, 
    toolEvents, 
    isStreaming, 
    error,
    sendMessage,
    clearMessages,
  } = useMock ? mockHook : liveHook;
  
  // Toggle between mock and live mode
  const toggleMode = () => {
    // Clear messages when switching modes to avoid confusion
    clearMessages();
    setUseMock(!useMock);
  };
  
  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="header-icon">💊</span>
            Pharmacy Assistant
          </h1>
          <button 
            className={`mode-badge ${useMock ? 'mock' : 'live'}`}
            onClick={toggleMode}
            disabled={isStreaming}
            title={`Click to switch to ${useMock ? 'Live' : 'Mock'} mode`}
          >
            {useMock ? '🔶 Mock' : '🟢 Live'}
          </button>
        </div>
        {messages.length > 0 && (
          <button 
            className="clear-button"
            onClick={clearMessages}
            disabled={isStreaming}
          >
            Clear Chat
          </button>
        )}
      </header>
      
      {/* Main chat area */}
      <main className="chat-main">
        <div className="chat-content">
          <MessageList messages={messages} />
          
          {/* Tool events panel (collapsible) */}
          <ToolEventList toolEvents={toolEvents} />
        </div>
      </main>
      
      {/* Error display */}
      {error && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      {/* Message input */}
      <footer className="chat-footer">
        <MessageInput 
          onSend={sendMessage}
          disabled={isStreaming}
          placeholder={isStreaming ? 'Assistant is typing...' : 'Type your message...'}
        />
      </footer>
    </div>
  );
}
