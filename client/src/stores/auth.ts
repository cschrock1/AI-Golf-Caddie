import { computed, ref } from 'vue'
import { getCurrentUser } from '../services/api'
import { getToken, logout as clearAuth } from '../services/auth'

const isAuthenticated = ref(Boolean(getToken()))
const user = ref<{ id: number; email: string; full_name?: string | null } | null>(null)
const loading = ref(false)
const error = ref('')

async function loadUser() {
  const token = getToken()
  if (!token) {
    isAuthenticated.value = false
    user.value = null
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await getCurrentUser()
    user.value = response.data
    isAuthenticated.value = true
  } catch {
    clearAuth()
    user.value = null
    isAuthenticated.value = false
    error.value = 'Your session expired. Please log in again.'
  } finally {
    loading.value = false
  }
}

function setLoggedInUser(nextUser: { id: number; email: string; full_name?: string | null } | null) {
  user.value = nextUser
  isAuthenticated.value = Boolean(nextUser)
}

function signOut() {
  clearAuth()
  user.value = null
  isAuthenticated.value = false
}

export const authStore = {
  isAuthenticated: computed(() => isAuthenticated.value),
  user: computed(() => user.value),
  loading: computed(() => loading.value),
  error: computed(() => error.value),
  loadUser,
  setLoggedInUser,
  signOut
}
