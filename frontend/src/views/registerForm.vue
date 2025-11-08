<script setup>
import { ref } from 'vue'
import api from '../api/http'
import { AUTH } from '../api/endpoints'

const username = ref('')
const email = ref('')
const password = ref('')
const confirm = ref('')

const message = ref('')
const error = ref('')              // ogólny fallback
const fieldErrors = ref({})        // błędy per pole: { username: '...', password: '...' }

function resetErrors() {
  error.value = ''
  fieldErrors.value = {}
}

function setFieldErrors(data) {
  // DRF zwykle zwraca { field: [msg1, msg2], non_field_errors: [...] }
  Object.entries(data || {}).forEach(([key, val]) => {
    const msgs = Array.isArray(val) ? val.join(' ') : String(val)
    fieldErrors.value[key] = msgs
  })
}

async function register() {
  resetErrors()
  message.value = ''

  if (password.value !== confirm.value) {
    fieldErrors.value.password = 'Passwords do not match.'
    return
  }

  try {
    await api.post(AUTH.register, {
      username: username.value,
      email: email.value,
      password: password.value,
    })

    message.value = 'Registration successful! You can now log in.'
    username.value = ''
    email.value = ''
    password.value = ''
    confirm.value = ''
  } catch (err) {
    const status = err.response?.status
    const data = err.response?.data

    if (status === 400 && data) {
      setFieldErrors(data)

      // Priorytet: pokaż dokładny błąd hasła, jeśli jest
      if (fieldErrors.value.password) return

      // Jak nie ma błędu hasła, pokaż inny błąd z pól lub non_field_errors
      error.value =
        fieldErrors.value.username ||
        fieldErrors.value.email ||
        fieldErrors.value.non_field_errors ||
        'Validation error.'
    } else {
      error.value = 'Server error. Please try again later.'
    }
  }
}
</script>

<template>
  <section style="border:1px solid #ddd;padding:1rem;border-radius:12px;">
    <h2>Rejestracja</h2>

    <label>Login
      <input v-model="username" />
    </label>
    <p v-if="fieldErrors.username" style="color:#b00;margin:.25rem 0 0;">
      {{ fieldErrors.username }}
    </p>

    <label style="display:block;margin-top:.5rem;">Email
      <input type="email" v-model="email" />
    </label>
    <p v-if="fieldErrors.email" style="color:#b00;margin:.25rem 0 0;">
      {{ fieldErrors.email }}
    </p>

    <label style="display:block;margin-top:.5rem;">Hasło
      <input type="password" v-model="password" />
    </label>
    <!-- Dokładne komunikaty z walidatora hasła -->
    <p v-if="fieldErrors.password" style="color:#b00;margin:.25rem 0 0;">
      {{ fieldErrors.password }}
    </p>

    <label style="display:block;margin-top:.5rem;">Powtórz hasło
      <input type="password" v-model="confirm" />
    </label>

    <button style="margin-top:1rem;" @click="register">Zarejestruj</button>

    <p v-if="message" style="color:green;margin-top:.5rem;">{{ message }}</p>
    <p v-if="error" style="color:#b00;margin-top:.5rem;">{{ error }}</p>
  </section>
</template>
