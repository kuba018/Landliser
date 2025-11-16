<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'
const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  // jeśli masz route o nazwie 'login'
  router.push({ name: 'login' })
  // albo zamiast tego:
  // router.push('/')   // jeśli '/' to login bez nazwy
}
</script>

<template>
  <main
    style="max-width:720px;margin:2rem auto;font-family:system-ui;color:#eee;background:#111;padding:1.5rem;border-radius:16px;border:1px solid #333;"
  >
    <header
      style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;border-bottom:1px solid #333;padding-bottom:.75rem;"
    >
      <h1 style="margin:0;font-size:1.6rem;">Landliser</h1>

      <div>
        <!-- jeśli NIE zalogowany -->
        <template v-if="!auth.isAuthenticated">
          <RouterLink
            to="/"
            style="margin-right:0.75rem;color:#4da3ff;text-decoration:none;"
          >
            Logowanie
          </RouterLink>
          <RouterLink
            to="/register"
            style="color:#4da3ff;text-decoration:none;"
          >
            Rejestracja
          </RouterLink>
        </template>

        <!-- jeśli zalogowany -->
        <template v-else>
          <span style="margin-right:0.75rem;font-size:0.9rem;opacity:.8;">
            Hi, {{ auth.user?.username || auth.user?.email }}
          </span>
          <button
            @click="handleLogout"
            style="padding:.35rem .9rem;border-radius:999px;border:1px solid #555;background:#222;color:#eee;cursor:pointer;font-size:0.85rem;"
          >
            Logout
          </button>
        </template>
      </div>
    </header>

    <!-- tu lądują widoki z routera: login, register, home itd. -->
    <RouterView />
  </main>
</template>
