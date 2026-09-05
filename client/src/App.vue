<template>
  <div class="min-h-screen bg-[#06110d] text-white antialiased">
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
