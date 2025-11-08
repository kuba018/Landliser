<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/http';

const me = ref(null);
const err = ref('');

onMounted(async () => {
  try {
    const { data } = await api.get('/api/auth/me/');
    me.value = data;
  } catch { err.value = 'Nie udało się pobrać /auth/me'; }
});
</script>

<template>
  <section style="border:1px solid #ddd;padding:1rem;border-radius:12px;">
    <pre v-if="me">{{ JSON.stringify(me, null, 2) }}</pre>
    <p v-else-if="err" style="color:#b00">{{ err }}</p>
    <p v-else>Ładowanie...</p>
  </section>
</template>
