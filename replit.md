# Project Overview

## Owner
**Fardowso Dhuuxo** - All Rights Reserved

## Repository Information
Professional full-stack TypeScript web application with modern architecture and development practices.

## Current State
Production-ready full-stack application with:
- ✅ TypeScript frontend (React + Vite)
- ✅ TypeScript backend (Express + Node.js)
- ✅ Shared type system
- ✅ Professional project structure
- ✅ Development tools configured (ESLint, Prettier)
- ✅ Hot reload enabled for rapid development

## Architecture

### Frontend (React + Vite)
- Port: 5000 (Replit webview)
- Framework: React 18 with TypeScript
- Build: Vite for fast development and optimized production builds
- Styling: Modern CSS3 with responsive design

### Backend (Express API)
- Port: 3001 (localhost)
- Framework: Express with TypeScript
- Runtime: Node.js 20 with tsx for TypeScript execution
- Security: Helmet.js, CORS protection

### Shared Layer
- Common TypeScript types and interfaces
- Shared constants and validators
- Ensures type safety across the entire stack

## Project Structure
```
src/
├── backend/       # Express API
├── frontend/      # React UI
└── shared/        # Common code
```

See `PROJECT_STRUCTURE.md` for detailed documentation.

## Technical Setup
- **Languages:** TypeScript 5.3+, Node.js 20
- **Frontend:** React 18, Vite 5
- **Backend:** Express 4
- **Tools:** ESLint, Prettier, Concurrently
- **Package Manager:** npm

## Workflows
- `web-server` - Runs both frontend and backend concurrently
  - Frontend: Vite dev server (port 5000)
  - Backend: Express API (port 3001)
  - Auto-restart on file changes

## Development Features
- 🔥 Hot module replacement (HMR)
- 🎯 Type checking across full stack
- 🔍 Code linting and formatting
- 📡 API proxy configuration
- 🔒 Security middleware
- ⚡ Fast build times

## Deployment
- Target: Autoscale deployment
- Build: TypeScript compilation + Vite optimization
- Run: Production Express server

## User Preferences
- Professional, modular architecture
- TypeScript for type safety
- Separation of concerns (frontend/backend/shared)
- Modern development practices

## Recent Changes
- **Nov 17, 2025**: Initial professional setup
  - Configured TypeScript for frontend and backend
  - Set up Vite + React frontend
  - Created Express API backend
  - Implemented shared type system
  - Added development tooling (ESLint, Prettier)
  - Configured workflows and deployment

## Last Updated
November 17, 2025
