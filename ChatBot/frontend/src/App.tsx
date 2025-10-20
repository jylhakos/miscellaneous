import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import DocumentUpload from './components/DocumentUpload';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import LoadingSpinner from './components/LoadingSpinner';
import { ChatMessage, Document as ChatDocument } from './types';
import { sendMessage, uploadDocument, getDocuments, deleteDocument } from './api';
import './App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [documents, setDocuments] = useState<ChatDocument[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentView, setCurrentView] = useState<'chat' | 'upload'>('chat');

  useEffect(() => {
    // Add welcome message
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      text: 'Hello I\'m your RAG Chatbot assistant. Upload documents and ask me questions about their content.',
      sender: 'bot',
      timestamp: new Date(),
      confidence: 1.0
    };
    setMessages([welcomeMessage]);
    
    // Check API health on startup
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      await chatAPI.healthCheck();
      console.log('API is healthy');
    } catch (error) {
      console.error('API health check failed:', error);
      const errorMessage: ChatMessage = {
        id: 'api-error',
        text: 'Warning: Unable to connect to the backend API. Please check your connection.',
        sender: 'bot',
        timestamp: new Date(),
        confidence: 0.0,
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage(text);
      
      const botMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        text: response.answer,
        sender: 'bot',
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources?.map(source => ({
          content: source.content,
          metadata: source.metadata,
          similarity_score: source.similarity_score
        }))
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        text: 'Sorry, I encountered an error while processing your message. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        confidence: 0.0,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentUpload = async (files: File[]) => {
    setIsLoading(true);
    
    try {
      const response = await chatAPI.uploadDocuments(files);
      
      const newDocuments: ChatDocument[] = files.map((file, index) => ({
        id: `doc-${Date.now()}-${index}`,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadedAt: new Date(),
        status: 'processed'
      }));

      setDocuments(prev => [...prev, ...newDocuments]);

      const successMessage: ChatMessage = {
        id: `upload-success-${Date.now()}`,
        text: `Successfully uploaded and processed ${files.length} document(s). You can now ask questions about their content!`,
        sender: 'bot',
        timestamp: new Date(),
        confidence: 1.0
      };

      setMessages(prev => [...prev, successMessage]);
      
      // Switch to chat view after successful upload
      setCurrentView('chat');
      
    } catch (error) {
      console.error('Error uploading documents:', error);
      
      const errorMessage: ChatMessage = {
        id: `upload-error-${Date.now()}`,
        text: 'Failed to upload documents. Please try again.',
        sender: 'bot',
        timestamp: new Date(),
        confidence: 0.0,
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([{
      id: 'welcome-clear',
      text: 'Chat history cleared. How can I help you today?',
      sender: 'bot',
      timestamp: new Date(),
      confidence: 1.0
    }]);
  };

  const handleRemoveDocument = (documentId: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== documentId));
  };

  return (
    <div className="app">
      <Header 
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        currentView={currentView}
        onViewChange={setCurrentView}
      />
      
      <div className="app-body">
        <Sidebar
          isOpen={sidebarOpen}
          documents={documents}
          onRemoveDocument={handleRemoveDocument}
          onClearChat={handleClearChat}
          onClose={() => setSidebarOpen(false)}
        />
        
        <main className={`main-content ${sidebarOpen ? 'sidebar-open' : ''}`}>
          {currentView === 'chat' ? (
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          ) : (
            <DocumentUpload
              onUpload={handleDocumentUpload}
              isLoading={isLoading}
              documents={documents}
            />
          )}
        </main>
      </div>
      
      {isLoading && <LoadingSpinner />}
    </div>
  );
};

export default App;
