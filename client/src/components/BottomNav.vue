<template>
  <nav class="fixed inset-x-0 bottom-0 z-40 border-t border-[#1a352d] bg-[#071b14]/95 backdrop-blur-md">
    <div class="mx-auto grid max-w-4xl grid-cols-4 gap-1 px-2 py-2 sm:gap-2">
      <button
        v-for="item in navItems"
        :key="item.to"
        type="button"
        class="flex flex-col items-center justify-center rounded-2xl px-2 py-2 text-[10px] font-medium uppercase tracking-[0.15em] transition"
        :class="isActive(item.to) ? 'bg-[#102d22] text-[#c8ff00]' : 'text-[#a7b8b0] hover:bg-[#0d2119] hover:text-white'"
        @click="go(item.to)"
      >
        <span class="mb-1 text-base" aria-hidden="true">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const navItems = [
  { label: 'GPS', to: '/hole', icon: '◎' },
  { label: 'Caddie', to: '/caddie', icon: '✦' },
  { label: 'Score', to: '/scorecard', icon: '▣' },
  { label: 'Bag', to: '/bag', icon: '◉' }
]

const isActive = (path: string) => route.path.startsWith(path)
const go = (path: string) => router.push(path)

const isBottomNavVisible = computed(() => !['/login', '/register'].includes(route.path))
</script>

<style scoped>
nav {
  box-shadow: 0 -8px 24px rgba(2, 8, 6, 0.28);
}
</style>
