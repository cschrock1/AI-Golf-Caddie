import api from './api'

const TOKEN_KEY = 'aigc_token'

export async function register(payload: { full_name?: string; email: string; password: string }) {
  const res = await api.post('/auth/register', payload)
  return res.data
}

export async function login(payload: { email: string; password: string }) {
  const res = await api.post('/auth/token', payload)
  const token = res.data.access_token
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }
  return res.data
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY)
  delete api.defaults.headers.common['Authorization']
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setAuthHeaderFromStorage() {
  const t = getToken()
  if (t) api.defaults.headers.common['Authorization'] = `Bearer ${t}`
}
