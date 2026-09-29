<template>
  <div class="pb-28 pt-4 sm:pt-6">
    <AppHeader :course-name="courseName" :hole-label="`Hole ${holeNumber}`" compact />

    <div v-if="isLoading" class="mt-5 space-y-5" aria-live="polite" aria-label="Loading golf data">
      <div class="h-40 animate-pulse rounded-[28px] border border-[#1d3a2d] bg-[#0d2119]"></div>
      <div class="h-64 animate-pulse rounded-[28px] border border-[#1d3a2d] bg-[#10271f]"></div>
    </div>

    <div v-else-if="error" class="mt-5 rounded-[28px] border border-[#5a2f33] bg-[#1c191b] p-5" role="alert">
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#f1b2b9]">Golf data unavailable</p>
      <p class="mt-2 text-sm leading-6 text-[#f7dfe2]">{{ error }}</p>
      <button type="button" class="mt-4 rounded-full bg-[#c8ff00] px-4 py-3 text-xs font-black uppercase tracking-[0.16em] text-[#07140f]" @click="loadHoleData">Retry</button>
    </div>

    <template v-else>
    <div v-if="!hole" class="mx-auto mt-4 max-w-6xl px-4 sm:px-6">
      <div class="rounded-2xl border border-[#6b5632] bg-[#201c13] p-4 text-sm leading-6 text-[#f0d9a8]" role="status">
        <template v-if="holes.length">Hole {{ holeNumber }} is not mapped for {{ courseName }} yet. Only mapped holes are available for play.</template>
        <template v-else>No holes are mapped for {{ courseName }} yet. The course can be selected after its hole data is imported.</template>
        <button v-if="holes.length" type="button" class="ml-2 rounded-full bg-[#c8ff00] px-3 py-1.5 text-xs font-bold text-[#07140f]" @click="selectHole(holes[0].hole_number)">Go to mapped Hole {{ holes[0].hole_number }}</button>
      </div>
    </div>
    <template v-else>
    <section class="relative mt-4 overflow-hidden border-y border-[#214335] bg-[#10271f] sm:mt-6">
      <CourseMap :hole="hole" :course="course" :target="recommendation?.target_location ?? null" :full-screen="true" />

      <div class="pointer-events-none absolute inset-x-3 top-3 z-20 flex items-start justify-between gap-2 sm:inset-x-5 sm:top-5">
        <div class="pointer-events-auto rounded-[22px] border border-white/15 bg-[#101914]/90 px-4 py-3 text-white shadow-xl backdrop-blur-md">
          <p class="max-w-[42vw] truncate text-[9px] font-bold uppercase tracking-[0.2em] text-[#b8d8c8]">{{ courseName }}</p>
          <div class="mt-1 flex items-end gap-3">
            <p class="text-4xl font-black leading-none">{{ holeNumber }}</p>
            <div class="pb-0.5 text-xs text-white/75">
              <span class="font-bold text-white">Par {{ par }}</span>
              <span class="mx-1.5 text-white/35">·</span>
              {{ pinDistance }} YDS
            </div>
          </div>
        </div>
        <div class="pointer-events-auto flex gap-2">
          <button type="button" class="flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-[#101914]/90 text-2xl text-white shadow-xl backdrop-blur-md disabled:opacity-40" aria-label="Previous mapped hole" :disabled="holeIndex <= 0" @click="selectHole(holes[holeIndex - 1]?.hole_number)">‹</button>
          <button type="button" class="flex h-11 w-11 items-center justify-center rounded-full border border-white/15 bg-[#101914]/90 text-2xl text-white shadow-xl backdrop-blur-md disabled:opacity-40" aria-label="Next mapped hole" :disabled="holeIndex < 0 || holeIndex >= holes.length - 1" @click="selectHole(holes[holeIndex + 1]?.hole_number)">›</button>
        </div>
      </div>

      <div class="absolute inset-x-3 bottom-20 z-20 sm:inset-x-5">
        <div class="flex items-center gap-2 overflow-x-auto rounded-2xl border border-white/15 bg-[#101914]/90 p-2 shadow-xl backdrop-blur-md" aria-label="Select hole">
          <button
            v-for="courseHole in holes"
            :key="courseHole.hole_number"
            type="button"
            class="h-9 min-w-9 rounded-xl px-2 text-xs font-black transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c8ff00]"
            :class="courseHole.hole_number === holeNumber ? 'bg-[#c8ff00] text-[#07140f]' : 'text-white/80 hover:bg-white/10'"
            :aria-label="`Select hole ${courseHole.hole_number}`"
            :aria-pressed="courseHole.hole_number === holeNumber"
            @click="selectHole(courseHole.hole_number)"
          >
            {{ courseHole.hole_number }}
          </button>
        </div>
      </div>
    </section>

    <div class="mx-auto max-w-6xl px-4 sm:px-6">
    <section class="mt-5 rounded-[28px] border border-[#1d3a2d] bg-[#0d2119] p-4 shadow-[0_16px_32px_rgba(2,10,7,0.18)] sm:p-5">
      <div class="flex items-end justify-between gap-4">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Hole summary</p>
          <h1 class="mt-1 text-2xl font-black tracking-tight text-white">Hole {{ holeNumber }}</h1>
        </div>
        <div class="flex gap-4 text-right">
          <div>
            <p class="text-[9px] uppercase tracking-[0.2em] text-[#8ca49a]">Par</p>
            <p class="mt-1 text-lg font-black text-white">{{ par }}</p>
          </div>
          <div>
            <p class="text-[9px] uppercase tracking-[0.2em] text-[#8ca49a]">HCP</p>
            <p class="mt-1 text-lg font-black text-white">{{ handicap }}</p>
          </div>
        </div>
      </div>

      <div class="mt-5 rounded-2xl border border-white/10 bg-[#10271f] p-4">
        <p class="text-[9px] font-bold uppercase tracking-[0.2em] text-[#91a69a]">Hole yardage</p>
        <p class="mt-1 text-3xl font-black tracking-tight text-white">{{ pinDistance }} <span class="text-xs font-bold text-[#91a69a]">YDS</span></p>
      </div>
      <p class="mt-3 text-[10px] uppercase tracking-[0.16em] text-[#789084]">Preferred tee: {{ tee }} · GPS distance updates when you locate yourself on the map.</p>
    </section>

    <section class="mt-5 rounded-[26px] border border-white/10 bg-[#0d1d16] p-4 sm:p-5">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-[0.22em] text-[#c8ff00]">Shot log · Hole {{ holeNumber }}</p>
          <p class="mt-1 text-sm text-[#a6b6ad]">Record the club and result after each shot.</p>
        </div>
        <p class="text-xs text-[#91a69a]">{{ holeShots.length }} {{ holeShots.length === 1 ? 'shot' : 'shots' }} logged</p>
      </div>
      <form class="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" @submit.prevent="recordShot">
        <label class="text-xs font-semibold text-[#a6b6ad]">Club
          <select v-model.number="shotClubId" required class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07150f] px-3 py-3 text-sm text-white focus:border-[#c8ff00]">
            <option :value="null" disabled>Select club</option>
            <option v-for="club in bagOptions" :key="club.id" :value="club.id">{{ club.name }}</option>
          </select>
        </label>
        <label class="text-xs font-semibold text-[#a6b6ad]">Distance to target after shot (yd)
          <input v-model.number="endDistance" type="number" min="0" placeholder="Optional" class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07150f] px-3 py-3 text-sm text-white placeholder:text-[#71867a] focus:border-[#c8ff00]" />
        </label>
        <label class="text-xs font-semibold text-[#a6b6ad]">Result
          <select v-model="shotResult" class="mt-1.5 w-full rounded-xl border border-white/10 bg-[#07150f] px-3 py-3 text-sm text-white focus:border-[#c8ff00]">
            <option value="">Choose result</option>
            <option value="fairway">Fairway</option>
            <option value="green">Green</option>
            <option value="bunker">Bunker</option>
            <option value="water">Water</option>
            <option value="rough">Rough</option>
            <option value="other">Other</option>
          </select>
        </label>
        <button type="submit" :disabled="!canRecordShot || savingShot" class="self-end rounded-xl bg-[#c8ff00] px-4 py-3 text-xs font-black uppercase tracking-[0.12em] text-[#07140f] disabled:cursor-not-allowed disabled:opacity-40">{{ savingShot ? 'Saving…' : 'Log shot' }}</button>
      </form>
      <p v-if="shotError" class="mt-3 text-sm text-[#ffaaa9]" role="alert">{{ shotError }}</p>
      <p v-if="!bagOptions.length" class="mt-3 text-sm text-[#f0d9a8]">Add clubs to your bag before logging a shot.</p>
      <div v-if="holeShots.length" class="mt-4 divide-y divide-white/10 rounded-2xl border border-white/10 px-3">
        <div v-for="(shot, index) in holeShots" :key="shot.id" class="flex items-center justify-between gap-3 py-3 text-sm">
          <span class="font-semibold text-white">Shot {{ index + 1 }} · {{ clubName(shot.club_id) }}</span>
          <span class="text-right text-[#a6b6ad]">{{ shot.result || 'Result not set' }}<span v-if="shot.end_distance != null"> · {{ shot.end_distance }} yd remaining</span></span>
        </div>
      </div>
    </section>

    <div class="mt-5 grid gap-5 lg:grid-cols-2 lg:items-start">
      <ConditionsCard
        :weather="currentWeather"
        :loading="weatherLoading"
        :error="weatherError"
      />

      <RecommendationCard
        :recommendation="recommendation"
        :loading="recommendationLoading"
        :error="recommendationError"
        @select-club="selectRecommendedClub"
      />
    </div>

    <section class="mt-5 rounded-[26px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
      <div class="flex items-center justify-between">
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Secondary actions</p>
        <span class="text-[9px] uppercase tracking-[0.18em] text-[#6f8e80]">Round tools</span>
      </div>
      <div class="mt-3 grid grid-cols-3 gap-2">
        <button type="button" class="rounded-2xl border border-[#214335] bg-[#0d2119] px-2 py-3 text-[10px] font-bold uppercase tracking-[0.12em] text-[#dfeee6] transition hover:border-[#668579] focus-visible:outline-none" @click="showBag = true">Bag select</button>
        <button type="button" class="rounded-2xl border border-[#214335] bg-[#0d2119] px-2 py-3 text-[10px] font-bold uppercase tracking-[0.12em] text-[#dfeee6] transition hover:border-[#668579] focus-visible:outline-none" @click="showDispersion = !showDispersion">Dispersion</button>
        <button type="button" class="rounded-2xl bg-[#c8ff00] px-2 py-3 text-[10px] font-black uppercase tracking-[0.12em] text-[#07140f] transition hover:brightness-110 focus-visible:outline-none" @click="router.push('/caddie')">Ask caddie</button>
      </div>
      <div v-if="showDispersion" class="mt-3 rounded-2xl border border-[#214335] bg-[#0b1d17] p-3 text-sm leading-6 text-[#dfeee6]" role="status">
        Dispersion will show your typical left and right miss pattern here once shot history is connected.
      </div>
    </section>
    </div>
    </template>
    </template>

    <div v-if="showBag" class="fixed inset-0 z-50 flex items-end justify-center bg-[#020806]/75 p-3 sm:items-center" @click.self="showBag = false">
      <section class="w-full max-w-md rounded-[28px] border border-[#315441] bg-[#10271f] p-5 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="bag-title">
        <div class="flex items-center justify-between gap-4">
          <div>
            <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Club selection</p>
            <h2 id="bag-title" class="mt-1 text-xl font-black text-white">Choose from your bag</h2>
          </div>
          <button type="button" class="rounded-full border border-[#315441] px-3 py-2 text-xs text-[#dfeee6] focus-visible:outline-none" aria-label="Close club selection" @click="showBag = false">Close</button>
        </div>
        <div class="mt-4 space-y-2">
          <button v-for="club in bagOptions" :key="club.name" type="button" class="flex w-full items-center justify-between rounded-2xl border border-[#214335] bg-[#0d2119] p-3 text-left transition hover:border-[#c8ff00] focus-visible:outline-none" @click="selectBagClub(club)">
            <span class="font-bold text-white">{{ club.name }}</span>
            <span class="text-xs uppercase tracking-[0.14em] text-[#8ca49a]">{{ club.carry_distance ?? club.total_distance ?? '—' }} YDS</span>
          </button>
        </div>
        <p v-if="bagMessage" class="mt-3 text-xs text-[#b8d8c8]" role="status">{{ bagMessage }}</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import RecommendationCard from '../components/RecommendationCard.vue'
import ConditionsCard from '../components/ConditionsCard.vue'
import CourseMap from '../components/CourseMap.vue'
import { roundStore } from '../stores/round'
import { authStore } from '../stores/auth'
import { createRound, createShot, getClubs, getCourses, getCourseHoles, getCurrentWeather, getGolferProfile, getHole, getRecommendation, getRounds, getShots } from '../services/api'
import type { Club, Course, Conditions, GolferProfile, Hole, Recommendation, Shot } from '../types'

const router = useRouter()
const route = useRoute()
const showDispersion = ref(false)
const showBag = ref(false)
const bagMessage = ref('')
const isLoading = ref(true)
const error = ref('')
const course = ref<Course | null>(null)
const hole = ref<Hole | null>(null)
const holes = ref<Hole[]>([])
const profile = ref<GolferProfile | null>(null)
const bagOptions = ref<Club[]>([])
const currentWeather = ref<Conditions | null>(null)
const weatherLoading = ref(false)
const weatherError = ref('')
const recommendation = ref<Recommendation | null>(null)
const recommendationLoading = ref(false)
const recommendationError = ref('')
const holeShots = ref<Shot[]>([])
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
const handicap = computed(() => profile.value?.handicap ?? '—')
const tee = computed(() => profile.value?.preferred_tee || '—')
const pinDistance = computed(() => hole.value?.yardage ?? 0)

const conditions = roundStore.conditions
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

async function loadProfile(userId: number) {
  try {
    const response = await getGolferProfile(userId)
    profile.value = response.data
  } catch {
    profile.value = null
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
    loadProfile(userId)
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
  if (!roundId.value || !hole.value?.id) return
  try {
    const response = await getShots(roundId.value)
    holeShots.value = response.data.filter((shot) => shot.hole_id === hole.value?.id)
  } catch {
    holeShots.value = []
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
  roundStore.setConditions({ ...conditions.value, temperature: null, windSpeed: null, windDirectionDegrees: null, observedAt: null, timezone: null, source: null })
  void loadWeather()
  void loadHoleShots()
}, { immediate: true })

watch(() => [hole.value?.id, conditions.value.playerLocation], () => {
  void loadRecommendation()
}, { deep: true, immediate: true })
</script>
