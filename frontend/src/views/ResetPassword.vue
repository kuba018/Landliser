<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/http'
import { AUTH } from '../api/endpoints'


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
  <section
    style="border:1px solid #555;padding:2rem;border-radius:16px;max-width:420px;margin:3rem auto;background:#222;color:#eee;text-align:center;"
  >
    <h2 style="font-size:1.8rem;margin-bottom:1.5rem;">Ustaw nowe hasło</h2>

    <p style="font-size:0.9rem;opacity:.8;margin-bottom:1rem;">
      Wprowadź nowe hasło dla swojego konta.
    </p>

    <p v-if="error" style="color:#ff4d4f;margin-bottom:1rem;">{{ error }}</p>
    <p v-if="message" style="color:#65ff9a;margin-bottom:1rem;">{{ message }}</p>

    <div v-if="!message">
      <div style="text-align:left;">
        <label style="display:block;margin-bottom:.75rem;">
          Nowe hasło
          <input
            type="password"
            v-model="newPassword"
            autocomplete="new-password"
            style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
          />
        </label>

        <label style="display:block;margin-bottom:.75rem;">
          Powtórz nowe hasło
          <input
            type="password"
            v-model="newPassword2"
            autocomplete="new-password"
            style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
          />
        </label>
      </div>

      <button
        @click="submit"
        :disabled="loading"
        style="margin-top:1.5rem;padding:.6rem 1.8rem;border-radius:10px;border:none;background:#000;color:#fff;cursor:pointer;"
      >
        {{ loading ? 'Zapisywanie…' : 'Zmień hasło' }}
      </button>
    </div>
  </section>
</template>
