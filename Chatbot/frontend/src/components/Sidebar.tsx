import React from 'react';
import { Document as ChatDocument } from '../types';

interface SidebarProps {
  isOpen: boolean;
  documents: ChatDocument[];
  onRemoveDocument: (documentId: string) => void;
  onClearChat: () => void;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  documents,
  onRemoveDocument,
  onClearChat,
  onClose,
}) => {
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2 className="sidebar-title">Menu</h2>
        <button className="close-btn" onClick={onClose} aria-label="Close sidebar">
          ×
        </button>
      </div>
      
      <div className="sidebar-content">
        <div className="sidebar-section">
          <h3>Documents ({documents.length})</h3>
          {documents.length === 0 ? (
            <p style={{ color: '#666', fontSize: '14px', fontStyle: 'italic' }}>
              No documents uploaded yet
            </p>
          ) : (
            <ul className="document-list">
              {documents.map((doc) => (
                <li key={doc.id} className="document-item">
                  <div className="document-info">
                    <div className="document-name" title={doc.name}>
                      {doc.name.length > 25 ? `${doc.name.substring(0, 25)}...` : doc.name}
                    </div>
                    <div className="document-meta">
                      {formatFileSize(doc.size)} • {formatDate(doc.uploadedAt)}
                    </div>
                    <div className="document-meta">
                      Status: <span style={{ 
                        color: doc.status === 'processed' ? '#28a745' : 
                               doc.status === 'error' ? '#dc3545' : '#ffc107',
                        fontWeight: 500 
                      }}>
                        {doc.status}
                      </span>
                    </div>
                  </div>
                  <button
                    className="remove-doc-btn"
                    onClick={() => onRemoveDocument(doc.id)}
                    aria-label={`Remove ${doc.name}`}
                    title="Remove document"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <div className="sidebar-section">
          <h3>Actions</h3>
          <button 
            className="clear-chat-btn"
            onClick={onClearChat}
            title="Clear all chat messages"
          >
            🗑️ Clear Chat History
          </button>
        </div>
        
        <div className="sidebar-section">
          <h3>About</h3>
          <p style={{ fontSize: '12px', color: '#666', lineHeight: 1.4 }}>
            RAG Chatbot uses Retrieval-Augmented Generation to provide accurate answers 
            based on your uploaded documents. Upload PDFs, Word docs, or text files to get started.
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
