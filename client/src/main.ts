import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/tailwind.css'
import { setAuthHeaderFromStorage } from './services/auth'
import { authStore } from './stores/auth'

setAuthHeaderFromStorage()

createApp(App).use(router).mount('#app')
void authStore.loadUser()
