<template>
  <div class="max-w-md mx-auto mt-12">
    <h1 class="text-2xl font-bold mb-4">Login</h1>
    <form @submit.prevent="onSubmit" class="space-y-4">
      <input v-model="email" placeholder="Email" type="email" class="w-full p-2 border rounded" />
      <input v-model="password" placeholder="Password" type="password" class="w-full p-2 border rounded" />
      <div class="flex justify-end">
        <button class="px-4 py-2 bg-blue-600 text-white rounded">Login</button>
      </div>
    </form>
    <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { login } from '../services/auth'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {
    const email = ref('')
    const password = ref('')
    const error = ref('')
    const router = useRouter()

    async function onSubmit() {
      error.value = ''
      try {
        await login({ email: email.value, password: password.value })
        router.push('/profile')
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Login failed'
      }
    }

    return { email, password, onSubmit, error }
  }
})
</script>
