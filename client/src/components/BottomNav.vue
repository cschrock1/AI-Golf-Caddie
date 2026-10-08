<template>
  <nav class="fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-[#07150f]/95 pb-[env(safe-area-inset-bottom)] shadow-[0_-12px_40px_rgba(0,0,0,0.35)] backdrop-blur-xl">
    <div class="mx-auto grid max-w-2xl gap-1 px-1.5 py-2 sm:gap-2 sm:px-2" :class="hasActiveRound ? 'grid-cols-5' : 'grid-cols-3'">
      <button
        v-for="item in navItems"
        :key="item.to"
        type="button"
        class="flex min-h-14 flex-col items-center justify-center rounded-2xl px-1 py-2 text-[8px] font-semibold uppercase tracking-[0.08em] transition min-[390px]:text-[9px] sm:px-2 sm:text-[10px] sm:tracking-[0.12em]"
        :class="isActive(item.to) ? 'bg-[#c8ff00] text-[#07140f] shadow-[0_4px_18px_rgba(200,255,0,0.16)]' : 'text-[#9aada2] hover:bg-white/5 hover:text-white'"
        @click="go(item.to)"
      >
        <span class="mb-1 text-base" aria-hidden="true">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { roundStore } from '../stores/round'

const route = useRoute()
const router = useRouter()

const hasActiveRound = computed(() => roundStore.hasActiveRound.value)
const navItems = computed(() => [
  { label: 'Home', to: '/dashboard', icon: '⌂' },
  ...(hasActiveRound.value ? [{ label: 'GPS', to: '/hole', icon: '◎' }] : []),
  { label: 'Caddie', to: '/caddie', icon: '✦' },
  ...(hasActiveRound.value ? [{ label: 'Scorecard', to: '/scorecard', icon: '▤' }] : []),
  { label: 'Profile', to: '/profile', icon: '●' }
])

const isActive = (path: string) => route.path.startsWith(path) || (path === '/profile' && route.path === '/rounds')
const go = (path: string) => router.push(path)

</script>

<style scoped>
nav {
  box-shadow: 0 -8px 24px rgba(2, 8, 6, 0.28);
}
</style>
