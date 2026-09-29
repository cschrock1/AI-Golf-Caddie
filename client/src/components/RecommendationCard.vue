<template>
  <section class="rounded-[28px] border border-white/10 bg-[#0d1d16] p-4 shadow-[0_20px_42px_rgba(2,10,7,0.28)] sm:p-5">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-[10px] font-bold uppercase tracking-[0.2em] text-[#c8ff00]">Distance based · deterministic</p>
        <h2 class="mt-2 text-xl font-black text-white">Shot suggestion</h2>
      </div>
      <span v-if="recommendation" class="rounded-full border border-white/10 px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.12em]" :class="recommendation.risk === 'Low' ? 'text-[#c8ff00]' : 'text-[#f2c57c]'">
        {{ recommendation.risk }} risk
      </span>
    </div>

    <p v-if="loading" class="mt-4 rounded-2xl border border-white/10 bg-[#10271f] p-4 text-sm text-[#a6b6ad]" role="status">Calculating from your position and saved club distances…</p>
    <p v-else-if="error" class="mt-4 rounded-2xl border border-[#70434a] bg-[#211719] p-4 text-sm leading-6 text-[#f0b9ba]" role="status">{{ error }}</p>
    <p v-else-if="!recommendation" class="mt-4 rounded-2xl border border-dashed border-white/15 bg-[#10271f] p-4 text-sm leading-6 text-[#a6b6ad]">Locate yourself on the mapped hole and add carry distances to your bag to get a shot suggestion.</p>

    <template v-else>
      <div class="mt-4 rounded-2xl border border-[#c8ff00]/20 bg-[#c8ff00]/5 p-4">
        <p class="text-[10px] uppercase tracking-[0.18em] text-[#91a69a]">Suggested club</p>
        <div class="mt-1 flex items-end justify-between gap-2">
          <p class="text-3xl font-black tracking-tight text-white">{{ recommendation.club_name }}</p>
          <p class="pb-1 text-sm font-bold text-[#c8ff00]">{{ recommendation.carry_yards }} yd carry</p>
        </div>
      </div>
      <div class="mt-3 grid grid-cols-2 gap-3">
        <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Target</p>
          <p class="mt-1 font-bold text-white">{{ recommendation.target_name }}</p>
          <p class="mt-1 text-xs text-[#a6b6ad]">{{ recommendation.target_yards }} yd</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Alternative</p>
          <p class="mt-1 font-bold text-white">{{ recommendation.alternative_club || '—' }}</p>
          <p class="mt-1 text-xs text-[#a6b6ad]">{{ recommendation.alternative_carry_yards ? `${recommendation.alternative_carry_yards} yd carry` : 'No second club with a distance' }}</p>
        </div>
      </div>
      <p class="mt-4 text-sm leading-6 text-[#d7e2db]">{{ recommendation.rationale }}</p>
      <button type="button" class="mt-4 w-full rounded-full bg-[#c8ff00] px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-[#07140f] transition hover:brightness-110" @click="emit('select-club', recommendation.club_id)">
        Use {{ recommendation.club_name }}
      </button>
    </template>
  </section>
</template>

<script setup lang="ts">
import type { Recommendation } from '../types'

defineProps<{
  recommendation: Recommendation | null
  loading: boolean
  error: string
}>()

const emit = defineEmits<{ 'select-club': [clubId: number] }>()
</script>
