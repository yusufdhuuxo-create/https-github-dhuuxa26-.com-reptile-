import React, { useEffect, useState } from 'react';
import type { ApiResponse, HealthCheck } from '../shared/types';
import { API_PREFIX } from '../shared/constants';
import './styles/App.css';

function App() {
  const [health, setHealth] = useState<HealthCheck | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_PREFIX}/health`)
      .then((res) => res.json())
      .then((data: ApiResponse<HealthCheck>) => {
        if (data.success && data.data) {
          setHealth(data.data);
        } else {
          setError('Failed to fetch health status');
        }
      })
      .catch((err) => {
        setError('Backend connection failed');
        console.error(err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🚀 Fardowso Dhuuxo</h1>
          <p className="subtitle">Professional Full-Stack System</p>
        </header>

        <div className="content">
          <div className="card">
            <h2>System Status</h2>
            {loading && <p>Checking system health...</p>}
            {error && <p className="error">⚠️ {error}</p>}
            {health && (
              <div className="health-status">
                <p className="status-badge success">✓ System Healthy</p>
                <div className="health-details">
                  <p><strong>Status:</strong> {health.status}</p>
                  <p><strong>Version:</strong> {health.version}</p>
                  <p><strong>Time:</strong> {new Date(health.timestamp).toLocaleString()}</p>
                </div>
              </div>
            )}
          </div>

          <div className="card">
            <h2>Tech Stack</h2>
            <ul className="tech-list">
              <li>✓ TypeScript - Type-safe code</li>
              <li>✓ React - Modern UI framework</li>
              <li>✓ Express - Backend API server</li>
              <li>✓ Vite - Fast build tool</li>
              <li>✓ Modular Architecture</li>
            </ul>
          </div>

          <div className="card">
            <h2>Features</h2>
            <ul className="features-list">
              <li>🏗️ Professional project structure</li>
              <li>🔒 Type-safe across frontend & backend</li>
              <li>📦 Shared code between layers</li>
              <li>🎨 Modern, responsive design</li>
              <li>⚡ Hot reload for development</li>
              <li>🚀 Production-ready setup</li>
            </ul>
          </div>
        </div>

        <footer className="footer">
          <p>© 2025 Fardowso Dhuuxo. All Rights Reserved.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
