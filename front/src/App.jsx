import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Verificar from './pages/Verificar'
import Certificado from './pages/Certificado'
import Login from './pages/Login'
import Panel from './pages/Panel'
import PdfFullView from './pages/PdfFullView'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Verificar />} />
        <Route path="verificar" element={<Verificar />} />
        <Route path="certificado/:codigo" element={<Certificado />} />
        <Route path="consulta/:codigo" element={<Certificado />} />
        <Route path="pdf/:codigo" element={<PdfFullView />} />
        <Route path="login" element={<Login />} />
        <Route
          path="panel/*"
          element={
            <ProtectedRoute>
              <Panel />
            </ProtectedRoute>
          }
        />
      </Route>
    </Routes>
  )
}

export default App
