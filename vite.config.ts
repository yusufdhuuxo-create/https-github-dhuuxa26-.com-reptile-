import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5000,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true
      }
    }
  },
  resolve: {
    alias: {
      '@frontend': path.resolve(__dirname, './src/frontend'),
      '@shared': path.resolve(__dirname, './src/shared'),
    }
  },
  build: {
    outDir: 'dist/frontend'
  }
});
