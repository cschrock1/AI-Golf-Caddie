<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="courseName || 'Scorecard'" :hole-label="roundDate || 'Round'" />

    <router-link v-if="isHistoricalRound" to="/rounds" class="mt-4 inline-flex rounded-full border border-white/10 px-4 py-2 text-xs font-bold text-[#c8ff00] hover:border-[#c8ff00]/50">← Back to round history</router-link>

    <section class="mt-6 rounded-[30px] border border-white/10 bg-[#0d1d16] p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)]">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Scorecard</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-white">{{ courseName || 'Your scorecard' }}</h1>
        </div>
        <div class="text-sm text-[#dfeee6]"><span class="text-[#91a69a]">Player:</span> {{ playerName }}</div>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Round</p>
          <p class="mt-2 text-base font-bold text-white">{{ roundDate || 'No active round' }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Total strokes</p>
          <p class="mt-2 text-base font-bold text-white">{{ liveTotal ?? '—' }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Mapped par</p>
          <p class="mt-2 text-base font-bold text-white">{{ parTotal || '—' }}</p>
        </div>
      </div>
    </section>

    <p v-if="loading" class="mt-5 rounded-2xl border border-white/10 bg-[#10271f] p-4 text-sm text-[#a6b6ad]" role="status">Loading your round and scorecard…</p>
    <p v-else-if="loadError" class="mt-5 rounded-2xl border border-[#6b5632] bg-[#201c13] p-4 text-sm leading-6 text-[#f0d9a8]" role="status">{{ loadError }}</p>
    <div v-else-if="holes.length" class="mt-6">
      <ScorecardTable
        :course-name="courseName"
        :holes="holes"
        :round-id="roundId"
        :user-id="userId"
        @total-updated="updateLiveTotal"
      />
      <p class="mt-3 text-xs leading-5 text-[#91a69a]">Showing {{ holes.length }} scorecard {{ holes.length === 1 ? 'hole' : 'holes' }}. GPS mapping is currently available for Hole 1 only.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import ScorecardTable from '../components/ScorecardTable.vue'
import { getCourses, getCourseHoles, getRounds } from '../services/api'
import { roundStore } from '../stores/round'
import { authStore } from '../stores/auth'
import type { Course } from '../types'

const playerName = computed(() => authStore.user.value?.full_name || 'Golfer')
const route = useRoute()
const userId = computed(() => authStore.user.value?.id ?? null)
const courseName = ref(roundStore.selectedCourse.value?.name ?? '')
const isHistoricalRound = computed(() => route.query.round !== undefined)
const roundId = ref<number | null>(null)
const roundDate = ref('')
const liveTotal = ref<number | null>(null)
const loading = ref(true)
const loadError = ref('')
const holes = ref<Array<{ hole: number; par: number; score: number | null }>>([])
const parTotal = computed(() => holes.value.reduce((total, hole) => total + hole.par, 0))

function updateLiveTotal(total: number | null) {
  liveTotal.value = total
}

function formatRoundDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(`${date}T00:00:00`))
}

function toScorecardHoles(courseHoles: Awaited<ReturnType<typeof getCourseHoles>>['data']) {
  return courseHoles
    .sort((a, b) => a.hole_number - b.hole_number)
    .map((hole) => ({ hole_id: hole.id, hole: hole.hole_number, par: hole.par, score: null }))
}

onMounted(async () => {
  const user = authStore.user.value
  if (!user) {
    loadError.value = 'Sign in to open your scorecard.'
    loading.value = false
    return
  }

  try {
    const [roundsResponse, coursesResponse] = await Promise.all([getRounds(user.id), getCourses()])
    const requestedRoundId = Number(route.query.round)
    const requestedRound = isHistoricalRound.value
      ? roundsResponse.data.find((round) => round.id === requestedRoundId)
      : undefined
    if (isHistoricalRound.value && !requestedRound) throw new Error('That round could not be found in your account.')
    const selectedRoundId = roundStore.selectedRoundId.value
    const activeRound = requestedRound
      || roundsResponse.data.find((round) => round.id === selectedRoundId && !round.is_complete)
      || [...roundsResponse.data].filter((round) => !round.is_complete).sort((a, b) => b.id - a.id)[0]
    let activeCourse: Course | undefined

    if (activeRound) {
      activeCourse = coursesResponse.data.find((course) => course.id === activeRound.course_id)
      if (!activeCourse) throw new Error('The course for this round is no longer available.')
      courseName.value = activeCourse.name
      roundId.value = activeRound.id
      roundDate.value = formatRoundDate(activeRound.date)
      if (!isHistoricalRound.value) {
        roundStore.setRoundId(activeRound.id)
        roundStore.setCourse(activeCourse)
      }
      const holeResponse = await getCourseHoles(activeCourse.id)
      holes.value = toScorecardHoles(holeResponse.data)
    } else {
      roundStore.setRoundId(null)
      throw new Error('Start a round from Home to open its scorecard.')
    }

    if (!holes.value.length) loadError.value = 'This course has no scorecard hole data yet.'
  } catch (error: unknown) {
    loadError.value = (error as { message?: string }).message || 'Unable to load the scorecard. Try again after reconnecting to the server.'
  } finally {
    loading.value = false
  }
})
</script>
