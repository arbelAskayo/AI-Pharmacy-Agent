/**
 * ChatPage Component
 * 
 * The main chat interface that combines all chat-related components.
 * Layout:
 * - Header: App title and mock indicator
 * - Main area: Message list + Tool events panel
 * - Footer: Message input
 */

import { useMockChatStream } from '../hooks/useMockChatStream';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ToolEventList } from './ToolEventList';
import './ChatPage.css';

export function ChatPage() {
  const { 
    messages, 
    toolEvents, 
    isStreaming, 
    error,
    sendMessage,
    clearMessages,
  } = useMockChatStream();
  
  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="header-icon">💊</span>
            Pharmacy Assistant
          </h1>
          <span className="mock-badge">Mock UI</span>
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

