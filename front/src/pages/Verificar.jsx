import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'
import logo from '../assets/logo.png'
import './Verificar.css'

function Verificar() {
  const [codigo, setCodigo] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/public/buscar', { codigo: codigo.trim() })
      
      if (response.data.found) {
        navigate(`/certificado/${codigo.trim()}`)
      } else {
        setError('Código no encontrado. Por favor verifica el código e intenta nuevamente.')
      }
    } catch (err) {
      setError('Error al buscar el certificado. Por favor intenta nuevamente.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="verificar-container">
      <div className="verificar-card">
        <div className="verificar-logo-container">
          <img src={logo} alt="CENPROD - Centro Profesional Docente" className="verificar-logo" />
        </div>
        <h1>
          <span className="verificar-text">Verificar</span>{' '}
          <span className="certificado-text">Certificado</span>
        </h1>
        <p className="subtitle">Ingresa el código de tu certificado para verificar su validez</p>
        
        <form onSubmit={handleSubmit} className="verificar-form">
          <div className="input-group">
            <label htmlFor="codigo">Código del Certificado</label>
            <input
              type="text"
              id="codigo"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              placeholder="A1B2C3D4E5"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Buscando...' : 'Buscar Certificado'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Verificar
