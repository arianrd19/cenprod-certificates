import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import { setToken, setUser } from '../utils/auth'
import logo from '../assets/logo.png'
import bgImage from '../assets/2.jpeg' // Import image for the left side
import './Login.css'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setToken(response.data.access_token)
      setUser({
        email: response.data.email,
        role: response.data.role,
      })

      navigate('/panel/certificados')
    } catch (err) {
      setError(err.response?.data?.detail || 'Credenciales incorrectas o error de conexión.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-split-screen">
        {/* Left Side: Branding / Image */}
        <div className="login-branding">
          <div className="branding-overlay">
          </div>
          <img src={bgImage} alt="Education Concept" className="branding-image" />
        </div>

        {/* Right Side: Form */}
        <div className="login-form-container">
          <div className="login-form-wrapper">
            {/* Form header removed as requested */}

            <form onSubmit={handleSubmit} className="modern-form">
              {error && (
                <div className="error-alert">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="icon-sm">
                    <path fillRule="evenodd" d="M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003zM12 8.25a.75.75 0 01.75.75v3.75a.75.75 0 01-1.5 0V9a.75.75 0 01.75-.75zm0 8.25a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
                  </svg>
                  <span>{error}</span>
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Correo Electrónico</label>
                <div className="input-wrapper">
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="ejemplo@cenprod.com"
                    required
                    disabled={loading}
                    className={error ? 'input-error' : ''}
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="password">Contraseña</label>
                <div className="input-wrapper">
                  <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    disabled={loading}
                    className={error ? 'input-error' : ''}
                  />
                </div>
              </div>

              <div className="form-actions">
                <a href="#" className="forgot-password" onClick={(e) => e.preventDefault()}>¿Olvidaste tu contraseña?</a>
              </div>

              <button type="submit" className="btn-submit" disabled={loading}>
                {loading ? (
                  <span className="loader"></span>
                ) : (
                  'Ingresar'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
