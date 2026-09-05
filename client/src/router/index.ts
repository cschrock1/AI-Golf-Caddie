import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import ProfileView from '../views/ProfileView.vue'
import ClubsView from '../views/ClubsView.vue'

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/profile', name: 'Profile', component: ProfileView }
  ,{ path: '/clubs', name: 'Clubs', component: ClubsView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
