export interface ChatMessage {
  id: string;
  message: string;
  content: string;
  type: 'user' | 'assistant';
  isUser: boolean;
  timestamp: Date;
  isError?: boolean;
  error?: string;
  sources?: MessageSource[];
}

export interface MessageSource {
  name: string;
  page?: number;
  relevanceScore?: number;
}

export interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: Date;
  status: 'uploading' | 'processed' | 'error';
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface ChatResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata: Record<string, any>;
    similarity_score: number;
  }>;
  confidence: number;
  num_sources: number;
}

export interface UploadResponse {
  message: string;
  files_processed: number;
  chunks_created: number;
}

export interface HealthResponse {
  status: string;
  message: string;
}

export interface StatsResponse {
  vector_db_type: string;
  embedding_model: string;
  llm_model: string;
  status: string;
}

export interface ChatRequest {
  question: string;
  num_docs?: number;
}

export type ViewType = 'chat' | 'upload';
