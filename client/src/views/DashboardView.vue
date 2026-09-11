<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="'Dashboard'" :hole-label="'Home'" />

    <section class="mt-6 rounded-[28px] border border-[#bfd4b0] bg-[#f7faf4] p-5 shadow-[0_18px_35px_rgba(24,60,42,0.08)]">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#5d7159]">Welcome back</p>
      <h1 class="mt-2 text-3xl font-black text-[#183c2a]">{{ userName }}</h1>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Rounds</p>
          <p class="mt-2 text-2xl font-black text-[#183c2a]">{{ rounds.length || 0 }}</p>
        </div>
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Avg score</p>
          <p class="mt-2 text-2xl font-black text-[#183c2a]">{{ averageScore || '—' }}</p>
        </div>
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Handicap</p>
          <p class="mt-2 text-2xl font-black text-[#183c2a]">{{ handicap || '—' }}</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[28px] border border-[#bfd4b0] bg-[#f7faf4] p-5 shadow-[0_18px_35px_rgba(24,60,42,0.08)]">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#5d7159]">Recent round</p>
          <h2 class="mt-2 text-2xl font-black text-[#183c2a]">Pebble Beach</h2>
        </div>
        <span class="rounded-full border border-[#cddcc0] bg-[#edf5ea] px-2 py-1 text-[10px] uppercase tracking-[0.18em] text-[#1e5d3f]">Score 74</span>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Course</p>
          <p class="mt-2 text-base font-bold text-[#183c2a]">Pebble Beach</p>
        </div>
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Date</p>
          <p class="mt-2 text-base font-bold text-[#183c2a]">Sep 4, 2026</p>
        </div>
        <div class="rounded-2xl border border-[#d9e6d0] bg-[#edf5ea] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#5d7159]">Result</p>
          <p class="mt-2 text-base font-bold text-[#183c2a]">+2</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[28px] border border-[#bfd4b0] bg-[#f7faf4] p-5 shadow-[0_18px_35px_rgba(24,60,42,0.08)]">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#5d7159]">Quick actions</p>
      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <button type="button" class="rounded-full bg-[#1f5d3a] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#effae4]" @click="router.push('/hole')">
          Start round
        </button>
        <button type="button" class="rounded-full border border-[#c5d5bd] bg-[#edf5ea] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#183c2a]" @click="router.push('/bag')">
          View bag
        </button>
        <button type="button" class="rounded-full border border-[#c5d5bd] bg-[#edf5ea] px-4 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#183c2a]" @click="router.push('/scorecard')">
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
