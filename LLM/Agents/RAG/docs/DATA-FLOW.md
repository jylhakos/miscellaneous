# Data flow

## System architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WebUI[Web Interface]
        API[API Clients]
        OpenWebUI[Open WebUI]
    end

    subgraph "Gateway Layer"
        Nginx[Nginx Reverse Proxy]
    end

    subgraph "Application Layer"
        App[RAG Chat Application]
        Server[Express Server]
        Handlers[Request Handlers]
        Middleware[Middleware]
    end

    subgraph "RAG Processing Layer"
        RAGSystem[RAG Chat System]
        Memory[Conversation Memory]
        Retriever[Document Retriever]
        Embedder[Text Embedder]
    end

    subgraph "AI/ML Layer"
        Ollama[Ollama LLM Server]
        LLM[Language Model]
        EmbedModel[Embedding Model]
    end

    subgraph "Storage Layer"
        ChromaDB[ChromaDB Vector Store]
        FileSystem[Document Storage]
        Logs[Application Logs]
    end

    WebUI --> Nginx
    API --> Nginx
    OpenWebUI --> Ollama
    
    Nginx --> Server
    Server --> Handlers
    Handlers --> Middleware
    Handlers --> RAGSystem
    
    RAGSystem --> Memory
    RAGSystem --> Retriever
    RAGSystem --> Embedder
    RAGSystem --> Ollama
    
    Ollama --> LLM
    Ollama --> EmbedModel
    
    Retriever --> ChromaDB
    Embedder --> ChromaDB
    App --> FileSystem
    App --> Logs
```

## Document processing flow

```mermaid
sequenceDiagram
    participant User
    participant API as RAG API
    participant Handler as Document Handler
    participant Splitter as Text Splitter
    participant Embedder as Ollama Embeddings
    participant VectorDB as ChromaDB

    User->>API: POST /api/documents/upload
    API->>Handler: Process uploaded file
    Handler->>Handler: Validate file type
    Handler->>Handler: Load document content
    Handler->>Splitter: Split into chunks
    Splitter-->>Handler: Document chunks
    Handler->>Embedder: Generate embeddings
    Embedder-->>Handler: Chunk embeddings
    Handler->>VectorDB: Store chunks + embeddings
    VectorDB-->>Handler: Storage confirmation
    Handler-->>API: Upload successful
    API-->>User: Document processed response
```

## Chat query processing flow

```mermaid
sequenceDiagram
    participant User
    participant API as RAG API
    participant RAG as RAG System
    participant Memory as Conversation Memory
    participant Retriever as Document Retriever
    participant VectorDB as ChromaDB
    participant LLM as Ollama LLM

    User->>API: POST /api/chat
    API->>RAG: Process query
    RAG->>Memory: Get conversation history
    Memory-->>RAG: Previous context
    RAG->>Retriever: Find relevant documents
    Retriever->>VectorDB: Similarity search
    VectorDB-->>Retriever: Similar document chunks
    Retriever-->>RAG: Relevant documents
    RAG->>RAG: Assemble context
    RAG->>LLM: Generate response with context
    LLM-->>RAG: Generated response
    RAG->>Memory: Save conversation
    RAG-->>API: Response with sources
    API-->>User: Chat response
```

## Meta Llama 4 Scout

```mermaid
graph LR
    subgraph "Input Processing"
        Query[User Query]
        Context[Retrieved Context]
        History[Chat History]
    end

    subgraph "Prompt Construction"
        Template[Llama4 Scout Template]
        SystemPrompt[System Instructions]
        UserPrompt[User Message]
    end

    subgraph "Model Processing"
        Ollama[Ollama Server]
        Model[llama4-scout:8b]
        Quantization[4/8-bit Quantization]
    end

    subgraph "Output Processing"
        Response[Generated Response]
        Sources[Source Attribution]
        Memory[Memory Update]
    end

    Query --> Template
    Context --> Template
    History --> Template
    
    Template --> SystemPrompt
    Template --> UserPrompt
    
    SystemPrompt --> Ollama
    UserPrompt --> Ollama
    Ollama --> Model
    Model --> Quantization
    
    Quantization --> Response
    Response --> Sources
    Response --> Memory
```

## System component interaction

```mermaid
graph TD
    subgraph "Docker Containers"
        subgraph "rag-app"
            ExpressJS[Express.js Server]
            LangChain[LangChain.js]
            RAGLogic[RAG Processing Logic]
        end
        
        subgraph "ollama"
            OllamaServer[Ollama Server]
            Models[AI Models]
            ModelCache[Model Cache]
        end
        
        subgraph "chromadb"
            ChromaServer[Chroma Server]
            VectorStore[Vector Storage]
            Collections[Document Collections]
        end
        
        subgraph "nginx"
            ReverseProxy[Reverse Proxy]
            LoadBalancer[Load Balancer]
            SSL[SSL Termination]
        end
        
        subgraph "open-webui"
            WebInterface[Web Interface]
            ChatUI[Chat UI]
        end
    end

    ExpressJS <--> LangChain
    LangChain <--> RAGLogic
    RAGLogic <--> OllamaServer
    RAGLogic <--> ChromaServer
    
    OllamaServer <--> Models
    Models <--> ModelCache
    
    ChromaServer <--> VectorStore
    VectorStore <--> Collections
    
    ReverseProxy <--> ExpressJS
    LoadBalancer <--> ReverseProxy
    SSL <--> ReverseProxy
    
    WebInterface <--> OllamaServer
    ChatUI <--> WebInterface
```

## Memory and session management

```mermaid
stateDiagram-v2
    [*] --> NewSession: User starts chat
    
    state "Active Session" as Active {
        [*] --> Processing
        Processing --> Retrieving: Get relevant docs
        Retrieving --> Generating: Query LLM
        Generating --> Saving: Save to memory
        Saving --> Processing: Next message
    }
    
    NewSession --> Active: Create session
    Active --> Cleanup: Session timeout
    Active --> Cleanup: Manual cleanup
    Cleanup --> [*]: Session destroyed
    
    note right of Active
        Session includes:
        - Conversation history
        - Context buffer
        - Last accessed time
        - Memory limit tracking
    end note
```

## Error handling

```mermaid
graph TD
    Request[Incoming Request] --> Validation{Valid Request?}
    
    Validation -->|No| BadRequest[400 Bad Request]
    Validation -->|Yes| RateLimit{Rate Limit OK?}
    
    RateLimit -->|No| TooManyRequests[429 Too Many Requests]
    RateLimit -->|Yes| Processing[Process Request]
    
    Processing --> ServiceCheck{Services Available?}
    
    ServiceCheck -->|Ollama Down| OllamaError[503 Ollama Unavailable]
    ServiceCheck -->|ChromaDB Down| ChromaError[503 ChromaDB Unavailable]
    ServiceCheck -->|Services OK| Success[200 Success]
    
    Processing --> ServerError{Server Error?}
    ServerError -->|Yes| InternalError[500 Internal Server Error]
    ServerError -->|No| Success
    
    BadRequest --> LogError[Log Error]
    TooManyRequests --> LogError
    OllamaError --> LogError
    ChromaError --> LogError
    InternalError --> LogError
    
    LogError --> ErrorResponse[Return Error Response]
```
