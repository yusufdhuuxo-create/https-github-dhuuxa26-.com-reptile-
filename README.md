# Professional Full-Stack System

**Author:** Fardowso Dhuuxo  
**Copyright:** © 2025 Fardowso Dhuuxo. All Rights Reserved.

## Overview

A modern, professional full-stack web application built with TypeScript, featuring a React frontend and Express backend with shared code architecture.

## Tech Stack

### Frontend
- **React 18** - Modern UI framework
- **TypeScript** - Type-safe development
- **Vite** - Lightning-fast build tool
- **CSS3** - Modern styling

### Backend
- **Node.js 20** - JavaScript runtime
- **Express** - Web application framework
- **TypeScript** - Type-safe development
- **Helmet** - Security middleware
- **CORS** - Cross-origin resource sharing

### Shared Architecture
- **TypeScript** - Shared types between frontend and backend
- **Zod** - Runtime type validation
- Modular, scalable structure

## Quick Start

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```
This starts both frontend (port 5000) and backend (port 3001) concurrently.

### Production Build
```bash
npm run build
npm start
```

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Run both frontend and backend in development mode |
| `npm run dev:frontend` | Run only the frontend (Vite dev server) |
| `npm run dev:backend` | Run only the backend (Express API) |
| `npm run build` | Build both frontend and backend for production |
| `npm start` | Start the production server |
| `npm run lint` | Lint code with ESLint |
| `npm run format` | Format code with Prettier |

## Project Structure

```
├── src/
│   ├── backend/           # Express API server
│   │   ├── controllers/   # Request handlers
│   │   ├── services/      # Business logic
│   │   ├── models/        # Data models
│   │   ├── middleware/    # Custom middleware
│   │   ├── routes/        # API routes
│   │   └── server.ts      # Main server file
│   │
│   ├── frontend/          # React application
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── styles/        # CSS files
│   │   ├── App.tsx        # Main app component
│   │   └── main.tsx       # Entry point
│   │
│   └── shared/            # Shared code
│       ├── types/         # TypeScript types
│       ├── constants/     # Constants
│       └── validators/    # Validation schemas
│
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
└── PROJECT_STRUCTURE.md   # Detailed structure documentation
```

## Features

✨ **Type-Safe Development** - TypeScript across the entire stack  
🏗️ **Modular Architecture** - Clean separation of concerns  
🔒 **Security First** - Helmet.js, CORS protection  
⚡ **Fast Development** - Hot reload with Vite and tsx  
🎨 **Modern UI** - Responsive design with React  
📦 **Shared Code** - Reusable types and constants  
🚀 **Production Ready** - Optimized build configuration

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/` - API welcome message

## Development Notes

- Frontend runs on port **5000** (configured for Replit webview)
- Backend runs on port **3001**
- API requests from frontend are proxied to backend via `/api/*`
- Both frontend and backend share TypeScript types from `src/shared/`

## License

This project is proprietary software. All rights reserved.

See [LICENSE](LICENSE) for details.

---

*Built with passion by Fardowso Dhuuxo*
