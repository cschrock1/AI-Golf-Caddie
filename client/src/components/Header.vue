<template>
  <header class="bg-white shadow p-4 mb-6">
    <div class="max-w-4xl mx-auto flex justify-between items-center">
      <div class="font-bold text-lg">AI Golf Caddie</div>
      <nav class="flex gap-3 items-center">
        <router-link to="/" class="text-sm">Home</router-link>
        <router-link to="/dashboard" class="text-sm">Dashboard</router-link>
        <router-link v-if="!isAuth" to="/login" class="text-sm">Login</router-link>
        <router-link v-if="!isAuth" to="/register" class="text-sm">Register</router-link>
        <router-link v-if="isAuth" to="/profile" class="text-sm">My Profile</router-link>
        <router-link v-if="isAuth" to="/clubs" class="text-sm">My Golf Bag</router-link>
        <button v-if="isAuth" @click="doLogout" class="text-sm text-red-600">Logout</button>
      </nav>
    </div>
  </header>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getToken, logout } from '../services/auth'

export default defineComponent({
  setup() {
    const router = useRouter()
    const isAuth = computed(() => !!getToken())

    function doLogout() {
      logout()
      router.push('/')
    }

    return { isAuth, doLogout }
  }
})
</script>

<style scoped></style>
