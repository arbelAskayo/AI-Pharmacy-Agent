/**
 * MessageBubble Component
 * 
 * Renders a single chat message with appropriate styling based on the role.
 * - User messages: aligned right, blue background
 * - Assistant messages: aligned left, gray background
 * 
 * Supports Hebrew text with automatic direction detection.
 */

import { ChatMessage } from '../types/chat';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-bubble-container ${isUser ? 'user' : 'assistant'}`}>
      <div className={`message-bubble ${isUser ? 'user' : 'assistant'}`}>
        {/* Role label */}
        <div className="message-role">
          {isUser ? 'You' : 'Pharmacy Assistant'}
        </div>
        
        {/* Message content with auto text direction for Hebrew support */}
        <div className="message-content" dir="auto">
          {message.content || (
            <span className="streaming-indicator">●●●</span>
          )}
        </div>
        
        {/* Timestamp */}
        <div className="message-time">
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
}

