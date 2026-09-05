<template>
  <section class="rounded-[30px] border border-[#c8ff00]/45 bg-[#0d2119] p-4 shadow-[0_20px_42px_rgba(2,10,7,0.32)] sm:p-5">
    <div class="flex items-start justify-between gap-3">
      <div>
        <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">✦ AI caddie recommendation</p>
        <p class="mt-3 text-4xl font-black tracking-tight text-white sm:text-5xl">{{ clubName }}</p>
        <p class="mt-1 text-xs font-bold uppercase tracking-[0.2em] text-[#b8d8c8]">Smooth {{ tempo }}%</p>
      </div>
      <div class="rounded-full border border-[#c8ff00]/35 bg-[#142d20] px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-[#c8ff00]">
        {{ confidence }}% confidence
      </div>
    </div>

    <div class="mt-5 grid grid-cols-2 gap-3 text-left">
      <div class="rounded-2xl border border-[#224236] bg-[#10271f] p-3">
        <p class="text-[10px] uppercase tracking-[0.18em] text-[#8ca49a]">Carry</p>
        <p class="mt-1 text-3xl font-black text-white">{{ carry }} <span class="text-xs text-[#8ca49a]">YDS</span></p>
      </div>
      <div class="rounded-2xl border border-[#224236] bg-[#10271f] p-3">
        <p class="text-[10px] uppercase tracking-[0.18em] text-[#8ca49a]">Target</p>
        <p class="mt-1 text-lg font-black leading-6 text-white">{{ target }}</p>
      </div>
    </div>

    <div class="mt-3 flex items-center justify-between rounded-2xl border border-[#214335] bg-[#0b1d17] p-3">
      <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Landing</p>
      <p class="text-sm font-bold uppercase tracking-[0.1em] text-[#ddf7be]">{{ landing }}</p>
    </div>

    <p class="mt-4 text-sm leading-6 text-[#e7efe9]">{{ rationale }}</p>

    <button type="button" class="mt-5 w-full rounded-full px-4 py-3 text-sm font-black uppercase tracking-[0.18em] transition hover:brightness-110 focus-visible:outline-none" :class="locked ? 'border border-[#c8ff00] bg-[#142d20] text-[#c8ff00]' : 'bg-[#c8ff00] text-[#07140f]'" :aria-pressed="locked" @click="emit('lock-in')">
      {{ locked ? 'Recommendation locked' : 'Lock in recommendation' }}
    </button>

    <div v-if="locked" class="mt-3 flex items-center gap-2 text-xs font-semibold text-[#c8ff00]" role="status">
      <span class="h-2 w-2 rounded-full bg-[#c8ff00]" aria-hidden="true"></span>
      Club and target saved for this hole.
    </div>

    <div class="mt-5 border-t border-[#1c3b31] pt-4">
      <p class="text-[10px] uppercase tracking-[0.22em] text-[#8ca49a]">Alternative</p>
      <div class="mt-2 flex items-center justify-between gap-3">
        <div>
          <p class="text-lg font-bold text-white">{{ alternativeClub }}</p>
          <p class="text-xs uppercase tracking-[0.18em] text-[#8ca49a]">{{ alternativeRisk }}</p>
        </div>
        <span class="rounded-full border border-[#245040] bg-[#10271f] px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[#dfeee6]">106 YDS</span>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
    clubName?: string
    confidence?: number
    carry?: number
    tempo?: number
    landing?: string
    target?: string
    rationale?: string
    alternativeClub?: string
    alternativeRisk?: string
    locked?: boolean
  }>(),
  {
    clubName: '9-Iron',
    confidence: 94,
    carry: 112,
    tempo: 85,
    landing: 'Soft hold',
    target: '4 yards left of pin',
    rationale: 'With the gusty 14 mph Pacific headwind, a smooth 9-iron should provide enough carry while keeping the ball below the wind.',
    alternativeClub: 'Pitching Wedge',
    alternativeRisk: 'Higher front bunker risk',
    locked: false
  })

const emit = defineEmits<{
  'lock-in': []
}>()
</script>
