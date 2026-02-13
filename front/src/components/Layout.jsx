import { Outlet, useLocation } from 'react-router-dom'
import './Layout.css'

function Layout() {
  const location = useLocation()

  // En el panel y certificado no usamos este header/layout público (pantalla completa)
  if (location.pathname.startsWith('/panel') ||
    location.pathname.startsWith('/certificado/') ||
    location.pathname.startsWith('/consulta/') ||
    location.pathname === '/login') {
    return <Outlet />
  }

  // Para la página de verificar, usar layout especial con fondo de gradiente
  if (location.pathname === '/verificar' || location.pathname === '/') {
    return (
      <div className="layout-verificar">
        <main className="main-verificar">
          <Outlet />
        </main>
      </div>
    )
  }

  return (
    <div className="layout">
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
