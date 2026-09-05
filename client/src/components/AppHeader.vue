<template>
  <header class="border-b border-[#1d3a2d] bg-[#081d16]/90 backdrop-blur-sm">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
      <div class="flex items-center gap-3">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg border border-[#2a4b3f] bg-[#102d22] text-sm font-bold text-[#c8ff00]">A</div>
        <div>
          <p class="text-[10px] uppercase tracking-[0.28em] text-[#8ca49a]">AI caddie gps</p>
          <div class="mt-1 flex items-center gap-2 text-sm font-semibold text-white sm:text-base">
            <span>AI Caddie</span>
            <span class="inline-block h-1.5 w-1.5 rounded-full bg-[#c8ff00]" aria-hidden="true"></span>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span class="hidden items-center gap-1.5 rounded-full border border-[#2a4b3f] bg-[#0d2119] px-2.5 py-2 text-[9px] font-bold uppercase tracking-[0.14em] text-[#c8ff00] sm:flex">
          <span class="h-1.5 w-1.5 rounded-full bg-[#c8ff00]" aria-hidden="true"></span>
          GPS active
        </span>
        <button
          type="button"
          class="flex items-center gap-2 rounded-full border border-[#2a4b3f] bg-[#113027] px-3 py-2 text-sm text-[#dfeee6] transition hover:border-[#5c7f73] hover:text-white"
          aria-label="Open profile"
        >
          <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-[#c8ff00] text-xs font-bold text-[#07140f]">JP</span>
          <span class="hidden sm:inline">Profile</span>
        </button>
      </div>
    </div>

    <div v-if="courseName || holeLabel" class="mx-auto max-w-6xl border-t border-[#17382d] px-4 py-3 text-sm text-[#d4e0d8] sm:px-6">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-[10px] uppercase tracking-[0.26em] text-[#8ca49a]">Current round</p>
          <p class="mt-1 text-base font-semibold text-white">{{ courseName || 'Pebble Beach' }}</p>
        </div>
        <div class="text-right">
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Hole</p>
          <p class="mt-1 text-base font-semibold text-[#c8ff00]">{{ holeLabel || 'Hole 7' }}</p>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    courseName?: string
    holeLabel?: string
  }>(),
  {
    courseName: 'Pebble Beach',
    holeLabel: 'Hole 7'
  }
)
</script>
