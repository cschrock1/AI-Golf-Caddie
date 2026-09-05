<template>
  <div class="flex min-h-screen items-center justify-center bg-[#06110d] px-4 py-10">
    <div class="w-full max-w-md rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-6 shadow-[0_18px_32px_rgba(0,0,0,0.28)] sm:p-8">
      <div class="mb-8 text-center">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-[#2a4b3f] bg-[#102d22] text-lg font-black text-[#c8ff00]">A</div>
        <h1 class="mt-4 text-3xl font-black tracking-tight text-white">AI Golf Caddie</h1>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="email">Email</label>
          <input id="email" v-model="email" type="email" autocomplete="email" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="you@example.com" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="password">Password</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-sm text-[#f1b2b9]">{{ error }}</p>

        <button type="submit" class="w-full rounded-full bg-[#c8ff00] px-4 py-3 text-sm font-black uppercase tracking-[0.2em] text-[#07140f] transition hover:brightness-110 disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log in' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[#dfeee6]">
        Don’t have an account?
        <router-link to="/register" class="ml-1 font-semibold text-[#c8ff00]">Create account</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../services/auth'
import { authStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()

async function onSubmit() {
  error.value = ''
  loading.value = true

  try {
    await login({ email: email.value, password: password.value })
    await authStore.loadUser()
    router.push('/dashboard')
  } catch (e: unknown) {
    const requestError = e as { response?: { status?: number; data?: { detail?: string } } }
    if (requestError.response?.status === 401) {
      error.value = 'Invalid email or password.'
    } else {
      error.value = requestError.response?.data?.detail || 'Unable to reach the server. Confirm the iPhone and Mac are on the same Wi-Fi network.'
    }
  } finally {
    loading.value = false
  }
}
</script>
