<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api/http'
import { AUTH } from '../api/endpoints'

const auth = useAuthStore()
const router = useRouter()

const isDeleting = ref(false)

async function handleDeleteAccount() {
  if (!auth.user) return

  const confirmed = window.confirm(
    'Czy na pewno chcesz usunąć swoje konto? Tego nie da się cofnąć.'
  )

  if (!confirmed) {
    return
  }

  isDeleting.value = true

  try {
    await api.delete(AUTH.deleteAccount)

    // wyczyść stan po stronie frontu
    auth.logout?.()

    // wyrzucamy użytkownika na ekran startowy / logowania
    router.push({ path: '/' })
  } catch (e) {
    console.error(e)
    alert('Nie udało się usunąć konta. Spróbuj ponownie później.')
  } finally {
    isDeleting.value = false
  }
}
</script>


<template>
  <section class="card user-card">
    <header class="card-header">
      <h2 class="section-title">Moje konto</h2>
      <p class="section-subtitle">
        Podsumowanie danych przypisanych do Twojego profilu użytkownika.
      </p>
    </header>

    <!-- GŁÓWNE DANE UŻYTKOWNIKA -->
    <div v-if="auth.user" class="user-grid">

      <div class="user-row">
        <span class="user-label">Nazwa użytkownika</span>
        <span class="user-value">{{ auth.user.username }}</span>
      </div>

      <div class="user-row">
        <span class="user-label">Adres e-mail</span>
        <span class="user-value">{{ auth.user.email }}</span>
      </div>

      <div class="user-row">
        <span class="user-label">Zweryfikowane konto</span>
        <span
          class="user-value user-badge"
          :class="auth.user.is_verified ? 'user-badge--ok' : 'user-badge--pending'"
        >
          {{ auth.user.is_verified ? 'Tak' : 'Nie' }}
        </span>
      </div>

      <!-- STREFA USUWANIA KONTA -->
      <div class="user-danger">
        <h3 class="user-danger-title">Usuń konto</h3>
        <p class="user-danger-text">
          Ta operacja całkowicie usunie Twoje konto i wszystkie powiązane dane.
          Tego procesu nie można cofnąć.
        </p>

        <button
          class="btn btn-danger"
          type="button"
          @click="handleDeleteAccount"
          :disabled="isDeleting"
        >
          {{ isDeleting ? 'Usuwanie…' : 'Usuń konto' }}
        </button>
      </div>

    </div>

    <!-- UŻYTKOWNIK NIEZALOGOWANY -->
    <p v-else class="user-empty">
      Nie jesteś zalogowany.
    </p>

  </section>
</template>


<style scoped>
/* tło karty jak w działkach */
.user-card {
  background: rgba(255, 255, 255, 0.6);
  border-color: #d0d7e2;
}

/* nagłówek */
.card-header {
  margin-bottom: 16px;
}

.section-subtitle {
  margin-top: 4px;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* kontener na wiersze */
.user-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* KAŻDY WIERSZ: 2-kolumnowy grid */
.user-row {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(0, 3fr); /* ~70% / 30% */
  align-items: center;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #d0d7e2;
}

.user-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--primary-700);
}

/* prawa kolumna – wszystko dociskamy do prawej,
   ale w ramach tej 30% kolumny (czyli mniej więcej 3/4 szerokości paska) */
.user-value {
  font-size: 0.9rem;
  color: var(--primary-900);
  justify-self: end;
}

/* badge weryfikacji */
.user-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.user-badge--ok {
  background-color: rgba(34, 197, 94, 0.12);
  color: #16a34a;
}

.user-badge--pending {
  background-color: rgba(248, 181, 47, 0.16);
  color: #b45309;
}

.user-empty {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}
/* Wymuszenie gridu zamiast flexa – przebija globalne style */
.user-row {
  display: grid !important;
  grid-template-columns: 70% 30% !important;
  align-items: center !important;
}
.user-danger {
  margin-top: 18px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(239, 68, 68, 0.2);
  background: rgba(248, 113, 113, 0.06);
}

.user-danger-title {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #991b1b;
}

.user-danger-text {
  margin: 0 0 10px;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}


</style>
