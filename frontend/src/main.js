// src/main.js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

// najpierw Pinia
const pinia = createPinia()
app.use(pinia)

// tutaj rehydratacja auth ze storage
const auth = useAuthStore(pinia)
auth.initFromStorage()

// dopiero potem router (który używa auth.isAuthenticated w guardach)
app.use(router)

// i dopiero na końcu montowanie
app.mount('#app')
