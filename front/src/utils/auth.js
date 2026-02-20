const USER_KEY = 'user_data'

export const getToken = () => {
  return null
}

export const setToken = () => {
  // Token is stored in HttpOnly cookie by backend.
}

export const removeToken = () => {
  localStorage.removeItem(USER_KEY)
}

export const getUser = () => {
  const userData = localStorage.getItem(USER_KEY)
  return userData ? JSON.parse(userData) : null
}

export const setUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}
