// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import VerifyEmailView from '../views/VerifyEmail.vue'
import HomeView from '../views/home.vue'
import LoginView from '../views/loginForm.vue'
import ResetPasswordView from '../views/ResetPassword.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },   // ⬅️ wymaga zalogowania
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: ResetPasswordView,    
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// globalny guard
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    // jeśli próbuje wejść na /home bez logowania → na / (login)
    return { name: 'login' }
  }

  // jeśli user zalogowany i idzie na / lub /login → przerzuć na /home
  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'home' }
  }

  return true
})

export default router
