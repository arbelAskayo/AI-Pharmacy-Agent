/**
 * App Component
 * 
 * Root component that renders the ChatPage.
 * This is the main entry point for the React application.
 */

import { ChatPage } from './components/ChatPage';
import './App.css';

function App() {
  return (
    <div className="app">
      <ChatPage />
    </div>
  );
}

export default App;

