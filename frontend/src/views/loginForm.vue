<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import ForgotPassword from '../components/ForgotPassword.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')

// komunikat po weryfikacji maila
const msg = ref('')

onMounted(() => {
  // Czytamy parametr ?verified=1 z URL-a
  try {
    const url = new URL(window.location.href)
    const verified = url.searchParams.get('verified')

    if (verified === '1') {
      msg.value = 'Twój adres e-mail został pomyślnie zweryfikowany. Możesz się teraz zalogować.'

      // Usuwamy parametr z URL, żeby komunikat nie pokazywał się przy każdym odświeżeniu
      url.searchParams.delete('verified')
      window.history.replaceState({}, '', url)
    }
  } catch (e) {
    // jakby coś nie poszło z URL-em, po prostu ignorujemy
  }
})

async function submit() {
  error.value = ''
  const ok = await auth
    .login({
      username: username.value,
      password: password.value,
    })
    .catch(() => false)

  if (!ok) {
    error.value = 'Logowanie nieudane'
  } else {
    router.push({ name: 'home' }) // po zalogowaniu na /home
  }
}
</script>

<template>
  <section
    style="border:1px solid #555;padding:2rem;border-radius:16px;max-width:420px;margin:3rem auto;background:#222;color:#eee;text-align:center;"
  >
    <!-- Komunikat po weryfikacji maila -->
    <div
      v-if="msg"
      style="background:#16351f;border:1px solid #32a852;padding:.75rem 1rem;margin-bottom:1rem;border-radius:10px;color:#dfffe8;text-align:left;font-size:0.9rem;"
    >
      {{ msg }}
    </div>

    <h2 style="font-size:1.8rem;margin-bottom:1.5rem;">Logowanie</h2>

    <div style="text-align:left;">
      <label style="display:block;margin-bottom:.5rem;">
        Login lub e-mail
        <input
          v-model="username"
          autocomplete="username"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
      </label>

      <label style="display:block;margin-top:.75rem;margin-bottom:.5rem;">
        Hasło
        <input
          type="password"
          v-model="password"
          autocomplete="current-password"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
      </label>
    </div>

    <button
      @click="submit"
      :disabled="auth.isLoading"
      style="margin-top:1.5rem;padding:.6rem 1.8rem;border-radius:10px;border:none;background:#000;color:#fff;cursor:pointer;"
    >
      {{ auth.isLoading ? 'Logowanie…' : 'Zaloguj' }}
    </button>

    <p v-if="error" style="color:#ff4d4f;margin-top:1rem;">{{ error }}</p>

    <ForgotPassword />

    <p style="margin-top:1.5rem;">
      Nie masz konta?
      <RouterLink to="/register" style="color:#4da3ff;">Zarejestruj się</RouterLink>
    </p>
  </section>
</template>
