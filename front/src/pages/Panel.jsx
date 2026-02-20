import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useNavigate, Navigate, useLocation } from 'react-router-dom'
import api from '../utils/api'
import { getUser, removeToken } from '../utils/auth'
import CrearCertificado from '../components/CrearCertificado'
import ListaCertificados from '../components/ListaCertificados'
import GestionClientes from '../components/GestionClientes'
import UnirPDFs from '../components/UnirPDFs'
import ReemplazarPDF from '../components/ReemplazarPDF'
import logoSidebar from '../assets/logo.png'
import './Panel.css'

function Panel() {
  const iconCertificados = '\u{1F4CB}'
  const iconCrear = '\u{2795}'
  const iconClientes = '\u{1F464}'
  const iconUnir = '\u{1F517}'
  const iconReemplazar = '\u{1F4C4}'
  const iconVerificar = '\u{1F50E}'
  const iconSalir = '\u{1F6AA}'
  const [user, setUser] = useState(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const isUnirPDFs = location.pathname === '/panel/unir-pdfs'
  const isReemplazarPDF = location.pathname === '/panel/reemplazar-pdf'

  useEffect(() => {
    const userData = getUser()
    if (!userData) {
      navigate('/login')
    } else {
      setUser(userData)
    }
  }, [navigate])

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  const closeSidebar = () => {
    setIsSidebarOpen(false)
  }

  if (!user) {
    return <div>Cargando...</div>
  }

  const handleLogout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (_) {
      // no-op
    }
    removeToken()
    navigate('/login')
  }

  return (
    <div className="panel-container">
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={closeSidebar}></div>
      )}

      <nav className={`panel-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <img src={logoSidebar} alt="CENPROD" className="sidebar-logo" />
          <button className="close-sidebar-btn" onClick={closeSidebar}>X</button>
          <div className="sidebar-user-info">
            <p className="sidebar-email">{user.email}</p>
            <span className="sidebar-role">
              {(user?.role || 'operador').toUpperCase()}
            </span>
          </div>
        </div>
        <div style={{ flex: 1, paddingTop: '1rem' }}>
          <NavLink to="/panel/certificados" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconCertificados} Certificados
          </NavLink>
          <NavLink to="/panel/crear" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconCrear} Crear Certificado
          </NavLink>
          <NavLink to="/panel/unir-pdfs" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconUnir} Unir PDFs
          </NavLink>
          <NavLink to="/panel/reemplazar-pdf" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconReemplazar} Reemplazar PDF
          </NavLink>
          <NavLink to="/panel/clientes" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconClientes} Gestion de Clientes
          </NavLink>
        </div>

        <div className="sidebar-footer">
          <NavLink to="/verificar" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            {iconVerificar} Verificar Certificado
          </NavLink>
          <button type="button" className="nav-item nav-item-button" onClick={handleLogout}>
            {iconSalir} Cerrar Sesion
          </button>
        </div>
      </nav>

      <main className="panel-content">
        <button className="mobile-menu-toggle" onClick={toggleSidebar}>
          Menu
        </button>

        <div className={`panel-main-card ${(isUnirPDFs || isReemplazarPDF) ? 'panel-main-card-muted' : ''}`}>
          <Routes>
            <Route index element={<Navigate to="certificados" replace />} />
            <Route path="certificados" element={<ListaCertificados />} />
            <Route path="crear" element={<CrearCertificado />} />
            <Route path="clientes" element={<GestionClientes />} />
            <Route path="unir-pdfs" element={<UnirPDFs />} />
            <Route path="reemplazar-pdf" element={<ReemplazarPDF />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default Panel
