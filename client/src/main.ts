import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/tailwind.css'
import { setAuthHeaderFromStorage } from './services/auth'

setAuthHeaderFromStorage()

createApp(App).use(router).mount('#app')
