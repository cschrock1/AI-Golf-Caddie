<template>
  <div class="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,_#edf5ea_0%,_#dfead6_35%,_#c9d7bf_100%)] px-4 py-10">
    <div class="w-full max-w-md rounded-[28px] border border-[#b5c8a9] bg-[#f9fbf7] p-6 shadow-[0_22px_50px_rgba(21,55,30,0.15)] sm:p-8">
      <div class="mb-8 text-center">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-[#bfd4b0] bg-[#1f5d3a] text-xl font-black text-[#eafac6] shadow-sm">⛳</div>
        <h1 class="mt-4 text-3xl font-black tracking-tight text-[#183c2a]">AI Golf Caddie</h1>
        <p class="mt-2 text-sm text-[#4b5f4f]">Your course-side decision helper</p>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="email">Email</label>
          <input id="email" v-model="email" type="email" autocomplete="email" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="you@example.com" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="password">Password</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-sm text-[#a53d3d]">{{ error }}</p>

        <button type="submit" class="w-full rounded-full bg-[#1f5d3a] px-4 py-3 text-sm font-black uppercase tracking-[0.2em] text-[#effae4] transition hover:bg-[#174c30] disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Log in' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[#485f49]">
        Don’t have an account?
        <router-link to="/register" class="ml-1 font-semibold text-[#1f5d3a] underline">Create account</router-link>
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
