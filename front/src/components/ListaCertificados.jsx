import { useState, useEffect } from 'react'
import api from '../utils/api'
import { getUser } from '../utils/auth'
import ConfirmModal from './ConfirmModal'
import './ListaCertificados.css'

function ListaCertificados() {
  const [certificados, setCertificados] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAnularModal, setShowAnularModal] = useState(false)
  const [certificadoToAnular, setCertificadoToAnular] = useState(null)
  const user = getUser()

  useEffect(() => {
    fetchCertificados()
  }, [])

  const fetchCertificados = async () => {
    try {
      const response = await api.get('/admin/certificados')
      setCertificados(response.data)
    } catch (err) {
      setError('Error al cargar los certificados')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadQR = async (codigo) => {
    try {
      const response = await api.get(`/admin/certificados/${codigo}/qr`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `qr_${codigo}.png`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('Error al descargar el QR')
    }
  }

  const handleAnularClick = (codigo) => {
    setCertificadoToAnular(codigo)
    setShowAnularModal(true)
  }

  const handleAnularConfirm = async () => {
    if (!certificadoToAnular) return

    try {
      await api.post(`/admin/certificados/${certificadoToAnular}/anular`, { motivo: 'Anulado desde panel' })
      setShowAnularModal(false)
      setCertificadoToAnular(null)
      setSuccess('Certificado anulado exitosamente')
      fetchCertificados()
    } catch (err) {
      setError('Error al anular el certificado')
      setShowAnularModal(false)
      setCertificadoToAnular(null)
    }
  }

  const copyLink = (codigo) => {
    const link = `${window.location.origin}/certificado/${codigo}`
    navigator.clipboard.writeText(link)
    setSuccess('Link copiado al portapapeles!')
    setTimeout(() => setSuccess(''), 3000)
  }

  const filteredCertificados = certificados.filter((cert) => {
    const search = searchTerm.toLowerCase()
    return (
      cert.codigo?.toLowerCase().includes(search) ||
      cert.nombres?.toLowerCase().includes(search) ||
      cert.apellidos?.toLowerCase().includes(search) ||
      cert.curso?.toLowerCase().includes(search)
    )
  })

  if (loading) {
    return <div className="loading">Cargando certificados...</div>
  }

  return (
    <div className="lista-certificados">
      <div className="lista-header">
        <h2>Lista de Certificados</h2>
      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}
      
      <ConfirmModal
        isOpen={showAnularModal}
        onClose={() => {
          setShowAnularModal(false)
          setCertificadoToAnular(null)
        }}
        onConfirm={handleAnularConfirm}
        title="Anular Certificado"
        message={`¿Está seguro de anular el certificado con código ${certificadoToAnular}? Esta acción marcará el certificado como anulado.`}
        confirmText="Anular"
        cancelText="Cancelar"
        type="warning"
      />
        <input
          type="text"
          placeholder="Buscar certificados..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      {error && <div className="alert error">{error}</div>}

      {/* Vista de tabla para desktop */}
      <div className="certificados-table-container">
        <table className="certificados-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre Completo</th>
              <th>Curso</th>
              <th>Fecha Emisión</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredCertificados.length === 0 ? (
              <tr>
                <td colSpan="6" className="no-data">
                  No hay certificados registrados
                </td>
              </tr>
            ) : (
              filteredCertificados.map((cert) => (
                <tr key={cert.codigo} className={cert.estado === 'ANULADO' ? 'anulado' : ''}>
                  <td>{cert.codigo}</td>
                  <td>
                    {cert.nombre_completo || `${cert.nombres || ''} ${cert.apellidos || ''}`.trim() || '-'}
                  </td>
                  <td>{cert.curso}</td>
                  <td>{cert.fecha_emision}</td>
                  <td>
                    <span className={`badge ${cert.estado === 'VALIDO' ? 'valido' : 'anulado'}`}>
                      {cert.estado}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button
                        onClick={() => copyLink(cert.codigo)}
                        className="btn-action btn-copy"
                        title="Copiar link"
                      >
                        🔗
                      </button>
                      <button
                        onClick={() => handleDownloadQR(cert.codigo)}
                        className="btn-action btn-qr"
                        title="Descargar QR"
                      >
                        📱
                      </button>
                      {cert.estado === 'VALIDO' && (
                        <button
                          onClick={() => handleAnularClick(cert.codigo)}
                          className="btn-action btn-anular"
                          title="Anular"
                        >
                          ❌
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Vista de cards para móviles */}
      <div className="certificados-cards-container">
        {filteredCertificados.length === 0 ? (
          <div className="no-data-card">
            No hay certificados registrados
          </div>
        ) : (
          filteredCertificados.map((cert) => (
            <div key={cert.codigo} className={`certificado-card ${cert.estado === 'ANULADO' ? 'anulado' : ''}`}>
              <div className="card-header">
                <div className="card-title">
                  <h3>{cert.nombre_completo || `${cert.nombres || ''} ${cert.apellidos || ''}`.trim() || '-'}</h3>
                  <span className={`badge ${cert.estado === 'VALIDO' ? 'valido' : 'anulado'}`}>
                    {cert.estado}
                  </span>
                </div>
                <div className="card-codigo">{cert.codigo}</div>
              </div>
              <div className="card-body">
                <div className="card-field">
                  <span className="card-label">Curso:</span>
                  <span className="card-value">{cert.curso}</span>
                </div>
                <div className="card-field">
                  <span className="card-label">Fecha Emisión:</span>
                  <span className="card-value">{cert.fecha_emision}</span>
                </div>
              </div>
              <div className="card-actions">
                <button
                  onClick={() => copyLink(cert.codigo)}
                  className="btn-action btn-copy"
                  title="Copiar link"
                >
                  🔗 Copiar
                </button>
                <button
                  onClick={() => handleDownloadQR(cert.codigo)}
                  className="btn-action btn-qr"
                  title="Descargar QR"
                >
                  📱 QR
                </button>
                {cert.estado === 'VALIDO' && (
                  <button
                    onClick={() => handleAnularClick(cert.codigo)}
                    className="btn-action btn-anular"
                    title="Anular"
                  >
                    ❌ Anular
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ListaCertificados
