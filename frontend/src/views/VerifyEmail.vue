<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/http'
import { AUTH } from '../api/endpoints'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const status = ref('pending')   // 'pending' | 'ok' | 'error'
const message = ref('Weryfikuję link...')

onMounted(async () => {
  const uid = route.query.uid
  const token = route.query.token

  if (!uid || !token) {
    status.value = 'error'
    message.value = 'Brak danych w linku weryfikacyjnym.'
    return
  }

  try {
    const { data } = await api.post(AUTH.verifyEmail, { uid, token })
    status.value = 'ok'
    message.value = data.detail || 'Adres e-mail został potwierdzony.'

    // jeśli użytkownik był już zalogowany, możemy zaktualizować go w store
    if (auth.isAuthenticated && auth.user) {
      auth.user = { ...auth.user, is_verified: true }
      // i przerzucić na home
      router.push({ name: 'home' })
    }
  } catch (e) {
    status.value = 'error'
    message.value =
      e.response?.data?.detail || 'Link jest nieprawidłowy lub wygasł.'
  }
})
</script>

<template>
  <section
    style="max-width:480px;margin:3rem auto;text-align:center;border:1px solid #555;padding:2rem;border-radius:16px;background:#222;color:#eee;"
  >
    <h2>Weryfikacja adresu e-mail</h2>
    <p style="margin-top:1rem;">{{ message }}</p>

    <button
      v-if="status !== 'pending' && !auth.isAuthenticated"
      @click="router.push({ name: 'login' })"
      style="margin-top:1.5rem;padding:.6rem 1.8rem;border-radius:10px;border:none;background:#000;color:#fff;cursor:pointer;"
    >
      Przejdź do logowania
    </button>
  </section>
</template>
