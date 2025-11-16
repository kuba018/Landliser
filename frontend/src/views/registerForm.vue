<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import api from '../api/http'
import { AUTH } from '../api/endpoints'
import ForgotPassword from '../components/ForgotPassword.vue'

const username = ref('')
const email = ref('')
const password = ref('')
const confirm = ref('')

const message = ref('')
const error = ref('')
const fieldErrors = ref({})
const passwordHelp = ref('')
const passwordError = ref('')

async function submit() {
  message.value = ''
  error.value = ''
  fieldErrors.value = {}
  passwordError.value = ''

  if (password.value !== confirm.value) {
    passwordError.value = 'Hasła muszą być takie same.'
    return
  }

  try {
    const { data } = await api.post(AUTH.register, {
      username: username.value,
      email: email.value,
      password: password.value,
    })
    message.value = data.detail || 'Konto utworzone. Sprawdź e-mail, aby je aktywować.'
  } catch (e) {
    const r = e.response?.data
    if (r?.password) {
      passwordError.value = Array.isArray(r.password) ? r.password.join(' ') : String(r.password)
    } else if (typeof r === 'object') {
      fieldErrors.value = r
      error.value = 'Niepoprawne dane.'
    } else {
      error.value = 'Rejestracja nie powiodła się.'
    }
  }
}
</script>

<template>
  <section
    style="border:1px solid #555;padding:2rem;border-radius:16px;max-width:420px;margin:3rem auto;background:#222;color:#eee;text-align:center;"
  >
    <h2 style="font-size:1.8rem;margin-bottom:1.5rem;">Rejestracja</h2>

    <div style="text-align:left;">
      <label style="display:block;margin-bottom:.5rem;">
        Nazwa użytkownika
        <input
          v-model="username"
          autocomplete="username"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
        <span v-if="fieldErrors.username" style="color:#ff4d4f;font-size:.85rem;">
          {{ fieldErrors.username.join ? fieldErrors.username.join(' ') : fieldErrors.username }}
        </span>
      </label>

      <label style="display:block;margin-top:.75rem;margin-bottom:.5rem;">
        E-mail
        <input
          v-model="email"
          type="email"
          autocomplete="email"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
        <span v-if="fieldErrors.email" style="color:#ff4d4f;font-size:.85rem;">
          {{ fieldErrors.email.join ? fieldErrors.email.join(' ') : fieldErrors.email }}
        </span>
      </label>

      <label style="display:block;margin-top:.75rem;margin-bottom:.5rem;">
        Hasło
        <input
          type="password"
          v-model="password"
          autocomplete="new-password"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
        <span v-if="passwordError" style="color:#ff4d4f;font-size:.85rem;">{{ passwordError }}</span>
        <span v-else-if="passwordHelp" style="font-size:.85rem;opacity:.8;">{{ passwordHelp }}</span>
      </label>

      <label style="display:block;margin-top:.75rem;margin-bottom:.5rem;">
        Powtórz hasło
        <input
          type="password"
          v-model="confirm"
          autocomplete="new-password"
          style="width:100%;margin-top:.25rem;padding:.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
        />
      </label>
    </div>

    <button
      @click="submit"
      style="margin-top:1.5rem;padding:.6rem 1.8rem;border-radius:10px;border:none;background:#000;color:#fff;cursor:pointer;"
    >
      Zarejestruj
    </button>

    <p v-if="message" style="color:#52c41a;margin-top:1rem;">{{ message }}</p>
    <p v-if="error" style="color:#ff4d4f;margin-top:1rem;">{{ error }}</p>

    <p style="margin-top:1.5rem;">
      Masz już konto?
      <RouterLink to="/" style="color:#4da3ff;">Zaloguj się</RouterLink>
    </p>

    <ForgotPassword :initial-email="email" />
  </section>
</template>
