import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../stores/auth'
import { getToken } from '../services/auth'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterView.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/hole', name: 'Hole', component: () => import('../views/HoleView.vue'), meta: { requiresAuth: true } },
  { path: '/caddie', name: 'Caddie', component: () => import('../views/CaddieView.vue'), meta: { requiresAuth: true } },
  { path: '/scorecard', name: 'Scorecard', component: () => import('../views/ScorecardView.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/bag', redirect: '/profile' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  if (getToken() && !authStore.isAuthenticated.value && authStore.user.value === null) {
    await authStore.loadUser()
  }

  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isAuthenticated = authStore.isAuthenticated.value

  if (requiresAuth && !isAuthenticated) {
    return { path: '/login' }
  }

  if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    return { path: '/hole' }
  }
})

export default router
