<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['switchView'])

const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')

async function submit() {
  error.value = ''
  const ok = await auth.login({ username: username.value, password: password.value })
    .catch(() => false)
  if (!ok) error.value = 'Logowanie nieudane'
}
</script>

<template>
  <section style="border:1px solid #ddd;padding:1rem;border-radius:12px;">
    <h2>Logowanie</h2>
    <label>Login
      <input v-model="username" autocomplete="username" />
    </label>
    <label style="display:block;margin-top:.5rem;">Hasło
      <input type="password" v-model="password" autocomplete="current-password" />
    </label>

    <button style="margin-top:1rem;" @click="submit" :disabled="auth.isLoading">
      {{ auth.isLoading ? '...' : 'Zaloguj' }}
    </button>

    <p v-if="error" style="color:#b00;margin-top:.5rem;">{{ error }}</p>

    <p style="margin-top:.75rem;">
      Nie masz konta?
      <a href="#" @click.prevent="emit('switchView')">Zarejestruj się</a>
    </p>
  </section>
</template>
