<template>
  <header class="border-b border-white/10 bg-[#08130e]/90 backdrop-blur-xl" :class="compact ? 'gps-header-compact' : ''">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6" :class="compact ? 'py-2.5' : ''">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg border border-[#2a4b3f] bg-[#102d22] text-sm font-bold text-[#c8ff00]">A</div>
        <div>
          <p class="text-[10px] uppercase tracking-[0.28em] text-[#8ca49a]">Course companion</p>
          <div class="mt-1 flex items-center gap-2 text-sm font-semibold text-white sm:text-base">
            <span>AI Caddie</span>
            <span class="inline-block h-1.5 w-1.5 rounded-full bg-[#c8ff00]" aria-hidden="true"></span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="flex items-center gap-2 rounded-full border border-[#2a4b3f] bg-[#113027] px-3 py-2 text-sm text-[#dfeee6] transition hover:border-[#5c7f73] hover:text-white"
          aria-label="Open profile"
          @click="router.push('/profile')"
        >
          <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-[#c8ff00] text-xs font-bold text-[#07140f]">{{ profileInitials }}</span>
          <span class="hidden sm:inline">Profile</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../stores/auth'

const profileInitials = computed(() => {
  const name = authStore.user.value?.full_name?.trim()
  if (!name) return 'G'

  return name
    .split(/\s+/)
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
})
const router = useRouter()

withDefaults(
  defineProps<{
    courseName?: string
    holeLabel?: string
    compact?: boolean
  }>(),
  {
    courseName: '',
    holeLabel: ''
  }
)
</script>
