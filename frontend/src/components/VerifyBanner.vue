<script setup>
const props = defineProps({
  email: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div
    style="padding:0.75rem 1rem;margin-bottom:1rem;border-radius:10px;background:#332b00;color:#ffd666;font-size:0.95rem;"
  >
    <strong>Adres e-mail nie został jeszcze potwierdzony.</strong>
    <span v-if="email"> ({{ email }})</span>
    <br />
    Sprawdź skrzynkę pocztową i kliknij w link aktywacyjny, aby odblokować pełne funkcje (np. widok działek).
  </div>
</template>
