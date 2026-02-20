import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api, { getApiUrl } from '../utils/api'
import logo from '../assets/logo.png'
import logoInst from '../assets/Logo_INST.png'
import './Certificado.css'

function Certificado() {
  const { codigo } = useParams()
  const navigate = useNavigate()
  const [certificado, setCertificado] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchCertificado = async () => {
      try {
        const response = await api.get(`/public/certificados/${codigo}`)
        if (response.data.found) {
          setCertificado(response.data)
        } else {
          setError('Certificado no encontrado')
        }
      } catch (err) {
        setError('Error al cargar el certificado')
      } finally {
        setLoading(false)
      }
    }

    fetchCertificado()
  }, [codigo])

  const handleDownloadPDF = () => {
    // Abrir PDF en nueva pestaña usando el visor personalizado del frontend
    // Esto mantiene el favicon y permite titulo personalizado
    window.open(`/pdf/${codigo}`, '_blank')
  }

  if (loading) {
    return (
      <div className="certificado-container">
        <div className="loading">Cargando certificado...</div>
      </div>
    )
  }

  if (error || !certificado) {
    return (
      <div className="certificado-container">
        <div className="error-card">
          <h2>Certificado no encontrado</h2>
          <p>{error || 'El certificado solicitado no existe o ha sido eliminado.'}</p>
        </div>
      </div>
    )
  }

  const isAnulado = certificado.estado === 'ANULADO'
  const nombreCompleto = `${certificado.nombres} ${certificado.apellidos}`

  const pdfUrl = getApiUrl(`/public/certificados/${codigo}/pdf`)
  const absolutePdfUrl = pdfUrl.startsWith('http')
    ? pdfUrl
    : `${window.location.origin}${pdfUrl}`
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  const previewUrl = isLocalhost
    ? pdfUrl
    : `https://docs.google.com/viewer?url=${encodeURIComponent(absolutePdfUrl)}&embedded=true`

  return (
    <div className="certificado-container">
      <div className="certificado-layout">
        {/* Columna izquierda: Información del certificado */}
        <div className="certificado-info-panel">
          {isAnulado && (
            <div className="alert-anulado">
              <strong>⚠️ Certificado Anulado</strong>
              <p>Este certificado ha sido anulado y no es válido.</p>
            </div>
          )}

          <div className="info-header">
            <img src={logo} alt="Logo" className="header-logo" />
            <div className="header-title">
              <h1>CERTIFICADO</h1>
              <p className="info-subtitle">Verificación Digital</p>
            </div>
            <img src={logoInst} alt="Logo Institucional" className="header-logo" />
          </div>

          <div className="info-content">
            <div className="info-section">
              <div className="info-label">Nombre Completo</div>
              <div className="info-value nombre">{nombreCompleto}</div>
            </div>

            <div className="info-section">
              <div className="info-label">Curso</div>
              <div className="info-value curso">{certificado.curso}</div>
            </div>

            {certificado.horas && (
              <div className="info-section">
                <div className="info-label">Duración</div>
                <div className="info-value">{certificado.horas} horas</div>
              </div>
            )}

            <div className="info-section">
              <div className="info-label">Fecha de Emisión</div>
              <div className="info-value">{certificado.fecha_emision}</div>
            </div>

            <div className="info-section">
              <div className="info-label">Código de Verificación</div>
              <div className="info-value codigo">{certificado.codigo}</div>
            </div>
          </div>

          <div className="info-actions">
            <button onClick={handleDownloadPDF} className="btn-download">
              📄 Ver PDF Completo
            </button>
            <button onClick={() => window.location.href = getApiUrl(`/public/certificados/${codigo}/pdf?download=true`)} className="btn-download-file">
              ⬇️ Descargar Certificado Digital
            </button>
            <button onClick={() => navigate('/verificar')} className="btn-back">
              🔍 Verificar Otro Certificado
            </button>
          </div>
        </div>

        {/* Columna derecha: Previsualización del PDF */}
        <div className="certificado-preview-panel">
          <div className="preview-header">
            <h2>Vista Previa del Certificado</h2>
          </div>
          <div className="preview-container">
            <div className="pdf-wrapper">
              <iframe
                src={previewUrl}
                className="pdf-preview"
                title="Vista previa del certificado"
                frameBorder="0"
                scrolling="yes"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Certificado
