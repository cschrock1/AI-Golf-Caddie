<template>
  <div class="flex min-h-screen items-center justify-center bg-[linear-gradient(180deg,_#edf5ea_0%,_#dfead6_35%,_#c9d7bf_100%)] px-4 py-8">
    <div class="w-full max-w-md rounded-[28px] border border-[#b5c8a9] bg-[#f9fbf7] p-6 shadow-[0_22px_50px_rgba(21,55,30,0.15)] sm:p-8">
      <div class="mb-8 text-center">
        <div class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-[#bfd4b0] bg-[#1f5d3a] text-xl font-black text-[#eafac6] shadow-sm">⛳</div>
        <h1 class="mt-4 text-3xl font-black tracking-tight text-[#183c2a]">Create account</h1>
        <p class="mt-2 text-sm text-[#4b5f4f]">Start tracking your golf game</p>
      </div>

      <form class="space-y-4" @submit.prevent="onSubmit">
        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="full-name">Full name</label>
          <input id="full-name" v-model="full_name" type="text" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="Jordan Palmer" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="register-email">Email</label>
          <input id="register-email" v-model="email" type="email" autocomplete="email" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="you@example.com" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="register-password">Password</label>
          <input id="register-password" v-model="password" type="password" autocomplete="new-password" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="••••••••" />
        </div>

        <div>
          <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#4f654d]" for="confirm-password">Confirm password</label>
          <input id="confirm-password" v-model="confirm" type="password" autocomplete="new-password" class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none" placeholder="••••••••" />
        </div>

        <p v-if="error" class="text-sm text-[#a53d3d]">{{ error }}</p>

        <button type="submit" class="w-full rounded-full bg-[#1f5d3a] px-4 py-3 text-sm font-black uppercase tracking-[0.2em] text-[#effae4] transition hover:bg-[#174c30] disabled:opacity-60" :disabled="loading">
          {{ loading ? 'Creating account...' : 'Create account' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[#485f49]">
        Already have an account?
        <router-link to="/login" class="ml-1 font-semibold text-[#1f5d3a] underline">Sign in</router-link>
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
