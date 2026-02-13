import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, useNavigate, Navigate, useLocation } from 'react-router-dom'
import { getUser, removeToken } from '../utils/auth'
import CrearCertificado from '../components/CrearCertificado'
import ListaCertificados from '../components/ListaCertificados'
import GestionUsuarios from '../components/GestionUsuarios'
import GestionClientes from '../components/GestionClientes'
import UnirPDFs from '../components/UnirPDFs'
import logoSidebar from '../assets/logo.png'
import './Panel.css'

function Panel() {
  const [user, setUser] = useState(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  // Detectar si estamos en la ruta de unir-pdfs para cambiar el fondo
  const isUnirPDFs = location.pathname === '/panel/unir-pdfs'

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

  const isAdmin = user.role === 'admin'

  const handleLogout = () => {
    removeToken()
    navigate('/login')
  }

  return (
    <div className="panel-container">
      {/* Overlay para cerrar sidebar en móvil */}
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={closeSidebar}></div>
      )}

      <nav className={`panel-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <img src={logoSidebar} alt="CENPROD" className="sidebar-logo" />
          <button className="close-sidebar-btn" onClick={closeSidebar}>×</button>
          <div className="sidebar-user-info">
            <p className="sidebar-email">{user.email}</p>
            <span className="sidebar-role">
              {user.role.toUpperCase()}
            </span>
          </div>
        </div>
        <div style={{ flex: 1, paddingTop: '1rem' }}>
          <NavLink to="/panel/certificados" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            📋 Certificados
          </NavLink>
          <NavLink to="/panel/crear" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            ➕ Crear Certificado
          </NavLink>
          <NavLink to="/panel/clientes" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            👤 Gestión de Clientes
          </NavLink>
          <NavLink to="/panel/unir-pdfs" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            🔗 Unir PDFs
          </NavLink>
          {isAdmin && (
            <NavLink to="/panel/usuarios" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
              👥 Gestión de Usuarios
            </NavLink>
          )}
        </div>

        <div className="sidebar-footer">
          <NavLink to="/verificar" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} onClick={closeSidebar}>
            🔎 Verificar Certificado
          </NavLink>
          <button type="button" className="nav-item nav-item-button" onClick={handleLogout}>
            🚪 Cerrar Sesión
          </button>
        </div>
      </nav>

      <main className="panel-content">
        <button className="mobile-menu-toggle" onClick={toggleSidebar}>
          ☰
        </button>

        <div style={{
          background: isUnirPDFs ? '#f1f5f9' : 'var(--color-white)',
          borderRadius: '12px',
          padding: '2rem',
          boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
        }}>
          <Routes>
            {/* /panel -> /panel/certificados */}
            <Route index element={<Navigate to="certificados" replace />} />
            <Route path="certificados" element={<ListaCertificados />} />
            <Route path="crear" element={<CrearCertificado />} />
            <Route path="clientes" element={<GestionClientes />} />
            <Route path="unir-pdfs" element={<UnirPDFs />} />
            {isAdmin && <Route path="usuarios" element={<GestionUsuarios />} />}
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default Panel
