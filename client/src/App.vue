<template>
  <div class="min-h-screen bg-[radial-gradient(circle_at_top,_#f3f7ee_0%,_#dfead6_30%,_#c7d7be_100%)] text-slate-900 antialiased">
    <router-view />
    <BottomNav v-if="showBottomNav" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BottomNav from './components/BottomNav.vue'

const route = useRoute()
const showBottomNav = computed(() => !['/login', '/register'].includes(route.path))
</script>
