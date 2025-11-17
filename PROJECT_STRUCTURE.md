# Project Structure

## Overview
Professional full-stack TypeScript application with clean separation of concerns.

## Directory Structure

```
├── src/
│   ├── backend/           # Express API Server
│   │   ├── controllers/   # Route controllers
│   │   ├── services/      # Business logic
│   │   ├── models/        # Data models
│   │   ├── middleware/    # Custom middleware
│   │   ├── routes/        # API routes
│   │   ├── utils/         # Helper functions
│   │   └── server.ts      # Main server file
│   │
│   ├── frontend/          # React Frontend
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── utils/         # Helper functions
│   │   ├── styles/        # CSS/styling files
│   │   ├── assets/        # Images, fonts, etc.
│   │   ├── App.tsx        # Main App component
│   │   └── main.tsx       # Entry point
│   │
│   └── shared/            # Code shared between frontend & backend
│       ├── types/         # TypeScript types & interfaces
│       ├── constants/     # Shared constants
│       └── validators/    # Data validation schemas
│
├── dist/                  # Compiled output (gitignored)
├── node_modules/          # Dependencies (gitignored)
│
├── package.json           # Project dependencies & scripts
├── tsconfig.json          # Base TypeScript config
├── tsconfig.backend.json  # Backend-specific TS config
├── tsconfig.frontend.json # Frontend-specific TS config
├── vite.config.ts         # Vite configuration
├── .eslintrc.json         # Code linting rules
├── .prettierrc            # Code formatting rules
└── .gitignore             # Git ignore patterns
```

## Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **CSS3** - Styling

### Backend
- **Node.js** - Runtime
- **Express** - Web framework
- **TypeScript** - Type safety
- **tsx** - TypeScript executor

### Shared
- **Zod** - Schema validation
- **TypeScript** - Shared types

### Development Tools
- **ESLint** - Code quality
- **Prettier** - Code formatting
- **Concurrently** - Run multiple processes

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start both frontend & backend in development mode |
| `npm run dev:frontend` | Start frontend only (Vite dev server on port 5000) |
| `npm run dev:backend` | Start backend only (Express API on port 3001) |
| `npm run build` | Build both frontend & backend for production |
| `npm run build:frontend` | Build frontend only |
| `npm run build:backend` | Build backend only |
| `npm start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run format` | Format code with Prettier |

## Port Configuration

- **Frontend (Vite)**: Port 5000 (configured for Replit webview)
- **Backend (Express)**: Port 3001
- **API Proxy**: Frontend proxies `/api/*` requests to backend

## Key Features

1. **Type Safety**: TypeScript across entire stack
2. **Shared Code**: Common types & constants in `/src/shared`
3. **Hot Reload**: Fast development with Vite & tsx watch mode
4. **Code Quality**: ESLint + Prettier for consistent code
5. **Production Ready**: Optimized build configuration
6. **Security**: Helmet.js, CORS protection
7. **Modular**: Clean separation of concerns

## Adding New Features

### Backend Endpoint
1. Create controller in `src/backend/controllers/`
2. Add route in `src/backend/routes/`
3. Register route in `server.ts`

### Frontend Component
1. Create component in `src/frontend/components/`
2. Import and use in pages or App.tsx

### Shared Types
1. Define in `src/shared/types/index.ts`
2. Use in both frontend and backend

## Best Practices

- Keep components small and focused
- Use TypeScript interfaces for all data structures
- Place shared code in `/src/shared`
- Follow existing naming conventions
- Run `npm run lint` before committing
- Use environment variables for configuration

---

**Author**: Fardowso Dhuuxo  
**License**: Proprietary - All Rights Reserved
