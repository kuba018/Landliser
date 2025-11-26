<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/http'
import { PARCEL } from '../api/endpoints'

const parcels = ref([])
const isLoading = ref(false)
const error = ref('')
const parcelIdInput = ref('')
const editingCriterionId = ref(null)
const editForm = ref({
  description: '',
  area_m2: '',
  rate_per_m2: '',
})

// która działka ma rozwinięte szczegóły
const expandedParcelId = ref(null)

// szczegóły działek i kryteria
const parcelDetails = ref({})   // { [id]: parcelDetail }
const criteriaByParcel = ref({}) // { [id]: [criteria] }
const criteriaLoading = ref({})  // { [id]: boolean }
const criteriaError = ref({})    // { [id]: string }
const newCriteria = ref({})      // { [id]: { description, area_m2, rate_per_m2 } }

function ensureCriteriaForm(parcelId) {
  if (!newCriteria.value[parcelId]) {
    newCriteria.value[parcelId] = {
      description: '',
      area_m2: '',
      rate_per_m2: '',
    }
  }
}

function startEditingCriterion(criterion) {
  editingCriterionId.value = criterion.id
  editForm.value = {
    description: criterion.description,
    area_m2: criterion.area_m2,
    rate_per_m2: criterion.rate_per_m2,
  }
}

function cancelEditing() {
  editingCriterionId.value = null
}

async function saveEditedCriterion(parcel, criterion) {
  const id = criterion.id
  criteriaLoading.value[parcel.id] = true

  try {
    await api.patch(PARCEL.criterionDetail(id), {
      description: editForm.value.description,
      area_m2: editForm.value.area_m2,
      rate_per_m2: editForm.value.rate_per_m2,
    })

    // po aktualizacji przelicz podatek
    await recalcAndFetchDetails(parcel.id)

    editingCriterionId.value = null
  } catch (e) {
    console.error(e)
    criteriaError.value[parcel.id] = 'Nie udało się zaktualizować kryterium.'
  } finally {
    criteriaLoading.value[parcel.id] = false
  }
}


/**
 * PRZELICZA podatek dla działki na backendzie
 * (POST /api/parcels/{id}/calculate-tax/)
 * i odświeża:
 * - total_tax_amount w tabeli,
 * - listę kryteriów (do widoku szczegółów).
 */
async function recalcAndFetchDetails(parcelId) {
  criteriaLoading.value[parcelId] = true
  criteriaError.value[parcelId] = ''

  try {
    const { data } = await api.post(PARCEL.calculateTax(parcelId))

    // backend zwraca {"parcel": {...}, ...} – bierzemy parcel
    const parcelData = data.parcel || data

    parcelDetails.value[parcelId] = parcelData
    criteriaByParcel.value[parcelId] = parcelData.criteria || []

    // podmień łączny podatek w głównej tabeli
    const idx = parcels.value.findIndex(p => p.id === parcelId)
    if (idx !== -1) {
      parcels.value[idx] = {
        ...parcels.value[idx],
        total_tax_amount: parcelData.total_tax_amount,
      }
    }
  } catch (e) {
    console.error(e)
    criteriaError.value[parcelId] =
      'Nie udało się przeliczyć podatku dla tej działki.'
  } finally {
    criteriaLoading.value[parcelId] = false
  }
}

async function fetchParcels() {
  isLoading.value = true
  error.value = ''
  try {
    const { data } = await api.get(PARCEL.list)
    parcels.value = data

    // MOMENT 1: właśnie otworzyłeś widok "Działki"
    // po wczytaniu listy przeliczamy podatek dla każdej działki
    await Promise.all(
      parcels.value.map(p => recalcAndFetchDetails(p.id))
    )
  } catch (e) {
    console.error(e)
    error.value = 'Nie udało się pobrać listy działek.'
  } finally {
    isLoading.value = false
  }
}

async function handleScrape() {
  if (!parcelIdInput.value.trim()) return

  isLoading.value = true
  error.value = ''
  try {
    await api.post(PARCEL.scrape, {
      parcel_id: parcelIdInput.value.trim(),
    })
    parcelIdInput.value = ''
    await fetchParcels()
  } catch (e) {
    console.error(e)
    const detail = e?.response?.data?.detail
    error.value = detail || 'Nie udało się pobrać danych działki.'
  } finally {
    isLoading.value = false
  }
}

async function toggleParcelDetails(parcel) {
  const id = parcel.id

  // drugi klik – zwijamy
  if (expandedParcelId.value === id) {
    expandedParcelId.value = null
    return
  }

  expandedParcelId.value = id
  ensureCriteriaForm(id)

  // jeśli jeszcze nie mamy szczegółów (np. świeżo po resecie),
  // dociągnij je; podatek i tak już był przeliczany w fetchParcels
  if (!parcelDetails.value[id]) {
    await recalcAndFetchDetails(id)
  }
}

/**
 * MOMENT 2: dodajesz nowe kryterium do działki.
 * Po POST /criteria/ od razu wołamy calculate-tax dla tej działki.
 */
async function handleCreateCriterion(parcel) {
  const id = parcel.id
  ensureCriteriaForm(id)
  const form = newCriteria.value[id]

  if (!form.description || !form.area_m2 || !form.rate_per_m2) {
    criteriaError.value[id] = 'Uzupełnij wszystkie pola formularza.'
    return
  }

  criteriaLoading.value[id] = true
  criteriaError.value[id] = ''

  try {
    const payload = {
      parcel: id,
      description: form.description,
      area_m2: form.area_m2,
      rate_per_m2: form.rate_per_m2,
    }

    await api.post(PARCEL.criteria, payload)

    // wyczyść formularz
    newCriteria.value[id] = {
      description: '',
      area_m2: '',
      rate_per_m2: '',
    }

    // PRZELICZ PODATEK + odśwież kryteria
    await recalcAndFetchDetails(id)
  } catch (e) {
    console.error(e)
    const detail = e?.response?.data?.detail
    criteriaError.value[id] =
      detail || 'Nie udało się zapisać kryterium dla tej działki.'
  } finally {
    criteriaLoading.value[id] = false
  }
}

async function handleDeleteCriterion(parcel, criterion) {
  const parcelId = parcel.id

  const confirmed = window.confirm(
    'Czy na pewno chcesz usunąć to kryterium?'
  )
  if (!confirmed) return

  criteriaLoading.value[parcelId] = true
  criteriaError.value[parcelId] = ''

  try {
    await api.delete(PARCEL.criterionDetail(criterion.id))

    // sensownie jest też po usunięciu przeliczyć podatek
    await recalcAndFetchDetails(parcelId)
  } catch (e) {
    console.error(e)
    const detail = e?.response?.data?.detail
    criteriaError.value[parcelId] =
      detail || 'Nie udało się usunąć kryterium.'
  } finally {
    criteriaLoading.value[parcelId] = false
  }
}

async function handleDeleteParcel(parcel) {
  const confirmed = window.confirm(
    'Czy na pewno chcesz usunąć tę działkę wraz z jej kryteriami?'
  )
  if (!confirmed) return

  try {
    await api.delete(PARCEL.detail(parcel.id))

    parcels.value = parcels.value.filter(p => p.id !== parcel.id)
    delete parcelDetails.value[parcel.id]
    delete criteriaByParcel.value[parcel.id]

    if (expandedParcelId.value === parcel.id) {
      expandedParcelId.value = null
    }
  } catch (e) {
    console.error(e)
    const detail = e?.response?.data?.detail
    error.value = detail || 'Nie udało się usunąć działki.'
  }
}

onMounted(fetchParcels)
</script>

<template>
  <section class="card parcel-card">
    <header class="card-header">
      <h2 class="section-title">Twoje działki</h2>
      <p class="section-subtitle">
        Wpisz identyfikator działki (np. <code>146510_8.0605.77</code>),
        a aplikacja pobierze dane z ULDK i zapisze je na Twoim koncie.
      </p>
    </header>

    <form class="parcel-form" @submit.prevent="handleScrape">
      <div class="form-field">
        <label class="label" for="parcelId">Identyfikator działki</label>
        <input
          id="parcelId"
          v-model="parcelIdInput"
          type="text"
          class="input parcel-input"
          placeholder="np. 146510_8.0605.77"
        >
      </div>

      <button
        type="submit"
        class="btn btn-primary"
        :disabled="isLoading || !parcelIdInput.trim()"
      >
        {{ isLoading ? 'Przetwarzanie…' : 'Pobierz dane działki' }}
      </button>
    </form>

    <p v-if="error" class="error-text">{{ error }}</p>

    <div v-if="!parcels.length && !isLoading" class="empty-state">
      Nie masz jeszcze żadnych zapisanych działek.
    </div>

    <div v-else class="parcel-table-wrapper">
      <table class="table parcel-table">
        <thead>
          <tr>
            <th>Identyfikator</th>
            <th>Gmina / region</th>
            <th>Powierzchnia [m²]</th>
            <th>Podatek łączny</th>
            <th>Akcje</th>
          </tr>
        </thead>

        <tbody>
          <template v-for="parcel in parcels" :key="parcel.id">
            <!-- główny wiersz -->
            <tr>
              <td>{{ parcel.parcel_id || parcel.parcel_number }}</td>
              <td>{{ parcel.commune || parcel.region }}</td>
              <td>{{ parcel.area_m2 }}</td>
              <td>{{ parcel.total_tax_amount }}</td>
              <td class="parcel-actions-cell">
                <button
                  type="button"
                  class="btn btn-secondary btn-sm parcel-details-toggle"
                  @click="toggleParcelDetails(parcel)"
                >
                  {{ expandedParcelId === parcel.id ? 'Ukryj szczegóły' : 'Pokaż szczegóły' }}
                </button>

                <button
                  type="button"
                  class="btn btn-danger btn-sm parcel-delete-btn"
                  @click="handleDeleteParcel(parcel)"
                >
                  Usuń działkę
                </button>
              </td>
            </tr>

            <!-- rozwijany wiersz ze szczegółami -->
            <tr
              v-if="expandedParcelId === parcel.id"
              class="parcel-details-row"
            >
              <td :colspan="5">
                <div class="parcel-details">
                  <h3 class="parcel-details-title">
                    Kryteria podatkowe dla działki
                    <span class="parcel-details-id">
                      {{ parcel.parcel_id || parcel.parcel_number }}
                    </span>
                  </h3>

                  <p
                    v-if="criteriaError[parcel.id]"
                    class="criteria-error"
                  >
                    {{ criteriaError[parcel.id] }}
                  </p>

                  <p
                    v-else-if="criteriaLoading[parcel.id]"
                    class="criteria-loading"
                  >
                    Ładowanie kryteriów…
                  </p>

                  <ul
                    v-else-if="(criteriaByParcel[parcel.id] || []).length"
                    class="criteria-list"
                  >
                    <li
                      v-for="criterion in criteriaByParcel[parcel.id]"
                      :key="criterion.id"
                      class="criteria-item"
                    >
                      <div class="criteria-item-left" v-if="criterion.id !== editingCriterionId">
                        <div class="criteria-main">
                          {{ criterion.description }}
                        </div>
                        <div class="criteria-meta">
                          <span>Powierzchnia: {{ criterion.area_m2 }} m²</span>
                          <span>Stawka: {{ Number(criterion.rate_per_m2).toFixed(2) }} zł/m²</span>
                          <span>Podatek: {{ Number(criterion.tax_amount).toFixed(2) }} zł</span>
                        </div>
                      </div>

                      <!-- FORMULARZ EDYCJI -->
                      <div class="criteria-edit" v-else>
                        <input v-model="editForm.description" class="input small-input" />
                        <input v-model="editForm.area_m2" type="number" class="input small-input" />
                        <input v-model="editForm.rate_per_m2" type="number" class="input small-input" />

                        <button
                          class="btn btn-primary btn-sm"
                          @click="saveEditedCriterion(parcel, criterion)"
                        >
                          Zapisz
                        </button>

                        <button
                          class="btn btn-ghost-danger btn-sm"
                          @click="cancelEditing()"
                        >
                          Anuluj
                        </button>
                      </div>

                      <div class="criteria-actions" v-if="criterion.id !== editingCriterionId">
                        <button
                          class="btn btn-secondary btn-sm"
                          @click="startEditingCriterion(criterion)"
                        >
                          Edytuj
                        </button>

                        <button
                          type="button"
                          class="btn btn-ghost-danger btn-sm"
                          @click="handleDeleteCriterion(parcel, criterion)"
                        >
                          Usuń
                        </button>
                      </div>
                    </li>

                  </ul>

                  <p
                    v-else
                    class="criteria-empty"
                  >
                    Brak jeszcze zdefiniowanych kryteriów dla tej działki.
                  </p>

                  <!-- formularz dodania nowego kryterium -->
                  <form
                    class="criteria-form"
                    @submit.prevent="handleCreateCriterion(parcel)"
                  >
                    <h4 class="criteria-form-title">Dodaj nowe kryterium</h4>

                    <div class="criteria-fields">
                      <div class="criteria-field">
                        <label
                          class="label"
                          :for="`crit-desc-${parcel.id}`"
                        >
                          Opis
                        </label>
                        <input
                          :id="`crit-desc-${parcel.id}`"
                          v-model="newCriteria[parcel.id].description"
                          type="text"
                          class="input"
                          placeholder="np. Część działki pod zabudowę jednorodzinną"
                          required
                        >
                      </div>

                      <div class="criteria-field criteria-field--short">
                        <label
                          class="label"
                          :for="`crit-area-${parcel.id}`"
                        >
                          Powierzchnia [m²]
                        </label>
                        <input
                          :id="`crit-area-${parcel.id}`"
                          v-model="newCriteria[parcel.id].area_m2"
                          type="number"
                          min="0"
                          step="0.01"
                          class="input"
                          required
                        >
                      </div>

                      <div class="criteria-field criteria-field--short">
                        <label
                          class="label"
                          :for="`crit-rate-${parcel.id}`"
                        >
                          Stawka [zł/m²]
                        </label>
                        <input
                          :id="`crit-rate-${parcel.id}`"
                          v-model="newCriteria[parcel.id].rate_per_m2"
                          type="number"
                          min="0"
                          step="0.0001"
                          class="input"
                          required
                        >
                      </div>
                    </div>

                    <button
                      type="submit"
                      class="btn btn-primary btn-sm"
                      :disabled="criteriaLoading[parcel.id]"
                    >
                      {{ criteriaLoading[parcel.id] ? 'Zapisywanie…' : 'Zapisz kryterium' }}
                    </button>
                  </form>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </section>
</template>
<style scoped>
/* ---------- NAGŁÓWEK SEKCJI ---------- */

.card-header {
  margin-bottom: 16px;
}

.section-subtitle {
  margin-top: 4px;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

/* ---------- GŁÓWNA KARTA WIDOKU DZIAŁEK ---------- */

/* ten sam klimat co inne sekcje (łagodna szarość zamiast czystej bieli) */
.parcel-card {
  background-color: rgba(255,255,255,0.6);
  border-color: #959595;
  color: var(--text-main);
  padding: 16px 20px; /* było 24–32 — zmniejszamy */
  margin-top: 12px;   /* mniej odstępu od nawigacji */
  margin-bottom: 12px; /* mniej miejsca pod spodem */
}


/* ---------- FORMULARZ POBIERANIA DZIAŁKI ---------- */

.parcel-form {
  display: flex;
  gap: 16px;
  align-items: flex-end; /* dół w jednej linii */
  margin-bottom: 6px;
}

/* pole z etykietą – zajmuje resztę szerokości */
.parcel-form-field {
  flex: 1;
}

/* wyrównanie wysokości inputa i przycisku:
   zabieramy margines z globalnego .input tylko w tym formularzu */
.input {
background-color: rgba(210, 218, 230, 0.6);
border: 1px solid rgba(150, 160, 175, 0.5);
border-radius: 6px;
  margin-bottom: 0;
}

.parcel-input {
  background: rgba(255, 255, 255, 0.381)  ;
}

/* ---------- TABELA DZIAŁEK ---------- */

.parcel-table-wrapper {
  margin-top: 12px;
  /* kontener ze scrollbarem – rozwijanie kryteriów nie powiększa całej strony */
  max-height: 350px;
  overflow-y: auto;
  padding-right: 4px;
}

/* używamy globalnej .table do nagłówków / ramek,
   dokładamy tylko drobne doprecyzowanie dla wierszy */

.parcel-table tbody td {
  background: rgba(108, 149, 185, 0.327);
}



/* kolumna z przyciskami */
.parcel-actions-cell {
  gap: 10px;
  align-items: center;
  white-space: nowrap;
}

.parcel-details-toggle,
.parcel-delete-btn {
  padding: 6px 10px;
  font-size: 0.85rem;
}

/* ---------- ROZWIJANE SZCZEGÓŁY DZIAŁKI ---------- */

.parcel-details-row td {
  background: rgba(248, 250, 252, 0.95);
  padding: 16px 18px;
}

.parcel-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-radius: var(--radius-md);
  border: 2px solid #d0d7e2;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px 18px;
}

.parcel-details-title {
  margin: 0 0 4px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--primary-900);
}

.parcel-details-id {
  font-weight: 500;
  color: var(--primary-700);
}

/* cienka linia oddzielająca listę kryteriów od formularza */
.criteria-form {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #d0d7e2;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.criteria-form-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--primary-800);
}

.criteria-fields {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.criteria-field {
  flex: 1 1 220px;
}

.criteria-field--short {
  max-width: 200px;
}

/* ---------- LISTA KRYTERIÓW ---------- */

.criteria-list {
  list-style: none;
  padding: 0;
  margin: 0 0 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* pojedyncze kryterium – jasny segment z ramką */
.criteria-item {
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  background: rgba(108, 149, 185, 0.327);
  border: 1px solid #e2e8f0;

  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.btn{
  background-color: var(--primary-900);
  color :white;
}

.criteria-item-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.criteria-main {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--primary-800);
}

.criteria-meta {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.criteria-meta span + span {
  margin-left: 12px;
}

.criteria-empty,
.criteria-loading {
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.criteria-error {
  font-size: 0.9rem;
  color: var(--danger);
}

/* przyciski przy kryterium (Edytuj / Usuń) */
.criteria-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* formularz edycji kryterium (inline) */
.criteria-edit {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.small-input {
  width: 120px;
  padding: 4px 6px;
  font-size: 0.8rem;
}

/* ---------- WARIANTY PRZYCISKÓW ---------- */

.btn-danger {
  background: #b91c1c;
  border-color: #991b1b;
  color: #ffffff;
}

.btn-danger:hover {
  background: #991b1b;
}

.btn-ghost-danger {
  background: #b91c1c;
  border: 1px solid #991b1b;
  color: white;
}

.btn-ghost-danger:hover {
  background: #fee2e2;
}
</style>
