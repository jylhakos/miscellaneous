import React from 'react';
import { ChatMessage } from '../types';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading,
}) => {
  const [inputMessage, setInputMessage] = React.useState('');
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputMessage.trim() && !isLoading) {
      onSendMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatTimestamp = (timestamp: Date): string => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.type === 'user';
    
    return (
      <div key={message.id} className={`message ${isUser ? 'user' : 'assistant'}`}>
        <div className="message-content">
          <div className="message-header">
            <span className="message-sender">
              {isUser ? '👤 You' : '🤖 Assistant'}
            </span>
            <span className="message-time">
              {formatTimestamp(message.timestamp)}
            </span>
          </div>
          
          <div className="message-text">
            {message.content.split('\n').map((line, index) => (
              <React.Fragment key={index}>
                {line}
                {index < message.content.split('\n').length - 1 && <br />}
              </React.Fragment>
            ))}
          </div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="message-sources">
              <div className="sources-header">📚 Sources:</div>
              <ul className="sources-list">
                {message.sources.map((source, index) => (
                  <li key={index} className="source-item">
                    <span className="source-name">{source.name}</span>
                    {source.page && (
                      <span className="source-page"> (page {source.page})</span>
                    )}
                    {source.relevanceScore && (
                      <span className="source-score">
                        {Math.round(source.relevanceScore * 100)}% match
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {message.error && (
            <div className="message-error">
              ⚠️ Error: {message.error}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">💬</div>
            <h3>Welcome to RAG Chatbot!</h3>
            <p>
              Start by uploading some documents, then ask questions about their content.
              I'll use the information from your documents to provide accurate answers.
            </p>
            <div className="sample-questions">
              <h4>Try asking questions like:</h4>
              <ul>
                <li>"What are the main topics in these documents?"</li>
                <li>"Can you summarize the key points?"</li>
                <li>"How does [concept A] relate to [concept B]?"</li>
              </ul>
            </div>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="message-header">
                <span className="message-sender">🤖 Assistant</span>
                <span className="message-time">now</span>
              </div>
              <div className="message-text">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your documents..."
            disabled={isLoading}
            rows={1}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
            title="Send message (Enter)"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </div>
        <div className="input-hint">
          Press Enter to send • Shift+Enter for new line
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
