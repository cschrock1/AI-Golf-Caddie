<template>
  <div class="max-w-md mx-auto mt-12">
    <h1 class="text-2xl font-bold mb-4">Register</h1>
    <form @submit.prevent="onSubmit" class="space-y-4">
      <input v-model="full_name" placeholder="Full name" class="w-full p-2 border rounded" />
      <input v-model="email" placeholder="Email" type="email" class="w-full p-2 border rounded" />
      <input v-model="password" placeholder="Password" type="password" class="w-full p-2 border rounded" />
      <input v-model="confirm" placeholder="Confirm password" type="password" class="w-full p-2 border rounded" />
      <div class="flex justify-end">
        <button class="px-4 py-2 bg-blue-600 text-white rounded">Register</button>
      </div>
    </form>
    <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { register, login } from '../services/auth'
import { useRouter } from 'vue-router'

export default defineComponent({
  setup() {
    const full_name = ref('')
    const email = ref('')
    const password = ref('')
    const confirm = ref('')
    const error = ref('')
    const router = useRouter()

    async function onSubmit() {
      error.value = ''
      if (!email.value || !password.value || !confirm.value) {
        error.value = 'Email and password are required.'
        return
      }
      if (password.value !== confirm.value) {
        error.value = 'Passwords do not match.'
        return
      }
      try {
        await register({ full_name: full_name.value, email: email.value, password: password.value })
        // auto-login
        await login({ email: email.value, password: password.value })
        router.push('/profile')
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Registration failed'
      }
    }

    return { full_name, email, password, confirm, onSubmit, error }
  }
})
</script>
