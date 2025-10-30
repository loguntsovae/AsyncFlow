import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get('/api/v1/health')
        setHealth(response.data)
      } catch (error) {
        setHealth({ status: 'error', message: error.message })
      } finally {
        setLoading(false)
      }
    }
    checkHealth()
  }, [])

  return (
    <div className="app">
      <header className="header">
        <h1>🌀 AsyncFlow</h1>
        <p className="subtitle">Event-Driven Microservices Platform</p>
      </header>

      <main className="main">
        <section className="hero">
          <h2>Welcome to AsyncFlow</h2>
          <p>A modern event-driven architecture demo built with FastAPI + RabbitMQ</p>
        </section>

        <section className="status-card">
          <h3>System Status</h3>
          {loading ? (
            <p className="loading">Checking services...</p>
          ) : (
            <div className="health-status">
              <div className={`status-indicator ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
                {health?.status === 'healthy' ? '✅' : '❌'}
              </div>
              <div className="status-details">
                <p><strong>Gateway:</strong> {health?.status || 'Unknown'}</p>
                {health?.services && (
                  <div className="services">
                    <h4>Services:</h4>
                    <ul>
                      {Object.entries(health.services).map(([name, info]) => (
                        <li key={name}>
                          <span className={`service-status ${info.status}`}>
                            {info.status === 'up' ? '🟢' : info.status === 'degraded' ? '🟡' : '🔴'}
                          </span>
                          <strong>{name}:</strong> {info.status}
                          {info.latency_ms && <span className="latency"> ({info.latency_ms}ms)</span>}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        <section className="features">
          <h3>Features</h3>
          <div className="feature-grid">
            <div className="feature-card">
              <h4>🔒 Authentication</h4>
              <p>JWT-based auth service with user management</p>
            </div>
            <div className="feature-card">
              <h4>📦 Orders</h4>
              <p>Order management with event publishing</p>
            </div>
            <div className="feature-card">
              <h4>💳 Billing</h4>
              <p>Async payment processing via RabbitMQ</p>
            </div>
            <div className="feature-card">
              <h4>🌐 API Gateway</h4>
              <p>Unified REST API with rate limiting & metrics</p>
            </div>
          </div>
        </section>

        <section className="tech-stack">
          <h3>Technology Stack</h3>
          <div className="tech-tags">
            <span className="tag">Python 3.12</span>
            <span className="tag">FastAPI</span>
            <span className="tag">RabbitMQ</span>
            <span className="tag">PostgreSQL</span>
            <span className="tag">Docker</span>
            <span className="tag">React</span>
            <span className="tag">Vite</span>
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>AsyncFlow © 2025 | Built with ❤️ for microservices architecture</p>
      </footer>
    </div>
  )
}

export default App
