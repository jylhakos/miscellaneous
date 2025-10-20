import { ChatResponse, UploadResponse, HealthResponse, StatsResponse, ChatRequest } from '../types';

// API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

class ChatAPI {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add timeout to requests
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...defaultOptions,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timed out. Please try again.');
        }
        throw error;
      }
      
      throw new Error('An unexpected error occurred');
    }
  }

  private async makeFormRequest<T>(
    endpoint: string,
    formData: FormData
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT * 2); // Longer timeout for file uploads

    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Upload timed out. Please try again with smaller files.');
        }
        throw error;
      }
      
      throw new Error('An unexpected error occurred during upload');
    }
  }

  async sendMessage(question: string, numDocs: number = 5): Promise<ChatResponse> {
    const request: ChatRequest = {
      question,
      num_docs: numDocs,
    };

    return this.makeRequest<ChatResponse>('/query', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async uploadDocuments(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    return this.makeFormRequest<UploadResponse>('/upload', formData);
  }

  async healthCheck(): Promise<HealthResponse> {
    return this.makeRequest<HealthResponse>('/health');
  }

  async getStats(): Promise<StatsResponse> {
    return this.makeRequest<StatsResponse>('/stats');
  }

  // Utility method to check if the API is reachable
  async isApiReachable(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  // Method to get API base URL (useful for debugging)
  getBaseURL(): string {
    return this.baseURL;
  }
}

// Create and export a singleton instance
export const chatAPI = new ChatAPI();

// Export the class for testing purposes
export { ChatAPI };
