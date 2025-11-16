<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import VerifyBanner from '../components/VerifyBanner.vue'
import InfoView from '../components/info.vue'
import UserView from '../components/user.vue'
import ParcelView from '../components/parcel.vue'

const auth = useAuthStore()

// zakładki: info | user | parcel
const currentTab = ref('info')

const canSeeParcels = computed(() =>
  auth.isAuthenticated && auth.user?.is_verified
)
</script>

<template>
  <section>
    <h2>Home</h2>

    <!-- jeśli chcesz, możesz coś pokazać gościom -->
    <p v-if="!auth.isAuthenticated" style="margin-bottom:1rem;">
      You are not logged in. Some features may be limited.
    </p>

    <!-- Baner o weryfikacji maila, jeśli chcesz (inaczej usuń ten kawałek) -->
    <VerifyBanner
      v-if="auth.isAuthenticated && !auth.user?.is_verified"
      v-model:email="auth.user.email"
      style="margin-bottom:1rem;"
    />

    <!-- Nawigacja zakładek -->
    <nav style="display:flex;gap:.5rem;border-bottom:1px solid #eee;margin-bottom:1rem;">
      <button :class="{active: currentTab==='info'}" @click="currentTab='info'">
        Fast info
      </button>
      <button :class="{active: currentTab==='user'}" @click="currentTab='user'">
        About me
      </button>
      <button
        :class="{active: currentTab==='parcel'}"
        :disabled="!canSeeParcels"
        :title="canSeeParcels ? '' : 'Verify your email to access parcels.'"
        @click="canSeeParcels && (currentTab='parcel')"
      >
        My parcels
      </button>
    </nav>

    <!-- Widoki wewnątrz Home -->
    <InfoView v-if="currentTab==='info'" />
    <UserView v-else-if="currentTab==='user'" />
    <ParcelView v-else-if="currentTab==='parcel' && canSeeParcels" />
  </section>
</template>

<style scoped>
button.active {
  border-bottom: 2px solid #333;
}
button[disabled] {
  opacity: .6;
  cursor: not-allowed;
}
</style>
