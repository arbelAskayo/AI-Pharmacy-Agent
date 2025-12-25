/**
 * ToolEventCard Component
 * 
 * Displays a single tool call with its result.
 * Shows the tool name, arguments, status, and result/error.
 */

import { ToolCallDisplay, ToolResultDisplay } from '../types/chat';
import './ToolEventCard.css';

interface ToolEventCardProps {
  call: ToolCallDisplay;
  result?: ToolResultDisplay;
}

export function ToolEventCard({ call, result }: ToolEventCardProps) {
  // Determine status icon and class
  const getStatusInfo = () => {
    if (call.status === 'pending') {
      return { icon: '⏳', className: 'pending', label: 'Running...' };
    }
    if (call.status === 'success') {
      return { icon: '✓', className: 'success', label: 'Success' };
    }
    return { icon: '✗', className: 'error', label: 'Error' };
  };
  
  const statusInfo = getStatusInfo();
  
  // Format tool name for display (e.g., "check_medication_stock" -> "Check Medication Stock")
  const formatToolName = (name: string): string => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };
  
  // Format arguments for display
  const formatArguments = (args: Record<string, unknown>): string => {
    return Object.entries(args)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join(', ');
  };
  
  return (
    <div className={`tool-event-card ${statusInfo.className}`}>
      <div className="tool-header">
        <span className="tool-icon">🔧</span>
        <span className="tool-name">{formatToolName(call.name)}</span>
        <span className={`tool-status ${statusInfo.className}`}>
          {statusInfo.icon} {statusInfo.label}
        </span>
      </div>
      
      <div className="tool-arguments">
        <span className="label">Input:</span>
        <code>{formatArguments(call.arguments)}</code>
      </div>
      
      {result && result.success && result.result !== undefined && (
        <div className="tool-result">
          <span className="label">Result:</span>
          <pre>{JSON.stringify(result.result, null, 2)}</pre>
        </div>
      )}
      
      {result && !result.success && result.error && (
        <div className="tool-error">
          <span className="label">Error:</span>
          <code>{result.error.message || 'Unknown error'}</code>
        </div>
      )}
    </div>
  );
}

