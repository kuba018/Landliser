<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import LoginForm from './views/LoginForm.vue'
import RegisterForm from './views/RegisterForm.vue'
import UserBox from './views/UserBox.vue'

const auth = useAuthStore()
const showRegister = ref(false)

onMounted(() => auth.initFromStorage())

function toggleView() {
  showRegister.value = !showRegister.value
}
</script>

<template>
  <main style="max-width:720px;margin:2rem auto;font-family:system-ui;">
    <header style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
      <h1>Landliser</h1>
      <div v-if="auth.isAuthenticated">
        <button @click="auth.logout()">Wyloguj</button>
      </div>
    </header>

    <section v-if="!auth.isAuthenticated">
      <LoginForm v-if="!showRegister" @switchView="toggleView" />
      <RegisterForm v-else />
      <p v-if="showRegister" style="margin-top:0.5rem;">
        Masz już konto?
        <a href="#" @click.prevent="toggleView">Zaloguj się</a>
      </p>
    </section>

    <section v-else style="margin-top:1rem;">
      <UserBox />
    </section>
  </main>
</template>
