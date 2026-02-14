import axios from 'axios'
import { getToken, removeToken } from './auth'

let baseURL = import.meta.env.VITE_API_URL || '/api'

// Si la URL es externa (http/https) y no termina en /api, agregar /api
if (baseURL.startsWith('http')) {
  // Remover barra final si existe
  baseURL = baseURL.replace(/\/$/, '')
  // Si no termina en /api, agregarlo
  if (!baseURL.endsWith('/api')) {
    baseURL = `${baseURL}/api`
  }
}

// Función helper para construir URLs completas de la API (útil para iframes, enlaces, etc.)
export const getApiUrl = (path) => {
  // Remover barra inicial si existe
  const cleanPath = path.startsWith('/') ? path.substring(1) : path
  
  // Si baseURL es relativo (empieza con /), simplemente concatenar
  if (baseURL.startsWith('/')) {
    return `${baseURL}/${cleanPath}`
  }
  
  // Si baseURL es absoluto (http/https), construir URL completa
  const base = baseURL.endsWith('/') ? baseURL.slice(0, -1) : baseURL
  return `${base}/${cleanPath}`
}

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
