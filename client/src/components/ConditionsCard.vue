<template>
  <section class="rounded-[28px] border border-white/10 bg-[#10271f] p-4 sm:p-5">
    <div class="mb-4 flex items-center justify-between">
      <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-white">Live conditions</p>
      <span v-if="weather?.source" class="rounded-full border border-[#274536] bg-[#0d2119] px-2 py-1 text-[9px] uppercase tracking-[0.14em] text-[#a6b6ad]">{{ weather.source }}</span>
    </div>

    <p v-if="loading" class="rounded-2xl border border-white/10 bg-[#0d2119] p-4 text-sm text-[#a6b6ad]" role="status">Loading current conditions…</p>
    <p v-else-if="error" class="rounded-2xl border border-[#70434a] bg-[#211719] p-4 text-sm leading-6 text-[#f0b9ba]" role="status">{{ error }}</p>
    <div v-else-if="weather?.temperature != null || weather?.windSpeed != null" class="grid grid-cols-2 gap-3">
      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#91a69a]">Wind</p>
        <p class="mt-2 text-3xl font-black text-white">{{ weather.windSpeed ?? '—' }} <span class="text-base font-semibold text-[#91a69a]">MPH</span></p>
        <p class="mt-1 text-[10px] uppercase tracking-[0.16em] text-[#c8ff00]">{{ windDirection }}</p>
      </div>

      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#91a69a]">Temperature</p>
        <p class="mt-2 text-3xl font-black text-white">{{ weather.temperature ?? '—' }}°</p>
        <p class="mt-1 text-[10px] uppercase tracking-[0.2em] text-[#91a69a]">Fahrenheit</p>
      </div>

      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3 col-span-2">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#91a69a]">Updated</p>
        <p class="mt-2 text-sm font-medium text-[#dfeee6]">{{ observedAt || 'Current local forecast' }}<span v-if="weather?.timezone" class="text-xs text-[#91a69a]"> · {{ weather.timezone }}</span></p>
      </div>
    </div>
    <p v-else class="rounded-2xl border border-white/10 bg-[#0d2119] p-4 text-sm text-[#a6b6ad]">Current conditions are unavailable for this hole.</p>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Conditions } from '../types'

const props = defineProps<{ weather: Conditions | null; loading: boolean; error: string }>()

const windDirection = computed(() => {
  const degrees = props.weather?.windDirectionDegrees
  if (degrees == null) return 'Direction unavailable'
  return ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.round(degrees / 45) % 8]
})
const observedAt = computed(() => {
  const value = props.weather?.observedAt
  if (!value) return null
  return value.replace('T', ' ')
})
</script>
