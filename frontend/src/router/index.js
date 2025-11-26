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
    name: 'login',          // to jest TWOJE logowanie
    component: LoginView,
  },
  {
    path: '/home',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: ResetPasswordView,
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: VerifyEmailView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // dostęp do /home bez zalogowania → wróć na '/'
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { path: '/' }
  }

  // opcjonalnie: jak user jest zalogowany i wejdzie na '/', przerzuć go na /home
  if (to.path === '/' && auth.isAuthenticated) {
    return { path: '/home' }
  }

  return true
})

export default router
