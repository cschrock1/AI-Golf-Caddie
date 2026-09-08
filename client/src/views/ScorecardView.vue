<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="courseName" :hole-label="'Round 2'" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Scorecard</p>
          <h1 class="mt-2 text-3xl font-black text-white">Pebble Beach</h1>
        </div>
        <div class="text-sm text-[#dfeee6]">
          <span class="text-[#8ca49a]">Player:</span> Jordan Palmer
        </div>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Round</p>
          <p class="mt-2 text-base font-bold text-white">Sep 4, 2026</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Total</p>
          <p class="mt-2 text-base font-bold text-white">74</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Par</p>
          <p class="mt-2 text-base font-bold text-white">72</p>
        </div>
      </div>
    </section>

    <div class="mt-6">
      <ScorecardTable :holes="holes" />
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '../components/AppHeader.vue'
import ScorecardTable from '../components/ScorecardTable.vue'

const courseName = 'Pebble Beach'

const holes = [
  { hole: 1, par: 4, score: 4 },
  { hole: 2, par: 5, score: 5 },
  { hole: 3, par: 3, score: 4 },
  { hole: 4, par: 4, score: 4 },
  { hole: 5, par: 4, score: 5 },
  { hole: 6, par: 3, score: 3 },
  { hole: 7, par: 3, score: 4 },
  { hole: 8, par: 5, score: 5 },
  { hole: 9, par: 4, score: 4 },
  { hole: 10, par: 4, score: 4 },
  { hole: 11, par: 5, score: 6 },
  { hole: 12, par: 4, score: 3 },
  { hole: 13, par: 3, score: 3 },
  { hole: 14, par: 4, score: 4 },
  { hole: 15, par: 5, score: 5 },
  { hole: 16, par: 4, score: 4 },
  { hole: 17, par: 3, score: 3 },
  { hole: 18, par: 4, score: 5 }
]
</script>
