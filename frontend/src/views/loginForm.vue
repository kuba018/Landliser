<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import InfoPanel from '../components/info.vue'
import ForgotPassword from '../components/ForgotPassword.vue'
import RegisterForm from '../components/RegisterForm.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

// 'login' albo 'register'
const mode = ref('login')

async function handleLogin() {
  error.value = ''

  try {
    await auth.login({
  username: username.value,
  password: password.value,
})

    router.push({ name: 'home' })
  } catch (e) {
    error.value = 'Nieprawidłowy login lub hasło.'
  }
}

function showRegister() {
  mode.value = 'register'
}

function showLogin() {
  mode.value = 'login'
}
</script>

<template>
  <div class="auth-layout">
    <!-- Lewa kolumna: Info -->
    <section class="auth-info-column">
      <InfoPanel />
    </section>

    <!-- Prawa kolumna: logowanie / rejestracja -->
    <section class="auth-form-column">
      <div class="auth-box">
        <h1 class="auth-logo">Landliser</h1>

        <!-- TRYB LOGOWANIA -->
        <template v-if="mode === 'login'">
          <h2 class="section-title" style="margin-bottom: 1rem; color: white;">
            Logowanie
          </h2>

          <form @submit.prevent="handleLogin">
            <div class="auth-input-group">
              <label class="label" for="username">Login</label>
              <input
                id="username"
                v-model="username"
                type="text"
                class="input"
                autocomplete="username"
              />
            </div>

            <div class="auth-input-group">
              <label class="label" for="password">Hasło</label>
              <input
                id="password"
                v-model="password"
                type="password"
                class="input"
                autocomplete="current-password"
              />
            </div>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="auth.isLoading"
            >
              {{ auth.isLoading ? 'Logowanie…' : 'Zaloguj' }}
            </button>

            <p v-if="error" class="auth-error">
              {{ error }}
            </p>
          </form>

          <div class="auth-links">
            <ForgotPassword />

            <p style="margin-top: 10px;">
              Nie masz konta?
              <button
                type="button"
                class="link-button"
                @click="showRegister"
              >
                Zarejestruj się
              </button>
            </p>
          </div>
        </template>

        <!-- TRYB REJESTRACJI -->
        <template v-else>
          <RegisterForm />

          <p class="auth-links" style="margin-top: 1.5rem;">
            Masz już konto?
            <button
              type="button"
              class="link-button"
              @click="showLogin"
            >
              Zaloguj się
            </button>
          </p>
        </template>
      </div>
    </section>
  </div>
</template>
