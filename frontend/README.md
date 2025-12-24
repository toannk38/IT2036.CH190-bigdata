# Vietnam Stock Frontend

React TypeScript frontend application for Vietnam Stock AI Backend.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.template .env
# Edit .env with your API base URL
```

3. Start development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── components/      # Reusable UI components
│   ├── common/      # Common components
│   ├── charts/      # Chart components  
│   └── layout/      # Layout components
├── pages/           # Page components
├── hooks/           # Custom React hooks
├── services/        # API service functions
├── types/           # TypeScript type definitions
├── utils/           # Utility functions
├── contexts/        # React contexts
└── constants/       # Application constants
```

## Technology Stack

- React 18 + TypeScript
- Vite for build tooling
- React Router for routing
- React Query for data fetching
- Material-UI for components
- Axios for HTTP client
