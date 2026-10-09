<template>
  <div class="mx-auto max-w-3xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="course?.name || 'Round recap'" hole-label="Round complete" />

    <main class="mt-6">
      <p v-if="loading" class="rounded-2xl border border-white/10 bg-[#10271f] p-4 text-sm text-[#a6b6ad]" role="status">Building your round recap…</p>
      <div v-else-if="error" class="rounded-2xl border border-[#70434a] bg-[#211719] p-5 text-sm text-[#f0b9ba]" role="alert">
        <p>{{ error }}</p>
        <button type="button" class="mt-4 rounded-full bg-[#c8ff00] px-4 py-2 text-xs font-black uppercase text-[#07140f]" @click="loadSummary">Try again</button>
      </div>
      <template v-else-if="round">
        <section class="rounded-[30px] border border-[#294b3c] bg-[radial-gradient(ellipse_at_top_right,_rgba(200,255,0,0.14),_transparent_50%),linear-gradient(135deg,#10271f,#0a1711)] p-5 sm:p-7">
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Round complete</p>
          <h1 class="mt-2 text-3xl font-black text-white">Nice round, {{ firstName }}</h1>
          <p class="mt-2 text-sm text-[#a6b6ad]">{{ course?.name || 'Golf course' }} · {{ formatDate(round.date) }}</p>
          <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-3">
            <div class="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-[#91a69a]">Total strokes</p>
              <p class="mt-2 text-3xl font-black text-white">{{ totalStrokes ?? '—' }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-[#91a69a]">To par</p>
              <p class="mt-2 text-3xl font-black text-[#c8ff00]">{{ toPar }}</p>
            </div>
            <div class="col-span-2 rounded-2xl border border-white/10 bg-black/20 p-4 sm:col-span-1">
              <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-[#91a69a]">Holes scored</p>
              <p class="mt-2 text-3xl font-black text-white">{{ scoredScores.length }}<span class="ml-1 text-sm font-semibold text-[#91a69a]">/ {{ holes.length }} mapped</span></p>
            </div>
          </div>
                </section>

        <section class="mt-4 rounded-[28px] border border-white/10 bg-[#0d1d16] p-5 sm:p-6">
          <div class="flex items-center justify-between gap-3">
            <div><p class="text-[10px] font-bold uppercase tracking-[0.2em] text-[#c8ff00]">Your play</p><h2 class="mt-1 text-xl font-black text-white">Shots by club</h2></div>
            <span class="rounded-full bg-white/5 px-3 py-1 text-xs font-bold text-white/70">{{ shots.length }} tracked</span>
          </div>
          <div v-if="clubUsage.length" class="mt-4 space-y-2">
            <div v-for="item in clubUsage" :key="item.clubId" class="flex items-center justify-between rounded-xl border border-white/5 bg-white/[0.03] px-4 py-3">
              <span class="font-semibold text-white">{{ item.name }}</span><span class="text-sm font-bold text-[#c8ff00]">{{ item.count }} {{ item.count === 1 ? 'shot' : 'shots' }}</span>
            </div>
          </div>
          <p v-else class="mt-4 rounded-xl border border-dashed border-white/10 p-4 text-sm text-[#a6b6ad]">No shots were tracked this round. Use Track shot on GPS next time to build club-by-club history.</p>
        </section>

        <div class="mt-5 grid gap-3 sm:grid-cols-2">
          <button type="button" class="rounded-full bg-[#c8ff00] px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-[#07140f]" @click="router.push({ path: '/scorecard', query: { round: String(round.id) } })">Review scorecard</button>
          <button type="button" class="rounded-full border border-white/10 bg-[#10271f] px-5 py-3 text-xs font-black uppercase tracking-[0.14em] text-white" @click="router.push('/rounds')">Round history</button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { getClubs, getCourses, getCourseHoles, getRoundScores, getRounds, getShots } from '../services/api'
import { authStore } from '../stores/auth'
import type { Club, Course, Hole, Round, RoundScore, Shot } from '../types'

type ClubUsage = { clubId: number; name: string; count: number }

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const round = ref<Round | null>(null)
const course = ref<Course | null>(null)
const holes = ref<Hole[]>([])
const scores = ref<RoundScore[]>([])
const shots = ref<Shot[]>([])
const clubs = ref<Club[]>([])
const firstName = computed(() => authStore.user.value?.full_name?.trim().split(/\s+/)[0] || 'Golfer')
const scoredScores = computed(() => {
  const mappedHoleIds = new Set(holes.value.map((hole) => hole.id))
  const latestScoreByHole = new Map<number, RoundScore>()
  for (const score of [...scores.value].sort((first, second) => first.id - second.id)) {
    if (mappedHoleIds.has(score.hole_id)) latestScoreByHole.set(score.hole_id, score)
  }
  return [...latestScoreByHole.values()]
})
const totalStrokes = computed(() => scoredScores.value.reduce((total, score) => total + score.strokes, 0) || round.value?.score || null)
const toPar = computed(() => {
  if (totalStrokes.value == null) return '—'
  const parTotal = scoredScores.value.reduce((total, score) => {
    const hole = holes.value.find((item) => item.id === score.hole_id)
    return total + (hole?.par ?? 0)
  }, 0)
  const difference = totalStrokes.value - parTotal
  return difference === 0 ? 'E' : difference > 0 ? `+${difference}` : String(difference)
})
const clubUsage = computed<ClubUsage[]>(() => {
  const counts = new Map<number, number>()
  for (const shot of shots.value) counts.set(shot.club_id, (counts.get(shot.club_id) ?? 0) + 1)
  return [...counts.entries()]
    .map(([clubId, count]) => ({ clubId, count, name: clubs.value.find((club) => club.id === clubId)?.name ?? 'Club' }))
    .sort((first, second) => second.count - first.count)
})

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(`${date}T00:00:00`))
}

async function loadSummary() {
  const user = authStore.user.value
  const roundId = Number(route.query.round)
  if (!user || !Number.isInteger(roundId) || roundId <= 0) {
    error.value = 'This round recap could not be opened.'
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [roundsResponse, coursesResponse, clubsResponse] = await Promise.all([
      getRounds(user.id), getCourses(), getClubs(user.id)
    ])
    const selectedRound = roundsResponse.data.find((item) => item.id === roundId)
    if (!selectedRound) throw new Error('Round not found in your history.')
    const selectedCourse = coursesResponse.data.find((item) => item.id === selectedRound.course_id)
    if (!selectedCourse) throw new Error('The course for this round is no longer available.')
    const [holeResponse, scoreResponse, shotResponse] = await Promise.all([
      getCourseHoles(selectedCourse.id), getRoundScores(roundId), getShots(roundId)
    ])
    round.value = selectedRound
    course.value = selectedCourse
    holes.value = holeResponse.data
    scores.value = scoreResponse.data
    shots.value = shotResponse.data
    clubs.value = clubsResponse.data
  } catch (requestError: any) {
    error.value = requestError?.message || requestError?.response?.data?.detail || 'Unable to load the round recap.'
  } finally {
    loading.value = false
  }
}

onMounted(loadSummary)
</script>
