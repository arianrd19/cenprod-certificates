import axios from 'axios'
import { getToken, removeToken } from './auth'

const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: baseURL.endsWith('/') ? baseURL : `${baseURL}/`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token y corregir rutas
api.interceptors.request.use(
  (config) => {
    // Si la URL empieza con /, se la quitamos para que se concatene correctamente con el baseURL
    if (config.url && config.url.startsWith('/')) {
      config.url = config.url.substring(1)
    }

    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
