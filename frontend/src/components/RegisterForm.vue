<script setup>
import { ref } from 'vue'
import api from '../api/http'
import { AUTH } from '../api/endpoints'

const username = ref('')
const email = ref('')
const password = ref('')
const confirm = ref('')

const message = ref('')
const error = ref('')
const fieldErrors = ref({})
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

    message.value =
      data.detail ||
      'Konto utworzone. Sprawdź e-mail, aby je aktywować.'
  } catch (e) {
    const r = e.response?.data
    if (r?.password) {
      passwordError.value = Array.isArray(r.password)
        ? r.password.join(' ')
        : String(r.password)
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
  <div>
    <h2 class="section-title" style="margin-bottom: 1rem; color: white;">
  Rejestracja
</h2>

    <div>
      <div class="auth-input-group">
        <label class="label" for="reg-username">Nazwa użytkownika</label>
        <input
          id="reg-username"
          v-model="username"
          autocomplete="username"
          class="input"
        />
        <p v-if="fieldErrors.username" class="field-error">
          {{
            fieldErrors.username.join
              ? fieldErrors.username.join(' ')
              : fieldErrors.username
          }}
        </p>
      </div>

      <div class="auth-input-group">
        <label class="label" for="reg-email">E-mail</label>
        <input
          id="reg-email"
          v-model="email"
          type="email"
          autocomplete="email"
          class="input"
        />
        <p v-if="fieldErrors.email" class="field-error">
          {{
            fieldErrors.email.join
              ? fieldErrors.email.join(' ')
              : fieldErrors.email
          }}
        </p>
      </div>

      <div class="auth-input-group">
        <label class="label" for="reg-password">Hasło</label>
        <input
          id="reg-password"
          v-model="password"
          type="password"
          autocomplete="new-password"
          class="input"
        />
      </div>

      <div class="auth-input-group">
        <label class="label" for="reg-confirm">Powtórz hasło</label>
        <input
          id="reg-confirm"
          v-model="confirm"
          type="password"
          autocomplete="new-password"
          class="input"
        />
        <p v-if="passwordError" class="field-error">
          {{ passwordError }}
        </p>
      </div>
    </div>

    <button
      type="button"
      class="btn btn-primary"
      @click="submit"
    >
      Zarejestruj
    </button>

    <p v-if="message" class="message-success">
      {{ message }}
    </p>

    <p
      v-if="error"
      class="field-error"
      style="margin-top: 0.75rem;"
    >
      {{ error }}
    </p>
  </div>
</template>
