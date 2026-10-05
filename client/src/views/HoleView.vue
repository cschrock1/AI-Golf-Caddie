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
      <p class="text-xs font-bold uppercase tracking-[0.2em] text-[#f0d9a8]">Hole not mapped yet</p>
      <h1 class="mt-3 text-2xl font-black">{{ courseName }}</h1>
      <p class="mt-2 text-sm leading-6 text-white/70">Only mapped holes are available for play. This course currently has {{ holes.length }} mapped {{ holes.length === 1 ? 'hole' : 'holes' }}.</p>
      <button v-if="holes.length" type="button" class="mt-5 rounded-xl bg-[#c8ff00] px-5 py-3 text-sm font-bold text-[#07140f]" @click="selectHole(holes[0].hole_number)">Open mapped Hole {{ holes[0].hole_number }}</button>
      <button type="button" class="ml-2 mt-5 rounded-xl border border-white/15 px-5 py-3 text-sm font-semibold" @click="router.push('/dashboard')">Back</button>
    </section>
  </main>

  <main v-else class="fixed inset-0 z-30 overflow-hidden bg-[#101914] text-white">
    <CourseMap :hole="hole" :course="course" :target="recommendation?.target_location ?? null" :full-screen="true" />

    <header class="pointer-events-none absolute inset-x-3 top-3 z-20 flex items-start gap-2 sm:inset-x-5 sm:top-5">
      <button type="button" class="pointer-events-auto grid h-12 w-12 shrink-0 place-items-center rounded-full bg-[#111512]/95 text-3xl shadow-xl backdrop-blur" aria-label="Back to dashboard" @click="router.push('/dashboard')">‹</button>

      <section class="pointer-events-auto min-w-0 flex-1 overflow-hidden rounded-[22px] bg-[#151a18]/95 shadow-xl backdrop-blur-md">
        <p class="truncate px-4 pt-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-white/55">{{ courseName }}</p>
        <div class="flex items-center">
          <div class="flex min-w-[112px] items-center gap-3 rounded-[20px] bg-[#111312] px-4 py-2.5">
            <span class="text-4xl font-black leading-none">{{ holeNumber }}</span>
            <div class="min-w-0">
              <p class="truncate text-xs font-semibold text-white/65">Mapped tee</p>
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
            <div class="flex flex-col gap-1">
              <button type="button" class="grid h-7 w-7 place-items-center rounded-full bg-white/10 text-lg disabled:opacity-30" aria-label="Previous mapped hole" :disabled="holeIndex <= 0" @click="selectHole(holes[holeIndex - 1]?.hole_number)">‹</button>
              <button type="button" class="grid h-7 w-7 place-items-center rounded-full bg-white/10 text-lg disabled:opacity-30" aria-label="Next mapped hole" :disabled="holeIndex < 0 || holeIndex >= holes.length - 1" @click="selectHole(holes[holeIndex + 1]?.hole_number)">›</button>
            </div>
          </div>
        </div>
      </section>
    </header>

    <div class="absolute left-3 top-[38%] z-20 rounded-[28px] bg-white text-[#161817] shadow-xl sm:left-6">
      <div class="flex items-center gap-3 pr-4">
        <div class="grid min-h-[82px] min-w-[82px] place-items-center rounded-full bg-[#151817] px-3 text-center text-white">
          <span class="text-3xl font-black leading-none">{{ liveDistance ?? pinDistance ?? '—' }}<span class="ml-0.5 text-xs">y</span></span>
        </div>
        <div class="py-2">
          <p class="text-xs text-[#666]">{{ liveDistance != null ? 'To pin' : 'Tee to pin' }}</p>
          <p class="text-xl font-bold leading-tight">{{ liveDistance != null ? 'GPS distance' : 'Hole yardage' }}</p>
        </div>
      </div>
    </div>

    <aside class="absolute right-3 top-[42%] z-20 w-[94px] rounded-[24px] bg-[#151817]/95 px-3 py-3 text-center shadow-xl backdrop-blur sm:right-6" aria-label="Current wind conditions">
      <div class="flex items-center justify-center gap-1 text-sm font-semibold">Wind <span class="grid h-5 w-5 place-items-center rounded-full bg-[#2588ef] text-xs">›</span></div>
      <p class="my-2 text-4xl leading-none" :style="{ transform: `rotate(${windArrowRotation}deg)` }" aria-hidden="true">↑</p>
      <p class="text-lg font-bold leading-tight">{{ currentWeather?.windSpeed ?? '—' }}<span class="ml-1 text-xs font-medium">mph</span></p>
      <p class="mt-1 truncate text-[9px] uppercase tracking-wide text-white/55">{{ weatherLoading ? 'Updating' : windDirectionLabel }}</p>
      <p v-if="weatherError && !weatherLoading" class="mt-1 text-[9px] leading-tight text-white/45">Unavailable</p>
    </aside>

    <footer class="pointer-events-none absolute inset-x-3 bottom-[calc(env(safe-area-inset-bottom)+1rem)] z-20 flex flex-col gap-2 sm:inset-x-auto sm:right-8 sm:w-[min(560px,calc(100%-4rem))] sm:left-1/2 sm:-translate-x-1/2">
      <button type="button" class="pointer-events-auto flex h-[68px] items-center justify-center gap-4 rounded-[20px] bg-[#171a19]/95 px-5 text-lg font-bold shadow-xl backdrop-blur transition active:scale-[0.99]" @click="showShotDialog = true">
        <span class="grid h-12 w-12 place-items-center rounded-2xl bg-[#101211] text-2xl" aria-hidden="true">⌖</span>
        <span>Track shot</span>
        <span class="text-xs font-medium text-white/55">{{ holeShots.length ? `${holeShots.length} logged` : 'Add shot' }}</span>
      </button>

      <nav class="pointer-events-auto grid grid-cols-[74px_42px_1fr_42px_74px] items-stretch gap-1.5">
        <button type="button" class="flex min-h-[74px] flex-col items-center justify-center rounded-[18px] bg-[#171a19]/95 text-[11px] font-semibold shadow-xl" @click="router.push('/scorecard')">Scorecard<span class="mt-1 text-[#2588ef]">●</span></button>
        <button type="button" class="rounded-[18px] bg-[#171a19]/95 text-3xl disabled:opacity-30" aria-label="Previous mapped hole" :disabled="holeIndex <= 0" @click="selectHole(holes[holeIndex - 1]?.hole_number)">‹</button>
        <button type="button" class="rounded-[18px] bg-[#2588ef] px-2 py-2 text-center shadow-xl" aria-label="Enter score for this hole" @click="openScoreDialog">
          <span class="block text-xl font-black">Hole {{ holeNumber }}</span>
          <span class="block text-sm">{{ holeScore != null ? `Score ${holeScore}` : 'Enter score' }}</span>
        </button>
        <button type="button" class="rounded-[18px] bg-[#171a19]/95 text-3xl disabled:opacity-30" aria-label="Next mapped hole" :disabled="holeIndex < 0 || holeIndex >= holes.length - 1" @click="selectHole(holes[holeIndex + 1]?.hole_number)">›</button>
        <button type="button" class="flex min-h-[74px] flex-col items-center justify-center rounded-[18px] bg-[#171a19]/95 text-[11px] font-semibold shadow-xl" @click="showTools = true">Tools<span class="mt-1 text-[#2588ef]">●</span></button>
      </nav>
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
import { createRound, createShot, getClubs, getCourses, getCourseHoles, getCurrentWeather, getHole, getRecommendation, getRoundScores, getRounds, getShots, saveRoundScores } from '../services/api'
import type { Club, Course, Conditions, Hole, Recommendation, RoundScore, Shot } from '../types'

const router = useRouter()
const route = useRoute()
const showBag = ref(false)
const showTools = ref(false)
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
const roundId = roundStore.selectedRoundId

const holeNumber = computed(() => {
  const requestedHole = Number(route.query.hole)
  return holes.value.some((item) => item.hole_number === requestedHole)
    ? requestedHole
    : Number.isInteger(requestedHole) && requestedHole >= 1 && requestedHole <= 18
      ? requestedHole
      : holes.value[0]?.hole_number ?? 1
})
const holeIndex = computed(() => holes.value.findIndex((item) => item.hole_number === holeNumber.value))
const courseName = computed(() => course.value?.name || 'Golf course')
const par = computed(() => hole.value?.par ?? 0)
const pinDistance = computed(() => hole.value?.yardage ?? 0)

const conditions = roundStore.conditions
const liveDistance = computed(() => conditions.value.holeDistance ?? null)
const windDirectionLabel = computed(() => {
  const degrees = currentWeather.value?.windDirectionDegrees
  if (degrees == null) return 'Direction unavailable'
  return `From ${['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.round(degrees / 45) % 8]}`
})
const windArrowRotation = computed(() => currentWeather.value?.windDirectionDegrees ?? 0)
const canRecordShot = computed(() => Boolean(roundId.value && hole.value?.id && shotClubId.value))
const clubName = (clubId: number) => bagOptions.value.find((club) => club.id === clubId)?.name || 'Club'

async function loadHoleData() {
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
    if (!selectedCourse) throw new Error('No courses with mapped holes are available yet.')
    const courseChanged = roundStore.selectedCourse.value?.id !== selectedCourse.id
    course.value = selectedCourse
    // sync selected course into roundStore so other views (Caddie) receive the active course
    if (courseChanged) {
      roundStore.setCourse(selectedCourse)
      roundStore.setConditions({ ...conditions.value, playerLocation: null, holeDistance: null })
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

    const user = authStore.user.value
    if (user) {
      const roundsResponse = await getRounds(user.id)
      const activeRound = roundsResponse.data.find((round) => round.id === roundId.value && round.course_id === selectedCourse.id)
        || [...roundsResponse.data].filter((round) => round.course_id === selectedCourse.id).sort((a, b) => b.id - a.id)[0]
      if (activeRound) roundStore.setRoundId(activeRound.id)
      else {
        const newRound = await createRound({ user_id: user.id, course_id: selectedCourse.id, date: new Date().toISOString().slice(0, 10) })
        roundStore.setRoundId(newRound.data.id)
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

function selectHole(nextHole?: number) {
  if (!nextHole) return
  router.replace({ query: { ...route.query, hole: String(nextHole) } })
  // keep central round store in sync with selected hole
  roundStore.setHole(nextHole)
}

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
  } catch (requestError: any) {
    scoreError.value = requestError?.response?.data?.detail || 'Unable to save this score.'
  } finally {
    savingScore.value = false
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
