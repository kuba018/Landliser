<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/http'
import { AUTH } from '../api/endpoints'
import InfoPanel from '../components/info.vue'


const route = useRoute()
const router = useRouter()

const uid = ref(null)
const token = ref(null)

const newPassword = ref('')
const newPassword2 = ref('')

const loading = ref(false)
const error = ref('')
const message = ref('')

onMounted(() => {
  uid.value = route.query.uid
  token.value = route.query.token

  if (!uid.value || !token.value) {
    error.value = 'Link resetujący hasło jest nieprawidłowy lub niekompletny.'
  }
})

async function submit() {
  error.value = ''
  message.value = ''

  if (!uid.value || !token.value) {
    error.value = 'Brak danych resetu w linku.'
    return
  }
  if (!newPassword.value || !newPassword2.value) {
    error.value = 'Podaj nowe hasło w obu polach.'
    return
  }
  if (newPassword.value !== newPassword2.value) {
    error.value = 'Hasła nie są takie same.'
    return
  }

  loading.value = true
  try {
    await api.post(AUTH.passwordResetConfirm, {
      uid: uid.value,
      token: token.value,
      new_password: newPassword.value,
    })
    message.value = 'Hasło zostało zmienione. Możesz się teraz zalogować.'
    setTimeout(() => router.push({ name: 'login' }), 2500)
  } catch (e) {
    const resp = e.response?.data
    if (resp?.detail) {
      error.value = resp.detail
    } else if (resp && typeof resp === 'object') {
      const key = Object.keys(resp)[0]
      const msg = Array.isArray(resp[key]) ? resp[key][0] : String(resp[key])
      error.value = msg
    } else {
      error.value = 'Nie udało się zmienić hasła. Spróbuj ponownie.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-layout">
    <!-- Lewa kolumna: Info -->
    <section class="auth-info-column">
      <InfoPanel />
    </section>

    <!-- Prawa kolumna: ustawienie nowego hasła -->
    <section class="auth-form-column">
      <div class="auth-box">
        <h1 class="auth-logo">Landliser</h1>

        <h2 class="section-title" style="margin-bottom: 0.5rem; color: white;">
          Ustaw nowe hasło
        </h2>
        <p class="reset-subtitle">
          Otworzyłeś link z wiadomości e-mail. Ustaw nowe hasło dla swojego konta.
        </p>

        <!-- komunikaty -->
        <p
          v-if="error"
          class="field-error"
          style="margin-bottom: 0.75rem;"
        >
          {{ error }}
        </p>

        <p v-if="message" class="message-success">
          {{ message }}
        </p>

        <!-- formularz pokazujemy tylko jeśli nie ma jeszcze komunikatu sukcesu -->
        <form v-if="!message" @submit.prevent="submit">
          <div class="auth-input-group">
            <label class="label" for="new-password">Nowe hasło</label>
            <input
              id="new-password"
              v-model="newPassword"
              type="password"
              class="input"
              autocomplete="new-password"
            />
          </div>

          <div class="auth-input-group">
            <label class="label" for="new-password2">Powtórz nowe hasło</label>
            <input
              id="new-password2"
              v-model="newPassword2"
              type="password"
              class="input"
              autocomplete="new-password"
            />
          </div>

          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            {{ loading ? 'Zapisywanie…' : 'Zmień hasło' }}
          </button>
        </form>
      </div>
    </section>
  </div>
</template>

