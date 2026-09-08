import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import HoleView from '../views/HoleView.vue'
import CaddieView from '../views/CaddieView.vue'
import ScorecardView from '../views/ScorecardView.vue'
import BagView from '../views/BagView.vue'
import { authStore } from '../stores/auth'
import { getToken } from '../services/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView, meta: { requiresAuth: true } },
  { path: '/hole', name: 'Hole', component: HoleView, meta: { requiresAuth: true } },
  { path: '/caddie', name: 'Caddie', component: CaddieView, meta: { requiresAuth: true } },
  { path: '/scorecard', name: 'Scorecard', component: ScorecardView, meta: { requiresAuth: true } },
  { path: '/bag', name: 'Bag', component: BagView, meta: { requiresAuth: true } }
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
    return { path: '/dashboard' }
  }
})

export default router
