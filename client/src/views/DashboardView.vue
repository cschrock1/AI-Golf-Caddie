<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="'Dashboard'" :hole-label="'Welcome back'" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Welcome back</p>
      <h1 class="mt-2 text-3xl font-black text-white">{{ userName }}</h1>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Rounds</p>
          <p class="mt-2 text-2xl font-black text-white">{{ rounds.length || 0 }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Avg score</p>
          <p class="mt-2 text-2xl font-black text-white">{{ averageScore || '—' }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Handicap</p>
          <p class="mt-2 text-2xl font-black text-white">{{ handicap || '—' }}</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Recent round</p>
          <h2 class="mt-2 text-2xl font-black text-white">Pebble Beach</h2>
        </div>
        <span class="rounded-full border border-[#274536] bg-[#10271f] px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[#c8ff00]">Score 74</span>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Course</p>
          <p class="mt-2 text-base font-bold text-white">Pebble Beach</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Date</p>
          <p class="mt-2 text-base font-bold text-white">Sep 4, 2026</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Result</p>
          <p class="mt-2 text-base font-bold text-white">+2</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Quick actions</p>
      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <button type="button" class="rounded-full bg-[#c8ff00] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#07140f]" @click="router.push('/hole')">
          Start round
        </button>
        <button type="button" class="rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#dfeee6]" @click="router.push('/bag')">
          View bag
        </button>
        <button type="button" class="rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#dfeee6]" @click="router.push('/scorecard')">
          Scorecard
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { authStore } from '../stores/auth'
import { getGolferProfile, getRounds } from '../services/api'

const router = useRouter()
const rounds = ref<Array<{ score?: number | null }>>([])

const userName = computed(() => authStore.user.value?.full_name || 'Golfer')
const averageScore = computed(() => {
  if (!rounds.value.length) return '—'
  const total = rounds.value.reduce((sum, round) => sum + (round.score ?? 0), 0)
  return Math.round(total / rounds.value.length)
})
const handicap = ref('—')

onMounted(async () => {
  const me = authStore.user.value
  if (!me) return

  try {
    const [roundsResponse, profileResponse] = await Promise.all([
      getRounds(me.id),
      getGolferProfile(me.id)
    ])
    rounds.value = roundsResponse.data
    handicap.value = profileResponse.data.handicap ?? '—'
  } catch {
    rounds.value = []
    handicap.value = '—'
  }
})
</script>
