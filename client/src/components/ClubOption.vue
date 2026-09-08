<template>
  <button
    type="button"
    class="w-full rounded-[24px] border p-3 text-left transition hover:border-[#5a7f74] hover:bg-[#143a2e]"
    :class="selected ? 'border-[#c8ff00] bg-[#0d2119]' : 'border-[#1e3b32] bg-[#0d2119]/80'"
  >
    <div class="flex items-center justify-between gap-2">
      <div>
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">{{ label }}</p>
        <p class="mt-1 text-xl font-black text-white">{{ clubName }}</p>
      </div>
      <span class="rounded-full border border-[#274536] bg-[#10271f] px-2 py-1 text-[9px] uppercase tracking-[0.16em] text-[#c8ff00]">{{ matchText }}</span>
    </div>

    <div class="mt-3 space-y-1 text-sm text-[#dfeee6]">
      <p><span class="text-[#8ca49a]">Carry:</span> {{ carry }} YDS</p>
      <p><span class="text-[#8ca49a]">Tempo:</span> {{ tempo }}%</p>
      <p><span class="text-[#8ca49a]">Landing:</span> {{ landing }}</p>
    </div>
  </button>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label?: string
    clubName?: string
    carry?: number
    tempo?: number
    landing?: string
    selected?: boolean
    matchText?: string
  }>(),
  {
    label: 'Alternative',
    clubName: 'Pitching Wedge',
    carry: 106,
    tempo: 80,
    landing: 'Full swing',
    selected: false,
    matchText: 'Higher risk'
  }
)
</script>
