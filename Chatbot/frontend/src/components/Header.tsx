import React from 'react';
import { ViewType } from '../types';

interface HeaderProps {
  onToggleSidebar: () => void;
  currentView: ViewType;
  onViewChange: (view: ViewType) => void;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar, currentView, onViewChange }) => {
  return (
    <header className="header">
      <div className="header-left">
        <button className="hamburger-btn" onClick={onToggleSidebar} aria-label="Toggle sidebar">
          ☰
        </button>
        <div>
          <h1 className="header-title">RAG Chatbot</h1>
          <p className="header-subtitle">AI-powered document chat assistant</p>
        </div>
      </div>
      
      <div className="header-right">
        <nav className="nav-tabs">
          <button
            className={`nav-tab ${currentView === 'chat' ? 'active' : ''}`}
            onClick={() => onViewChange('chat')}
          >
            💬 Chat
          </button>
          <button
            className={`nav-tab ${currentView === 'upload' ? 'active' : ''}`}
            onClick={() => onViewChange('upload')}
          >
            📎 Upload
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
