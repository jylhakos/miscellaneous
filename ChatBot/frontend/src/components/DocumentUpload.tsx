import React from 'react';
import { Document as ChatDocument } from '../types';

interface DocumentUploadProps {
  onFileUpload: (files: File[]) => void;
  isUploading: boolean;
  uploadProgress: number;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onFileUpload,
  isUploading,
  uploadProgress,
}) => {
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = React.useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    
    const validFiles = Array.from(files).filter(file => {
      const validTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain',
        'text/markdown',
        'application/rtf'
      ];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!validTypes.includes(file.type)) {
        alert(`Invalid file type: ${file.name}. Please upload PDF, Word, or text files.`);
        return false;
      }
      
      if (file.size > maxSize) {
        alert(`File too large: ${file.name}. Maximum size is 10MB.`);
        return false;
      }
      
      return true;
    });

    if (validFiles.length > 0) {
      onFileUpload(validFiles);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="document-upload">
      <h3>Upload Documents</h3>
      
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${isUploading ? 'uploading' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt,.md,.rtf"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />
        
        {isUploading ? (
          <div className="upload-progress">
            <div className="progress-icon">📤</div>
            <div className="progress-text">Uploading...</div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="progress-percentage">{Math.round(uploadProgress)}%</div>
          </div>
        ) : (
          <div className="upload-content">
            <div className="upload-icon">📁</div>
            <div className="upload-text">
              <div className="upload-primary">
                Drag & drop documents here
              </div>
              <div className="upload-secondary">
                or click to browse files
              </div>
            </div>
            <div className="upload-formats">
              Supports: PDF, Word, Text, Markdown (max 10MB each)
            </div>
          </div>
        )}
      </div>
      
      <div className="upload-tips">
        <h4>Tips for better results:</h4>
        <ul>
          <li>Use high-quality documents with clear text</li>
          <li>Avoid scanned images without OCR</li>
          <li>Structure documents with headings and sections</li>
          <li>Include relevant context and details</li>
        </ul>
      </div>
    </div>
  );
};

export default DocumentUpload;
