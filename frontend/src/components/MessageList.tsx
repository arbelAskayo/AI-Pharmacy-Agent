/**
 * MessageList Component
 * 
 * Renders the scrollable list of chat messages.
 * Auto-scrolls to the bottom when new messages arrive.
 */

import { useEffect, useRef } from 'react';
import { ChatMessage } from '../types/chat';
import { MessageBubble } from './MessageBubble';
import './MessageList.css';

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  if (messages.length === 0) {
    return (
      <div className="message-list empty">
        <div className="empty-state">
          <div className="empty-icon">💊</div>
          <h3>Welcome to Pharmacy Assistant</h3>
          <p>Ask me about medications, check stock availability, or manage your prescriptions.</p>
          <div className="example-prompts">
            <p><strong>Try asking:</strong></p>
            <ul>
              <li>"Is aspirin in stock?"</li>
              <li>"I need to refill my prescription"</li>
              <li>"האם יש לכם אספירין במלאי?"</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="message-list">
      {messages.map(message => (
        <MessageBubble key={message.id} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

