import { useState, useEffect } from 'react'
import api from '../utils/api'
import './GestionUsuarios.css'

function GestionUsuarios() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    role: 'operador',
  })

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users')
      setUsers(Array.isArray(response.data) ? response.data : [])
    } catch (err) {
      setError('Error al cargar los usuarios')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateUser = async (e) => {
    e.preventDefault()
    setError('')

    try {
      await api.post('/auth/users', formData)
      setShowCreateForm(false)
      setFormData({ email: '', password: '', role: 'operador' })
      fetchUsers()
      alert('Usuario creado exitosamente')
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al crear el usuario')
    }
  }

  const handleToggleStatus = async (email, currentStatus) => {
    try {
      if (currentStatus) {
        await api.put(`/admin/users/${email}/deactivate`)
      } else {
        await api.put(`/admin/users/${email}/activate`)
      }
      fetchUsers()
    } catch (err) {
      alert('Error al cambiar el estado del usuario')
    }
  }

  if (loading) {
    return <div className="loading">Cargando usuarios...</div>
  }

  return (
    <div className="gestion-usuarios">
      <div className="usuarios-header">
        <h2>Gestión de Usuarios</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn-primary"
        >
          {showCreateForm ? 'Cancelar' : '+ Crear Usuario'}
        </button>
      </div>

      {showCreateForm && (
        <div className="create-user-form">
          <h3>Crear Nuevo Usuario</h3>
          {error && <div className="alert error">{error}</div>}
          <form onSubmit={handleCreateUser}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group">
              <label>Contraseña</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
                minLength={6}
              />
            </div>
            <div className="form-group">
              <label>Rol</label>
              <select
                value={formData.role}
                onChange={(e) =>
                  setFormData({ ...formData, role: e.target.value })
                }
              >
                <option value="operador">Operador</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn-primary">
                Crear Usuario
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="users-table-container">
        {/* Vista de tabla para desktop */}
        <table className="users-table">
          <thead>
            <tr>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="4" className="no-data">
                  No hay usuarios registrados
                </td>
              </tr>
            ) : (
              users.map((user) => (
                <tr key={user.email}>
                  <td>{user.email}</td>
                  <td>
                    <span className={`badge ${user.role === 'admin' ? 'admin' : 'operador'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${user.active ? 'active' : 'inactive'}`}>
                      {user.active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => handleToggleStatus(user.email, user.active)}
                      className={`btn-toggle ${user.active ? 'deactivate' : 'activate'}`}
                    >
                      {user.active ? 'Desactivar' : 'Activar'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Vista de cards para móviles */}
        <div className="users-cards-container">
          {users.length === 0 ? (
            <div className="no-data-card">
              No hay usuarios registrados
            </div>
          ) : (
            users.map((user) => (
              <div key={user.email} className="user-card">
                <div className="card-header">
                  <h3>{user.email}</h3>
                </div>
                <div className="card-body">
                  <div className="card-field">
                    <span className="card-label">Rol:</span>
                    <span className={`badge ${user.role === 'admin' ? 'admin' : 'operador'}`}>
                      {user.role}
                    </span>
                  </div>
                  <div className="card-field">
                    <span className="card-label">Estado:</span>
                    <span className={`badge ${user.active ? 'active' : 'inactive'}`}>
                      {user.active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>
                <div className="card-actions">
                  <button
                    onClick={() => handleToggleStatus(user.email, user.active)}
                    className={`btn-toggle ${user.active ? 'deactivate' : 'activate'}`}
                  >
                    {user.active ? 'Desactivar' : 'Activar'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default GestionUsuarios
