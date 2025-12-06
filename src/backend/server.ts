import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { API_PREFIX, HTTP_STATUS } from '../shared/constants/index.js';
import type { ApiResponse, HealthCheck } from '../shared/types/index.js';

dotenv.config();

const app: Application = express();
const isProduction = process.env.NODE_ENV === 'production';
const PORT = isProduction ? Number(process.env.PORT) || 5000 : Number(process.env.BACKEND_PORT) || 3001;
const HOST = '0.0.0.0';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Allow Vite dev tools in development
}));
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
app.use((req: Request, res: Response, next: NextFunction) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get(`${API_PREFIX}/health`, (req: Request, res: Response<ApiResponse<HealthCheck>>) => {
  const healthCheck: HealthCheck = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
  };

  res.status(HTTP_STATUS.OK).json({
    success: true,
    data: healthCheck,
  });
});

// Welcome endpoint
app.get(`${API_PREFIX}/`, (req: Request, res: Response<ApiResponse<{ message: string }>>) => {
  res.status(HTTP_STATUS.OK).json({
    success: true,
    data: {
      message: 'Welcome to Fardowso Dhuuxo API - Strong Foundation for Complete Systems',
    },
  });
});

// Serve static frontend files in production
if (isProduction) {
  // From dist/backend/backend/server.js, frontend build is at dist/frontend
  const frontendPath = path.join(__dirname, '../../frontend');
  app.use(express.static(frontendPath));
  
  // Handle client-side routing - serve index.html for all non-API routes
  app.get('*', (req: Request, res: Response) => {
    res.sendFile(path.join(frontendPath, 'index.html'));
  });
} else {
  // 404 handler for development (production uses catch-all above)
  app.use((req: Request, res: Response<ApiResponse>) => {
    res.status(HTTP_STATUS.NOT_FOUND).json({
      success: false,
      error: 'Route not found',
    });
  });
}

// Error handler
app.use((err: Error, req: Request, res: Response<ApiResponse>, next: NextFunction) => {
  console.error('Error:', err);
  res.status(HTTP_STATUS.INTERNAL_ERROR).json({
    success: false,
    error: process.env.NODE_ENV === 'production' ? 'Internal server error' : err.message,
  });
});

// Start server
app.listen(PORT, HOST, () => {
  console.log(`🚀 Backend API running on http://${HOST}:${PORT}`);
  console.log(`📡 Health check: http://${HOST}:${PORT}${API_PREFIX}/health`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app;
