/**
 * MessageInput Component
 * 
 * A text input with send button for composing new messages.
 * - Supports Enter to send (Shift+Enter for new line)
 * - Disables input while streaming
 * - Auto-resizes textarea
 */

import { useState, useRef, useEffect, KeyboardEvent, FormEvent } from 'react';
import './MessageInput.css';

interface MessageInputProps {
  onSend: (text: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({ 
  onSend, 
  disabled = false,
  placeholder = 'Type your message...'
}: MessageInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-resize textarea based on content
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [text]);
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText('');
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };
  
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  return (
    <form className="message-input-container" onSubmit={handleSubmit}>
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          dir="auto"
          className="message-textarea"
        />
        <button 
          type="submit" 
          disabled={disabled || !text.trim()}
          className="send-button"
          title="Send message"
        >
          {disabled ? (
            <span className="loading-spinner">⏳</span>
          ) : (
            <span className="send-icon">➤</span>
          )}
        </button>
      </div>
      <div className="input-hint">
        Press Enter to send, Shift+Enter for new line
      </div>
    </form>
  );
}

