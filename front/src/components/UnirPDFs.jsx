import { useState } from 'react'
import api from '../utils/api'
import './UnirPDFs.css'

function UnirPDFs() {
  const [codigo, setCodigo] = useState('')
  const [certificado, setCertificado] = useState(null)
  const [archivo, setArchivo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const buscarCertificado = async () => {
    if (!codigo.trim()) {
      setError('Por favor ingresa un código de certificado')
      return
    }

    setError('')
    setCertificado(null)
    setLoading(true)

    try {
      const response = await api.get(`/public/certificados/${codigo.trim()}`)
      if (response.data.found) {
        setCertificado(response.data)
      } else {
        setError('Certificado no encontrado')
      }
    } catch (err) {
      setError('Error al buscar el certificado')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Por favor selecciona un archivo PDF')
        return
      }
      setArchivo(file)
      setError('')
    }
  }

  const handleUnirPDFs = async () => {
    if (!certificado) {
      setError('Primero debes buscar un certificado')
      return
    }

    if (!archivo) {
      setError('Por favor selecciona un archivo PDF para unir')
      return
    }

    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const formData = new FormData()
      formData.append('pdf_file', archivo)

      const response = await api.post(
        `/admin/certificados/${codigo}/unir-pdf`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setSuccess('PDFs unidos exitosamente. El certificado ahora tiene 2 páginas.')
      setArchivo(null)
      setCertificado(null)
      setCodigo('')
      
      // Limpiar el input de archivo
      const fileInput = document.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al unir los PDFs')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="unir-pdfs-container unir-pdfs-wrapper">
      <div className="unir-pdfs-header">
        <h1>🔗 Unir PDFs</h1>
        <p>Une un PDF adicional al certificado generado</p>
      </div>

      <div className="unir-pdfs-content">
        {/* Buscar Certificado */}
        <div className="form-section">
          <h2>1. Buscar Certificado</h2>
          <div className="search-box">
            <input
              type="text"
              placeholder="Ingresa el código del certificado"
              value={codigo}
              onChange={(e) => setCodigo(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && buscarCertificado()}
              className="search-input"
            />
            <button
              onClick={buscarCertificado}
              disabled={loading}
              className="btn-search"
            >
              {loading ? 'Buscando...' : '🔍 Buscar'}
            </button>
          </div>

          {certificado && (
            <div className="certificado-info">
              <h3>Certificado Encontrado:</h3>
              <p><strong>Nombre:</strong> {certificado.nombres} {certificado.apellidos}</p>
              <p><strong>Curso:</strong> {certificado.curso}</p>
              <p><strong>Código:</strong> {certificado.codigo}</p>
            </div>
          )}
        </div>

        {/* Subir PDF */}
        <div className="form-section">
          <h2>2. Subir PDF Adicional</h2>
          <div className="file-upload-area">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              id="pdf-upload"
              className="file-input"
            />
            <label htmlFor="pdf-upload" className="file-label">
              {archivo ? `📄 ${archivo.name}` : '📎 Seleccionar archivo PDF'}
            </label>
            {archivo && (
              <button
                onClick={() => {
                  setArchivo(null)
                  const fileInput = document.getElementById('pdf-upload')
                  if (fileInput) fileInput.value = ''
                }}
                className="btn-remove-file"
              >
                ✕
              </button>
            )}
          </div>
        </div>

        {/* Mensajes */}
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {/* Botón Unir */}
        <div className="form-actions">
          <button
            onClick={handleUnirPDFs}
            disabled={!certificado || !archivo || loading}
            className="btn-unir"
          >
            {loading ? 'Uniendo PDFs...' : '🔗 Unir PDFs'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default UnirPDFs
