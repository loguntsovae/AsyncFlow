import { useState, useEffect } from 'react'
import './App.css'
import axios from 'axios'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showSignIn, setShowSignIn] = useState(false)
  const [showSignUp, setShowSignUp] = useState(false)
  const [signInData, setSignInData] = useState({ username: '', password: '' })
  const [signUpData, setSignUpData] = useState({ username: '', password: '' })
  const [showAuthForm, setShowAuthForm] = useState(false)
  const [authData, setAuthData] = useState({ username: '', password: '' })

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

  const toggleSignIn = () => setShowSignIn(!showSignIn)
  const toggleSignUp = () => setShowSignUp(!showSignUp)
  const toggleAuthForm = () => setShowAuthForm(!showAuthForm)

  const handleSignInChange = (e) => {
    const { name, value } = e.target
    setSignInData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSignUpChange = (e) => {
    const { name, value } = e.target
    setSignUpData((prev) => ({ ...prev, [name]: value }))
  }

  const handleAuthChange = (e) => {
    const { name, value } = e.target
    setAuthData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSignInSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post('/api/v1/auth/login', signInData)
      alert(`Login successful: ${response.data.message}`)
    } catch (error) {
      alert(`Login failed: ${error.response?.data?.message || error.message}`)
    }
  }

  const handleSignUpSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post('/api/v1/auth/register', signUpData)
      alert(`Registration successful: ${response.data.message}`)
    } catch (error) {
      alert(`Registration failed: ${error.response?.data?.message || error.message}`)
    }
  }

  const handleAuthSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await axios.post('/api/v1/auth/login', authData)
      alert(`Login successful: ${response.data.message}`)
      toggleAuthForm()
    } catch (error) {
      alert(`Login failed: ${error.response?.data?.message || error.message}`)
    }
  }

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

      <div className="auth-buttons" style={{ position: 'absolute', top: '20px', right: '20px' }}>
        <button className="auth-button" onClick={toggleSignIn}>Sign In</button>
        <button className="auth-button" onClick={toggleSignUp}>Sign Up</button>
      </div>

      {showSignIn && (
        <div className="modal">
          <button className="modal-close" onClick={toggleSignIn}>&times;</button>
          <h3>Sign In</h3>
          <form onSubmit={handleSignInSubmit}>
            <label>
              Username:
              <input
                type="text"
                name="username"
                value={signInData.username}
                onChange={handleSignInChange}
                placeholder="Enter your username"
              />
            </label>
            <label>
              Password:
              <input
                type="password"
                name="password"
                value={signInData.password}
                onChange={handleSignInChange}
                placeholder="Enter your password"
              />
            </label>
            <button type="submit">Submit</button>
          </form>
        </div>
      )}

      {showSignUp && (
        <div className="modal">
          <button className="modal-close" onClick={toggleSignUp}>&times;</button>
          <h3>Sign Up</h3>
          <form onSubmit={handleSignUpSubmit}>
            <label>
              Username:
              <input
                type="text"
                name="username"
                value={signUpData.username}
                onChange={handleSignUpChange}
                placeholder="Choose a username"
              />
            </label>
            <label>
              Password:
              <input
                type="password"
                name="password"
                value={signUpData.password}
                onChange={handleSignUpChange}
                placeholder="Choose a password"
              />
            </label>
            <button type="submit">Register</button>
          </form>
        </div>
      )}

      {showAuthForm && (
        <div className="modal">
          <button className="modal-close" onClick={toggleAuthForm}>&times;</button>
          <h3>Authentication</h3>
          <form onSubmit={handleAuthSubmit}>
            <label>
              Username:
              <input
                type="text"
                name="username"
                value={authData.username}
                onChange={handleAuthChange}
                placeholder="Enter your username"
              />
            </label>
            <label>
              Password:
              <input
                type="password"
                name="password"
                value={authData.password}
                onChange={handleAuthChange}
                placeholder="Enter your password"
              />
            </label>
            <button type="submit">Submit</button>
          </form>
        </div>
      )}

      <footer className="footer">
        <p>AsyncFlow © 2025 | Built with ❤️ for microservices architecture</p>
      </footer>
    </div>
  )
}

export default App
