<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'

const auth = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => auth.isAuthenticated)

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div>
    <!-- Header pokazujemy tylko, gdy user jest zalogowany -->
    <div v-if="isAuthenticated" class="layout-container">
      <header class="app-header">
        <div class="logo">Landliser</div>

        <nav class="nav">
          <RouterLink
            :to="{ name: 'home' }"
            class="nav-link"
          >
            Strona główna
          </RouterLink>

          <RouterLink
            :to="{ name: 'register' }"
            class="nav-link"
          >
            Rejestracja
          </RouterLink>

          <button
            type="button"
            class="btn btn-primary"
            @click="handleLogout"
          >
            Wyloguj
          </button>
        </nav>
      </header>
    </div>

    <!-- Tu wchodzą widoki z routera (login, home itd.) -->
    <RouterView />
  </div>
</template>
