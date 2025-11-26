<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import VerifyBanner from '../components/VerifyBanner.vue'
import InfoView from '../components/info.vue'
import UserView from '../components/user.vue'
import ParcelView from '../components/parcel.vue'

const auth = useAuthStore()
const router = useRouter()

// zakładki: info | user | parcel
const currentTab = ref('info')

const canSeeParcels = computed(
  () => auth.isAuthenticated && auth.user?.is_verified
)

const handleLogout = () => {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="home-shell auth-info-column">
    <div class="home-inner">
      <!-- pasek o weryfikacji maila -->
      <VerifyBanner
        v-if="auth.isAuthenticated && !auth.user?.is_verified"
        class="home-banner"
      />

      <!-- nagłówek strony -->
      <section class="card home-header">
        <div class="home-header-main">
          <h1 class="home-title">
            Panel użytkownika
            <span v-if="auth.user?.username">
              – {{ auth.user.username }}
            </span>
          </h1>
          <p class="home-subtitle">
            Tutaj zarządzasz swoim kontem i pracujesz z danymi działek
            pobieranymi z ewidencji gruntów i budynków.
          </p>
        </div>
      </section>

      <!-- pasek zakładek + logout -->
      <section class="home-tabs">
        <nav class="home-tabs-nav">
          <div class="home-tabs-left">
            <button
              type="button"
              class="home-tab-btn"
              :class="{ 'home-tab-btn--active': currentTab === 'info' }"
              @click="currentTab = 'info'"
            >
              Informacje
            </button>

            <button
              type="button"
              class="home-tab-btn"
              :class="{ 'home-tab-btn--active': currentTab === 'user' }"
              @click="currentTab = 'user'"
            >
              Moje konto
            </button>

            <button
              type="button"
              class="home-tab-btn"
              :class="{ 'home-tab-btn--active': currentTab === 'parcel' }"
              :disabled="!canSeeParcels"
              @click="currentTab = 'parcel'"
            >
              Działki
            </button>
          </div>

          <button
            type="button"
            class="home-logout-btn"
            @click="handleLogout"
          >
            Wyloguj
          </button>
        </nav>

        <!-- zawartość zakładek -->
        <section class="home-content">
          <InfoView v-if="currentTab === 'info'" />
          <UserView v-else-if="currentTab === 'user'" />
          <ParcelView
            v-else-if="currentTab === 'parcel' && canSeeParcels"
          />
        </section>
      </section>
    </div>
  </div>
</template>

<style scoped>
.home-shell {
  min-height: 100vh;
  padding: 32px 16px;
}

.home-inner {
  max-width: 1100px;
  margin: 0 auto;
}

/* nagłówek */
.home-header {
  margin-bottom: 18px;
  background: var(--primary-700);
  border-color: var(--primary-600);
  color: var(--text-light);
}

.home-header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.home-title {
  margin: 0;
  font-size: 1.9rem;
  color: #ffffff;
}

.home-subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: #e5e7eb;
}

/* zakładki */
.home-tabs {
  margin-top: 10px;
}

/* NAV: granatowy pasek + flex: zakładki lewo, logout prawo */
.home-tabs-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 14px;
  margin-bottom: 12px;

  background: var(--primary-900);
  border: 1px solid var(--primary-700);
  border-radius: var(--radius-md);
  box-shadow: 0 18px 45px rgba(15, 23, 42, 0.45);
}

.home-tabs-left {
  display: flex;
  gap: 10px;
}

/* pojedynczy przycisk zakładki */
.home-tab-btn {
  background: transparent;
  border: none;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  font-weight: 500;
  color: #e5e7eb;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: var(--transition);
}

.home-tab-btn:hover:not([disabled]) {
  background: rgba(15, 23, 42, 0.4);
}

/* 3. Zmiana koloru podświetlenia zakładki (bez niebieskiego) */
.home-tab-btn--active {
  border-bottom-color: #5e6682a8; /* ciepły żółty na granacie */
  color: #ffffff;
}

.home-tab-btn[disabled] {
  opacity: 0.5;
  cursor: not-allowed;
}

/* logout na pasku */
.home-logout-btn {
  background: #ffffff;
  color: var(--primary-900);
  border-radius: 999px;
  padding: 8px 18px;
  border: 1px solid rgba(15, 23, 42, 0.45);
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.55);
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: var(--transition);
}

.home-logout-btn:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

/* zawartość zakładek */
.home-content {
  margin-top: 4px;
}

.home-banner {
  margin-bottom: 16px;
}
</style>
