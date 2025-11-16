<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<template>
  <section>
    <h2>About me</h2>

    <div v-if="auth.user">
      <p><strong>Username:</strong> {{ auth.user.username }}</p>
      <p><strong>Email:</strong> {{ auth.user.email }}</p>
      <p><strong>Verified:</strong> {{ auth.user.is_verified ? 'Yes' : 'No' }}</p>
      <p v-if="auth.user.phone_number">
        <strong>Phone:</strong> {{ auth.user.phone_number }}
      </p>
    </div>

    <p v-else>
      You are not logged in.
    </p>
  </section>
</template>
