<template>
  <main v-if="isLoading" class="fixed inset-0 z-50 grid place-items-center bg-[#07100c] px-6" aria-live="polite" aria-label="Loading golf data">
    <div class="w-full max-w-sm space-y-3">
      <div class="h-16 animate-pulse rounded-2xl bg-white/10"></div>
      <div class="h-72 animate-pulse rounded-3xl bg-white/5"></div>
    </div>
  </main>

  <main v-else-if="error" class="fixed inset-0 z-50 grid place-items-center bg-[#07100c] p-6" role="alert">
    <section class="max-w-md rounded-3xl border border-white/10 bg-[#111a15] p-6 text-white">
      <p class="text-xs font-bold uppercase tracking-[0.2em] text-[#c8ff00]">Golf data unavailable</p>
      <p class="mt-3 text-sm leading-6 text-white/75">{{ error }}</p>
      <div class="mt-5 flex gap-2">
        <button type="button" class="rounded-xl bg-[#c8ff00] px-4 py-3 text-sm font-bold text-[#07140f]" @click="loadHoleData">Retry</button>
        <button type="button" class="rounded-xl border border-white/15 px-4 py-3 text-sm font-semibold" @click="router.push('/dashboard')">Back</button>
      </div>
    </section>
  </main>

  <main v-else-if="!hole" class="fixed inset-0 z-50 grid place-items-center bg-[#07100c] p-5 text-white">
    <section class="max-w-md rounded-3xl border border-[#6b5632] bg-[#201c13] p-6 text-center">
      <p class="text-xs font-bold uppercase tracking-[0.2em] text-[#f0d9a8]">Hole data unavailable</p>
      <h1 class="mt-3 text-2xl font-black">{{ courseName }}</h1>
      <p class="mt-2 text-sm leading-6 text-white/70">Scorecard data is unavailable for this hole. GPS mapping is currently available for Hole 1 only.</p>
      <button type="button" class="mt-5 rounded-xl border border-white/15 px-5 py-3 text-sm font-semibold" @click="router.push('/dashboard')">Back</button>
    </section>
  </main>

  <main v-else class="fixed inset-0 z-30 overflow-hidden bg-[#101914] text-white">
    <CourseMap v-if="hasGpsData" :hole="hole" :course="course" :full-screen="true" @distance-change="updateMapDistance" />
    <div v-else class="absolute inset-0 grid place-items-center bg-[#101914] px-6 pb-24 text-center">
      <div class="max-w-sm rounded-3xl border border-white/10 bg-[#0b1511]/90 p-6 shadow-2xl">
        <p class="text-xs font-bold uppercase tracking-[0.2em] text-[#c8ff00]">GPS unavailable</p>
        <h2 class="mt-2 text-2xl font-black">No GPS data available</h2>
        <p class="mt-2 text-sm leading-6 text-white/65">GPS mapping is currently available for Hole 1. You can still record a score for this hole.</p>
      </div>
    </div>

    <header class="pointer-events-none absolute inset-x-3 top-3 z-20 flex items-start gap-2 sm:inset-x-5 sm:top-5">
      <button type="button" class="pointer-events-auto grid h-12 w-12 shrink-0 place-items-center rounded-full bg-[#111512]/95 text-3xl shadow-xl backdrop-blur" aria-label="Back to dashboard" @click="router.push('/dashboard')">‹</button>

      <section class="pointer-events-auto min-w-0 flex-1 overflow-hidden rounded-[22px] bg-[#151a18]/95 shadow-xl backdrop-blur-md">
        <p class="truncate px-4 pt-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-white/55">{{ courseName }}</p>
        <div class="flex items-center">
          <div class="flex min-w-[112px] items-center gap-3 rounded-[20px] bg-[#111312] px-4 py-2.5">
            <span class="text-4xl font-black leading-none">{{ holeNumber }}</span>
            <div class="min-w-0">
              <p class="truncate text-xs font-semibold text-white/65">Hole length</p>
              <p class="whitespace-nowrap text-lg font-bold leading-tight">{{ pinDistance || '—' }}<span class="ml-1 text-xs font-semibold">yds</span></p>
            </div>
          </div>
          <div class="flex flex-1 items-center justify-around px-1 py-2 text-center">
            <div>
              <p class="text-[10px] text-white/55">Par</p>
              <p class="text-2xl font-bold">{{ par || '—' }}</p>
            </div>
            <div class="hidden min-[420px]:block">
              <p class="text-[10px] text-white/55">Score</p>
              <p class="text-2xl font-bold">{{ holeScore ?? '—' }}</p>
            </div>
          </div>
        </div>
      </section>
    </header>

    <footer class="pointer-events-none absolute inset-x-2 bottom-[calc(env(safe-area-inset-bottom)+5.25rem)] z-20 sm:inset-x-auto sm:left-1/2 sm:w-[min(620px,calc(100%-2rem))] sm:-translate-x-1/2">
      <section class="pointer-events-auto max-h-[72svh] overflow-hidden rounded-[28px] border border-white/10 bg-[#0b1511]/95 shadow-2xl backdrop-blur-xl">
        <button type="button" class="w-full px-4 pb-4 pt-3 text-left" :aria-expanded="sheetExpanded" @click="sheetExpanded = !sheetExpanded">
          <span class="mx-auto mb-3 block h-1 w-10 rounded-full bg-white/30" aria-hidden="true"></span>
          <span class="flex items-center justify-between gap-3">
            <span class="min-w-0">
              <span class="block text-[10px] font-bold uppercase tracking-[0.18em] text-[#a6b6ad]">Hole {{ holeNumber }} · Par {{ par || '—' }}</span>
              <span class="mt-1 block truncate text-base font-bold text-white">{{ courseName }}</span>
              <span class="mt-1 block text-xs text-white/55">{{ liveDistance != null ? 'Distance from tee marker to green center' : 'Drag the tee marker to set your position' }}</span>
            </span>
            <span class="shrink-0 rounded-2xl bg-[#c8ff00] px-4 py-2 text-right text-[#07140f]">
              <span class="block text-[9px] font-black uppercase tracking-[0.12em]">{{ liveDistance != null ? 'To green' : 'Hole length' }}</span>
              <span class="mt-0.5 block text-3xl font-black leading-none">{{ liveDistance ?? pinDistance ?? '—' }}<span class="ml-1 text-xs">yd</span></span>
            </span>
          </span>
          <span class="mt-3 flex items-center justify-between border-t border-white/10 pt-3 text-xs text-white/65">
            <span>{{ locationSummary }}</span>
            <span class="text-[#c8ff00]">{{ sheetExpanded ? 'Hide details ↑' : 'Round details ↓' }}</span>
          </span>
        </button>

        <div v-if="sheetExpanded" class="max-h-[42svh] space-y-4 overflow-y-auto border-t border-white/10 px-4 pb-4 pt-4">
          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-white/10 bg-white/5 p-3">
              <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-white/50">Wind</p>
              <p class="mt-1 text-lg font-black text-white">{{ currentWeather?.windSpeed ?? '—' }} <span class="text-xs font-semibold">mph</span></p>
              <p class="text-xs text-white/55">{{ weatherLoading ? 'Updating…' : windDirectionLabel }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/5 p-3">
              <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-white/50">Score</p>
              <p class="mt-1 text-lg font-black text-white">{{ holeScore ?? '—' }} <span class="text-xs font-semibold text-white/55">{{ holeScore != null ? 'strokes' : 'not entered' }}</span></p>
              <p class="text-xs text-white/55">{{ weatherError && !weatherLoading ? 'Weather unavailable' : 'Center of green target' }}</p>
            </div>
          </div>
          <div v-if="recommendationLoading || recommendation || recommendationError" class="rounded-2xl border border-[#c8ff00]/20 bg-[#c8ff00]/5 p-3">
            <p class="text-[9px] font-bold uppercase tracking-[0.16em] text-[#c8ff00]">Caddie</p>
            <p v-if="recommendationLoading" class="mt-1 text-sm text-white/65">Finding a club suggestion…</p>
            <p v-else-if="recommendation" class="mt-1 text-sm font-bold text-white">{{ recommendation.club_name }} · {{ recommendation.carry_yards }} yd</p>
            <p v-else class="mt-1 text-sm text-white/65">{{ recommendationError }}</p>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <button type="button" class="rounded-xl bg-[#c8ff00] px-3 py-3 text-sm font-black text-[#07140f]" @click="showShotDialog = true">Track shot<span class="mt-0.5 block text-[10px] font-semibold">{{ holeShots.length ? `${holeShots.length} logged` : 'Log a shot' }}</span></button>
            <button type="button" class="rounded-xl bg-[#2588ef] px-3 py-3 text-sm font-black text-white" @click="openScoreDialog">{{ holeScore != null ? 'Update score' : 'Enter score' }}<span class="mt-0.5 block text-[10px] font-semibold">{{ holeScore != null ? `${holeScore} strokes` : `Par ${par}` }}</span></button>
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-sm font-bold text-white" @click="router.push('/caddie')">Ask caddie<span class="mt-0.5 block text-[10px] font-medium text-white/55">Club recommendation</span></button>
            <button type="button" class="rounded-xl border border-white/10 bg-white/5 px-3 py-3 text-sm font-bold text-white" @click="router.push('/scorecard')">Open scorecard<span class="mt-0.5 block text-[10px] font-medium text-white/55">Round totals</span></button>
          </div>
          <button type="button" class="w-full rounded-xl border border-white/10 px-3 py-2.5 text-xs font-semibold text-white/65" @click="showTools = true">More round tools</button>
        </div>
      </section>
    </footer>

    <div v-if="showShotDialog" class="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-3 sm:items-center" @click.self="showShotDialog = false">
      <section class="w-full max-w-md rounded-[28px] border border-white/10 bg-[#111a15] p-5 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="shot-dialog-title">
        <div class="flex items-start justify-between gap-4">
          <div><p class="text-[10px] font-bold uppercase tracking-[0.2em] text-[#9cad9f]">Hole {{ holeNumber }} · Shot {{ holeShots.length + 1 }}</p><h2 id="shot-dialog-title" class="mt-1 text-2xl font-black">Track shot</h2></div>
          <button type="button" class="rounded-full border border-white/15 px-3 py-2 text-sm" @click="showShotDialog = false">Close</button>
        </div>
        <form class="mt-5 space-y-3" @submit.prevent="recordShot">
          <label class="block text-xs font-semibold text-white/65">Club
            <select v-model.number="shotClubId" required class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07100c] px-3 py-3 text-sm text-white">
              <option :value="null" disabled>Select club</option>
              <option v-for="club in bagOptions" :key="club.id" :value="club.id">{{ club.name }}{{ club.carry_distance ? ` · ${club.carry_distance} yd` : '' }}</option>
            </select>
          </label>
          <label class="block text-xs font-semibold text-white/65">Distance remaining (yards)
            <input v-model.number="endDistance" type="number" min="0" placeholder="Optional" class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07100c] px-3 py-3 text-sm text-white placeholder:text-white/35" />
          </label>
          <label class="block text-xs font-semibold text-white/65">Lie / result
            <select v-model="shotResult" class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07100c] px-3 py-3 text-sm text-white">
              <option value="">Choose result</option><option value="fairway">Fairway</option><option value="green">Green</option><option value="bunker">Bunker</option><option value="water">Water</option><option value="rough">Rough</option><option value="other">Other</option>
            </select>
          </label>
          <p v-if="shotError" class="text-sm text-[#ffaaa9]" role="alert">{{ shotError }}</p>
          <p v-if="!bagOptions.length" class="text-sm text-[#f0d9a8]">Add clubs to your bag before logging a shot.</p>
          <button type="submit" :disabled="!canRecordShot || savingShot" class="w-full rounded-xl bg-[#c8ff00] px-4 py-3.5 text-sm font-black uppercase tracking-wide text-[#07140f] disabled:opacity-40">{{ savingShot ? 'Saving…' : 'Save shot' }}</button>
        </form>
        <div v-if="holeShots.length" class="mt-4 max-h-32 divide-y divide-white/10 overflow-y-auto rounded-xl border border-white/10 px-3">
          <div v-for="(shot, index) in holeShots" :key="shot.id" class="flex justify-between gap-3 py-2 text-xs"><span>Shot {{ index + 1 }} · {{ clubName(shot.club_id) }}</span><span class="text-white/55">{{ shot.result || 'Result not set' }}<span v-if="shot.end_distance != null"> · {{ shot.end_distance }} yd</span></span></div>
        </div>
      </section>
    </div>

    <div v-if="showScoreDialog" class="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-3 sm:items-center" @click.self="showScoreDialog = false">
      <section class="w-full max-w-sm rounded-[28px] border border-white/10 bg-[#111a15] p-5 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="score-dialog-title">
        <div class="flex items-start justify-between"><div><p class="text-[10px] font-bold uppercase tracking-[0.2em] text-white/55">{{ courseName }}</p><h2 id="score-dialog-title" class="mt-1 text-2xl font-black">Hole {{ holeNumber }} score</h2></div><button type="button" class="rounded-full border border-white/15 px-3 py-2 text-sm" @click="showScoreDialog = false">Close</button></div>
        <p class="mt-1 text-sm text-white/55">Par {{ par }}</p>
        <div class="mt-5 flex items-center justify-center gap-8">
          <button type="button" class="grid h-12 w-12 place-items-center rounded-full bg-white/10 text-3xl" aria-label="Subtract one stroke" @click="scoreEntry = Math.max(1, scoreEntry - 1)">−</button>
          <div class="min-w-20 text-center"><p class="text-5xl font-black">{{ scoreEntry }}</p><p class="mt-1 text-[10px] uppercase tracking-widest text-white/50">Strokes</p></div>
          <button type="button" class="grid h-12 w-12 place-items-center rounded-full bg-white/10 text-3xl" aria-label="Add one stroke" @click="scoreEntry = Math.min(20, scoreEntry + 1)">+</button>
        </div>
        <p v-if="scoreError" class="mt-3 text-center text-sm text-[#ffaaa9]" role="alert">{{ scoreError }}</p>
        <button type="button" :disabled="savingScore" class="mt-5 w-full rounded-xl bg-[#2588ef] px-4 py-3.5 text-sm font-black uppercase tracking-wide disabled:opacity-40" @click="saveScore">{{ savingScore ? 'Saving…' : 'Save score' }}</button>
      </section>
    </div>

    <div v-if="showTools" class="fixed inset-0 z-50 flex items-end justify-center bg-black/70 p-3 sm:items-center" @click.self="showTools = false">
      <section class="w-full max-w-sm rounded-[28px] border border-white/10 bg-[#111a15] p-5 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="tools-title">
        <div class="flex items-center justify-between"><h2 id="tools-title" class="text-xl font-black">Round tools</h2><button type="button" class="rounded-full border border-white/15 px-3 py-2 text-sm" @click="showTools = false">Close</button></div>
        <div class="mt-4 grid grid-cols-2 gap-2">
          <button type="button" class="rounded-xl border border-white/10 bg-white/5 p-4 text-left font-semibold" @click="showTools = false; showBag = true">Choose club<span class="mt-1 block text-xs font-normal text-white/50">{{ shotClubId ? clubName(shotClubId) : 'Open your bag' }}</span></button>
          <button type="button" class="rounded-xl border border-white/10 bg-white/5 p-4 text-left font-semibold" @click="showTools = false; router.push('/caddie')">Ask caddie<span class="mt-1 block text-xs font-normal text-white/50">Shot recommendation</span></button>
          <button type="button" class="rounded-xl border border-white/10 bg-white/5 p-4 text-left font-semibold" @click="showTools = false; router.push('/profile')">Profile & bag<span class="mt-1 block text-xs font-normal text-white/50">Edit golfer data</span></button>
          <button type="button" class="rounded-xl border border-white/10 bg-white/5 p-4 text-left font-semibold" @click="showTools = false; router.push('/scorecard')">Scorecard<span class="mt-1 block text-xs font-normal text-white/50">Round totals</span></button>
        </div>
        <button type="button" :disabled="!roundId || endingRound" class="mt-3 w-full rounded-xl border border-[#ffaaa9]/35 bg-[#3a1d20]/60 px-4 py-3 text-sm font-bold text-[#ffcfce] disabled:opacity-40" @click="endRound">{{ endingRound ? 'Ending round…' : 'End round and save to history' }}</button>
        <p v-if="endRoundError" class="mt-2 text-sm text-[#ffaaa9]" role="alert">{{ endRoundError }}</p>
      </section>
    </div>

    <div v-if="showBag" class="fixed inset-0 z-[60] flex items-end justify-center bg-black/70 p-3 sm:items-center" @click.self="showBag = false">
      <section class="w-full max-w-md rounded-[28px] border border-white/10 bg-[#111a15] p-5 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="bag-title">
        <div class="flex items-center justify-between gap-4"><div><p class="text-[10px] uppercase tracking-[0.2em] text-white/55">Club selection</p><h2 id="bag-title" class="mt-1 text-xl font-black">Choose from your bag</h2></div><button type="button" class="rounded-full border border-white/15 px-3 py-2 text-sm" @click="showBag = false">Close</button></div>
        <div class="mt-4 max-h-[55svh] space-y-2 overflow-y-auto">
          <button v-for="club in bagOptions" :key="club.name" type="button" class="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/5 p-3 text-left" @click="selectBagClub(club)"><span class="font-bold">{{ club.name }}</span><span class="text-xs text-white/55">{{ club.carry_distance ?? club.total_distance ?? '—' }} yd</span></button>
        </div>
        <p v-if="bagMessage" class="mt-3 text-xs text-[#c8ff00]" role="status">{{ bagMessage }}</p>
      </section>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CourseMap from '../components/CourseMap.vue'
import { roundStore } from '../stores/round'
import { authStore } from '../stores/auth'
import { completeRound, createRound, createShot, getClubs, getCourses, getCourseHoles, getCurrentWeather, getHole, getRecommendation, getRoundScores, getRounds, getShots, saveRoundScores } from '../services/api'
import type { Club, Course, Conditions, Hole, Recommendation, RoundScore, Shot } from '../types'

const router = useRouter()
const route = useRoute()
const showBag = ref(false)
const showTools = ref(false)
const sheetExpanded = ref(false)
const showShotDialog = ref(false)
const showScoreDialog = ref(false)
const bagMessage = ref('')
const isLoading = ref(true)
const error = ref('')
const course = ref<Course | null>(null)
const hole = ref<Hole | null>(null)
const holes = ref<Hole[]>([])
const bagOptions = ref<Club[]>([])
const currentWeather = ref<Conditions | null>(null)
const weatherLoading = ref(false)
const weatherError = ref('')
const recommendation = ref<Recommendation | null>(null)
const recommendationLoading = ref(false)
const recommendationError = ref('')
const holeShots = ref<Shot[]>([])
const holeScore = ref<number | null>(null)
const scoreEntry = ref(4)
const scoreError = ref('')
const savingScore = ref(false)
const shotClubId = ref<number | null>(null)
const endDistance = ref<number | null>(null)
const shotResult = ref('')
const savingShot = ref(false)
const shotError = ref('')
const endingRound = ref(false)
const endRoundError = ref('')
const roundId = roundStore.selectedRoundId

const holeNumber = computed(() => 1)
const courseName = computed(() => course.value?.name || 'Golf course')
const par = computed(() => hole.value?.par ?? 0)
const pinDistance = computed(() => hole.value?.yardage ?? 0)
const hasGpsData = computed(() => Boolean(holeNumber.value === 1 && hole.value && (
  course.value?.name.toLowerCase().includes('stonehenge')
  || hole.value.tee_location || hole.value.pin_location || hole.value.green_geometry || hole.value.fairway_geometry
)))

const conditions = roundStore.conditions
const mappedDistance = ref<number | null>(null)
const liveDistance = computed(() => mappedDistance.value ?? conditions.value.holeDistance ?? null)
function updateMapDistance(distance: number) {
  mappedDistance.value = distance
}
const locationSummary = computed(() => {
  return conditions.value.playerLocation
    ? 'Drag tee marker to adjust your position'
    : 'Drag tee marker to set your position'
})
const windDirectionLabel = computed(() => {
  const degrees = currentWeather.value?.windDirectionDegrees
  if (degrees == null) return 'Direction unavailable'
  return `From ${['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.round(degrees / 45) % 8]}`
})
const windArrowRotation = computed(() => currentWeather.value?.windDirectionDegrees ?? 0)
const canRecordShot = computed(() => Boolean(roundId.value && hole.value?.id && shotClubId.value))
const clubName = (clubId: number) => bagOptions.value.find((club) => club.id === clubId)?.name || 'Club'

async function loadHoleData() {
  if (route.query.hole !== undefined && route.query.hole !== '1') {
    router.replace({ query: { ...route.query, hole: '1' } })
  }
  isLoading.value = true
  error.value = ''

  try {
    const coursesResponse = await getCourses()
    const availableCourses = coursesResponse.data as Course[]
    const requestedCourseId = Number(route.query.course)
    const storedId = roundStore.selectedCourse.value?.id
    let selectedCourse = availableCourses.find((item) => item.id === requestedCourseId)
      || availableCourses.find((item) => item.id === storedId)
    let loadedHoles: Hole[] | null = null
    if (!selectedCourse) {
      for (const candidate of availableCourses) {
        const response = await getCourseHoles(candidate.id)
        if (response.data.length) {
          selectedCourse = candidate
          loadedHoles = response.data
          break
        }
      }
    }
    if (!selectedCourse) throw new Error('No course scorecard data is available yet.')
    const courseChanged = roundStore.selectedCourse.value?.id !== selectedCourse.id
    course.value = selectedCourse
    // sync selected course into roundStore so other views (Caddie) receive the active course
    if (courseChanged) {
      roundStore.setCourse(selectedCourse)
      roundStore.setConditions({ ...conditions.value, playerLocation: null, holeDistance: null, locationAccuracy: null })
    }

    if (loadedHoles) {
      holes.value = loadedHoles.sort((first, second) => first.hole_number - second.hole_number)
    } else if (selectedCourse.id) {
      const courseHolesResponse = await getCourseHoles(selectedCourse.id)
      const apiHoles = courseHolesResponse.data as Hole[]
      holes.value = apiHoles.sort((first, second) => first.hole_number - second.hole_number)
    }
    const localHole = holes.value.find((item) => item.hole_number === holeNumber.value)
    hole.value = null
    if (!localHole) return

    if (selectedCourse) {
      try {
        const holeResponse = await getHole(selectedCourse.id, holeNumber.value)
        hole.value = { ...localHole, ...holeResponse.data }
      } catch {
        hole.value = localHole
      }
    } else {
      hole.value = localHole
    }

    if (!hasGpsData.value) {
      roundStore.setConditions({ ...conditions.value, playerLocation: null, holeDistance: null, locationAccuracy: null })
    }

    const user = authStore.user.value
    if (user) {
      const roundsResponse = await getRounds(user.id)
      const isStartingNewRound = route.query.new === '1'
      const openRounds = roundsResponse.data.filter((round) => !round.is_complete && round.course_id === selectedCourse.id)
      const activeRound = isStartingNewRound ? undefined : (
        openRounds.find((round) => round.id === roundId.value)
          || [...openRounds].sort((a, b) => b.id - a.id)[0]
      )
      if (activeRound) roundStore.setRoundId(activeRound.id)
      else {
        if (!isStartingNewRound) {
          roundStore.setRoundId(null)
          await router.replace('/dashboard')
          return
        }
        roundStore.setConditions({ ...conditions.value, playerLocation: null, holeDistance: null, locationAccuracy: null })
        const newRound = await createRound({ user_id: user.id, course_id: selectedCourse.id, date: new Date().toISOString().slice(0, 10) })
        roundStore.setRoundId(newRound.data.id)
        if (isStartingNewRound) {
          const remainingQuery = { ...route.query }
          delete remainingQuery.new
          router.replace({ query: remainingQuery })
        }
      }
    }
    roundStore.setHole(holeNumber.value)
  } catch {
    error.value = 'Unable to load course data. Check your connection and retry.'
  } finally {
    isLoading.value = false
  }
}

function loadBagOptions(userId: number) {
  getClubs(userId).then((response) => {
    bagOptions.value = response.data
    if (!shotClubId.value && response.data.length) shotClubId.value = response.data[0].id
  }).catch(() => undefined)
}

watch(() => authStore.user.value?.id, (userId) => {
  if (userId) {
    loadBagOptions(userId)
  }
}, { immediate: true })

loadHoleData()

watch([holeNumber, () => route.query.course], () => {
  loadHoleData()
})

function selectBagClub(club: Club) {
  shotClubId.value = club.id
  roundStore.setClub(club)
  bagMessage.value = `${club.name} selected for this hole.`
  showBag.value = false
}

async function loadWeather() {
  if (!course.value?.id || !hole.value) return
  weatherLoading.value = true
  weatherError.value = ''
  currentWeather.value = null
  try {
    const response = await getCurrentWeather(course.value.id, hole.value.hole_number)
    currentWeather.value = response.data
    roundStore.setConditions({ ...conditions.value, ...response.data })
  } catch (requestError: any) {
    currentWeather.value = null
    weatherError.value = requestError?.response?.data?.detail || 'Live weather is unavailable right now.'
  } finally {
    weatherLoading.value = false
  }
}

async function loadRecommendation() {
  if (!hole.value?.id || !conditions.value.playerLocation) {
    recommendation.value = null
    roundStore.clearRecommendation()
    recommendationError.value = ''
    return
  }
  recommendationLoading.value = true
  recommendationError.value = ''
  try {
    const response = await getRecommendation(hole.value.id, conditions.value.playerLocation)
    recommendation.value = response.data
    roundStore.setRecommendation(response.data)
  } catch (requestError: any) {
    recommendation.value = null
    roundStore.clearRecommendation()
    recommendationError.value = requestError?.response?.data?.detail || 'Unable to calculate a shot suggestion.'
  } finally {
    recommendationLoading.value = false
  }
}

async function loadHoleShots() {
  if (!roundId.value || !hole.value?.id) {
    holeShots.value = []
    holeScore.value = null
    return
  }
  try {
    const response = await getShots(roundId.value)
    holeShots.value = response.data.filter((shot) => shot.hole_id === hole.value?.id)
  } catch {
    holeShots.value = []
  }
  try {
    const scores = await getRoundScores(roundId.value)
    holeScore.value = scores.data.find((score: RoundScore) => score.hole_id === hole.value?.id)?.strokes ?? null
  } catch {
    holeScore.value = null
  }
}

function openScoreDialog() {
  scoreEntry.value = holeScore.value ?? (par.value > 0 ? par.value : 1)
  scoreError.value = ''
  showScoreDialog.value = true
}

async function saveScore() {
  const userId = authStore.user.value?.id
  if (!userId || !roundId.value || !hole.value) {
    scoreError.value = 'Start a round before saving a score.'
    return
  }
  savingScore.value = true
  scoreError.value = ''
  try {
    const response = await saveRoundScores(userId, roundId.value, [{ hole_id: hole.value.id, strokes: scoreEntry.value }])
    holeScore.value = response.data[0]?.strokes ?? scoreEntry.value
    showScoreDialog.value = false
    // notify dashboard that a score was updated
    try { window.dispatchEvent(new CustomEvent('scores:updated')) } catch {}
  } catch (requestError: any) {
    scoreError.value = requestError?.response?.data?.detail || 'Unable to save this score.'
  } finally {
    savingScore.value = false
  }
}

async function endRound() {
  if (!roundId.value || endingRound.value) return
  try {
    const savedScores = await getRoundScores(roundId.value)
    const hasScores = savedScores.data.length > 0
    const confirmation = hasScores
      ? 'End this round and save it to your round history?'
      : 'No hole scores have been entered. End this round and save an empty round to your history?'
    if (!window.confirm(confirmation)) return
  } catch (requestError: any) {
    endRoundError.value = requestError?.response?.data?.detail || 'Unable to check your saved scores. Please try again.'
    return
  }
  endingRound.value = true
  endRoundError.value = ''
  try {
    await completeRound(roundId.value)
    roundStore.setRoundId(null)
    showTools.value = false
    await router.push({ path: '/round-summary', query: { round: String(roundId.value) } })
  } catch (requestError: any) {
    endRoundError.value = requestError?.response?.data?.detail || 'Unable to end this round. Try again.'
  } finally {
    endingRound.value = false
  }
}

async function recordShot() {
  if (!canRecordShot.value || !hole.value || !roundId.value || !shotClubId.value) return
  savingShot.value = true
  shotError.value = ''
  try {
    const response = await createShot({
      round_id: roundId.value,
      hole_id: hole.value.id,
      club_id: shotClubId.value,
      start_distance: conditions.value.holeDistance ?? null,
      end_distance: endDistance.value,
      result: shotResult.value || null,
    })
    holeShots.value.push(response.data)
    endDistance.value = null
    shotResult.value = ''
    showShotDialog.value = false
  } catch (requestError: any) {
    shotError.value = requestError?.response?.data?.detail || 'Unable to save this shot.'
  } finally {
    savingShot.value = false
  }
}

function selectRecommendedClub(clubId: number) {
  shotClubId.value = clubId
  showBag.value = false
}

watch(() => [hole.value?.id, course.value?.id, roundId.value], () => {
  currentWeather.value = null
  holeShots.value = []
  holeScore.value = null
  roundStore.setConditions({ ...conditions.value, temperature: null, windSpeed: null, windDirectionDegrees: null, observedAt: null, timezone: null, source: null })
  void loadWeather()
  void loadHoleShots()
}, { immediate: true })

watch(() => [hole.value?.id, conditions.value.playerLocation], () => {
  void loadRecommendation()
}, { deep: true, immediate: true })
</script>
