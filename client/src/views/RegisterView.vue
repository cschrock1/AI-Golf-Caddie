<template>
  <div class="flex min-h-screen items-center justify-center bg-[#06110d] px-4 py-10">
    <div class="w-full max-w-md rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-6 shadow-[0_18px_32px_rgba(0,0,0,0.28)] sm:p-8">
      <div class="mb-8 text-center">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl border border-[#2a4b3f] bg-[#102d22] text-lg font-black text-[#c8ff00]">A</div>
        <h1 class="mt-4 text-3xl font-black tracking-tight text-white">AI Golf Caddie</h1>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="full-name">Full name</label>
          <input id="full-name" v-model="full_name" type="text" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="Jordan Palmer" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="register-email">Email</label>
          <input id="register-email" v-model="email" type="email" autocomplete="email" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="you@example.com" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="register-password">Password</label>
          <input id="register-password" v-model="password" type="password" autocomplete="new-password" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="••••••••" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="confirm-password">Confirm password</label>
          <input id="confirm-password" v-model="confirm" type="password" autocomplete="new-password" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-sm text-[#f1b2b9]">{{ error }}</p>

        <button type="submit" class="w-full rounded-full bg-[#c8ff00] px-4 py-3 text-sm font-black uppercase tracking-[0.2em] text-[#07140f] transition hover:brightness-110 disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[#dfeee6]">
        Already have an account?
        <router-link to="/login" class="ml-1 font-semibold text-[#c8ff00]">Log in</router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../services/auth'
import { authStore } from '../stores/auth'

const full_name = ref('')
const email = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()

async function onSubmit() {
  error.value = ''

  if (!email.value || !password.value || !confirm.value) {
    error.value = 'Email and password are required.'
    return
  }

  if (password.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }

  if (password.value !== confirm.value) {
    error.value = 'Passwords do not match.'
    return
  }

  loading.value = true

  try {
    await register({ full_name: full_name.value, email: email.value, password: password.value })
    await login({ email: email.value, password: password.value })
    await authStore.loadUser()
    router.push('/dashboard')
  } catch (requestError: unknown) {
    const detail = (requestError as { response?: { data?: { detail?: string } } }).response?.data?.detail
    error.value = detail || 'Unable to reach the server. Confirm the iPhone and Mac are on the same Wi-Fi network.'
  } finally {
    loading.value = false
  }
}
</script>
