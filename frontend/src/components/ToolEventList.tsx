/**
 * ToolEventList Component
 * 
 * Displays a collapsible panel showing all tool calls and their results.
 * This helps users understand what the assistant is doing behind the scenes.
 */

import { useState } from 'react';
import { ToolEvents } from '../types/chat';
import { ToolEventCard } from './ToolEventCard';
import './ToolEventList.css';

interface ToolEventListProps {
  toolEvents: ToolEvents;
}

export function ToolEventList({ toolEvents }: ToolEventListProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  
  // Don't render if there are no tool calls
  if (toolEvents.calls.length === 0) {
    return null;
  }
  
  return (
    <div className="tool-event-list">
      <button 
        className="tool-list-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="header-icon">🔧</span>
        <span className="header-title">
          Tool Activity ({toolEvents.calls.length})
        </span>
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>
          ▼
        </span>
      </button>
      
      {isExpanded && (
        <div className="tool-list-content">
          {toolEvents.calls.map(call => {
            const result = toolEvents.results.find(
              r => r.toolCallId === call.id
            );
            return (
              <ToolEventCard 
                key={call.id} 
                call={call} 
                result={result}
              />
            );
          })}
        </div>
      )}
    </div>
  );
}

