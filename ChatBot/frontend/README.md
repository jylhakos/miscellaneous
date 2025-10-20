# RAG Chatbot Frontend

A React TypeScript frontend for the RAG (Retrieval-Augmented Generation) chatbot application.

## Features

- 💬 Real-time chat interface with the RAG backend
- 📁 Drag-and-drop document upload
- Responsive design for mobile and desktop
- UI (React) with animations
- 📚 Document management sidebar
- 🔍 Source attribution for AI responses
- ⚡ Fast and optimized performance

## Tech Stack

- **React 18** with TypeScript
- **Axios** for API communication
- **CSS3** with modern animations
- **React Hooks** for state management

## Project

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Header.tsx          # Navigation header
│   │   ├── ChatInterface.tsx   # Main chat component
│   │   ├── DocumentUpload.tsx  # File upload interface
│   │   ├── Sidebar.tsx         # Document management
│   │   └── LoadingSpinner.tsx  # Loading indicator
│   ├── types.ts               # TypeScript interfaces
│   ├── api.ts                 # API service layer
│   ├── App.tsx                # Main application
│   ├── App.css                # Global styles
│   ├── index.tsx              # React entry point
│   └── index.css              # Base styles
├── package.json
└── tsconfig.json
```

## Step-by-step

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open http://localhost:3000 in your browser

### Building for production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## API integration

The frontend communicates with the FastAPI backend through these endpoints:

- `POST /chat` - Send messages to the chatbot
- `POST /upload` - Upload documents
- `GET /documents` - List uploaded documents
- `DELETE /documents/{id}` - Remove documents

## Components

### ChatInterface
- Displays conversation history
- Handles message input and sending
- Shows typing indicators and loading states
- Displays source citations from RAG responses

### DocumentUpload
- Drag-and-drop file upload
- File validation (PDF, Word, text formats)
- Upload progress tracking
- File size and type restrictions

### Sidebar
- Document management interface
- Chat history clearing
- Application information
- Responsive mobile menu

### Header
- View switching (Chat/Upload)
- Sidebar toggle
- Document count indicator
- Responsive navigation

## Styling

The application uses a modern design system with:

- **Color Scheme**: Professional blue/gray palette
- **Typography**: System font stack for optimal readability
- **Animations**: Smooth transitions and micro-interactions
- **Responsive**: Mobile-first design approach
- **Accessibility**: ARIA labels and keyboard navigation

## Development

### Scripts

- `npm start` - Development server
- `npm run build` - Production build
- `npm test` - Run tests
- `npm run lint` - Code linting
- `npm run lint:fix` - Auto-fix linting issues

### Quality

- TypeScript for type safety
- ESLint for code quality
- React best practices
- Responsive design patterns

## Deployment

The frontend can be deployed to:

- **AWS Amplify** (Recommended)
- **Netlify**
- **Vercel**
- **Traditional web servers**

For AWS deployment, see the main project README for CloudFormation templates.

## Configuration

The application uses a proxy configuration in `package.json` to connect to the backend during development. For production, update the API base URL in `src/api.ts`.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is part of the RAG Chatbot application suite.
