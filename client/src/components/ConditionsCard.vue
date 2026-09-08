<template>
  <section class="rounded-[28px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
    <div class="mb-4 flex items-center justify-between">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Conditions</p>
      <span class="rounded-full border border-[#274536] bg-[#0d2119] px-2 py-1 text-[9px] uppercase tracking-[0.18em] text-[#8ca49a]">demo data</span>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Wind</p>
        <p class="mt-2 text-3xl font-black text-white">{{ windSpeed }} <span class="text-base font-semibold text-[#8ca49a]">MPH</span></p>
        <p class="mt-1 text-[10px] font-bold uppercase tracking-[0.16em] text-[#c8ff00]">Headwind</p>
      </div>

      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Temp</p>
        <p class="mt-2 text-3xl font-black text-white">{{ temperature }}°</p>
        <p class="mt-1 text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Fahrenheit</p>
      </div>

      <div class="rounded-2xl border border-[#1f4135] bg-[#0d2119] p-3 col-span-2">
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Wind notes</p>
        <p class="mt-2 text-sm font-medium text-[#dfeee6]">{{ windDirection }}</p>
        <p class="mt-1 text-xs text-[#8ca49a]">{{ note }}</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    windSpeed?: number
    windDirection?: string
    temperature?: number
    note?: string
  }>(),
  {
    windSpeed: 14,
    windDirection: 'South-Southeast',
    temperature: 61,
    note: 'Sample conditions for visual design and frontend validation.'
  }
)
</script>
