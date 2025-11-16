<script setup>
import { ref, watch } from 'vue'
import api from '../api/http'
import { AUTH } from '../api/endpoints'

const props = defineProps({
  // opcjonalnie możesz przekazać domyślny e-mail z formularza
  initialEmail: {
    type: String,
    default: '',
  },
})

const isOpen = ref(false)
const email = ref(props.initialEmail)
const isLoading = ref(false)
const message = ref('')
const error = ref('')

// jeśli initialEmail się zmieni (np. użytkownik wpisze mail w innym polu),
// możemy go zsynchronizować:
watch(
  () => props.initialEmail,
  (val) => {
    if (!email.value) {
      email.value = val || ''
    }
  }
)

async function submit() {
  message.value = ''
  error.value = ''

  if (!email.value) {
    error.value = 'Podaj adres e-mail.'
    return
  }

  isLoading.value = true
  try {
    await api.post(AUTH.passwordResetRequest, {
      email: email.value,
    })
    message.value =
      'Jeśli podany adres istnieje w systemie, wysłaliśmy link do resetu hasła.'
  } catch (e) {
    // backend i tak zwraca ten sam komunikat, ale jakby coś się wywaliło:
    error.value = 'Nie udało się wysłać prośby o reset hasła.'
  } finally {
    isLoading.value = false
  }
}

function toggle() {
  isOpen.value = !isOpen.value
  // wyczyść komunikaty przy każdym otwarciu
  if (isOpen.value) {
    message.value = ''
    error.value = ''
  }
}
</script>

<template>
  <div style="margin-top:1rem;text-align:left;">
    <button
      type="button"
      @click="toggle"
      style="background:none;border:none;color:#4da3ff;cursor:pointer;padding:0;font-size:0.9rem;"
    >
      Nie pamiętasz hasła?
    </button>

    <div v-if="isOpen" style="margin-top:0.75rem;">
      <label style="display:block;font-size:0.9rem;margin-bottom:0.25rem;">
        Podaj adres e-mail powiązany z kontem:
      </label>
      <input
        v-model="email"
        type="email"
        autocomplete="email"
        style="width:100%;max-width:320px;padding:0.4rem;border-radius:6px;border:1px solid #555;background:#333;color:#eee;"
      />

      <button
        type="button"
        @click="submit"
        :disabled="isLoading"
        style="display:block;margin-top:0.5rem;padding:0.4rem 1.2rem;border-radius:8px;border:none;background:#000;color:#fff;cursor:pointer;font-size:0.9rem;"
      >
        {{ isLoading ? 'Wysyłanie…' : 'Wyślij link resetujący' }}
      </button>

      <p v-if="message" style="margin-top:0.5rem;font-size:0.85rem;color:#52c41a;">
        {{ message }}
      </p>
      <p v-if="error" style="margin-top:0.5rem;font-size:0.85rem;color:#ff4d4f;">
        {{ error }}
      </p>
    </div>
  </div>
</template>
