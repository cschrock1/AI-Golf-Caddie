<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-6">
    <div class="max-w-2xl text-center">
      <h1 class="text-4xl font-bold mb-4">AI Golf Caddie</h1>
      <p class="text-lg text-gray-700 mb-6">Personalized golf decisions powered by your game data.</p>
      <router-link to="/dashboard" class="inline-block px-4 py-2 bg-blue-600 text-white rounded">Go to Dashboard</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({ name: 'HomeView' })
</script>
