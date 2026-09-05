<template>
  <div class="mx-auto max-w-6xl px-4 pb-36 pt-4 sm:px-6 sm:pt-6">
    <AppHeader :course-name="courseName" :hole-label="`Hole ${holeNumber}`" />

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

      <div class="mt-5 grid grid-cols-2 gap-3">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[9px] uppercase tracking-[0.2em] text-[#8ca49a]">Center pin</p>
          <p class="mt-1 text-3xl font-black tracking-tight text-white">{{ pinDistance }} <span class="text-xs font-bold text-[#8ca49a]">YDS</span></p>
        </div>
        <div class="rounded-2xl border border-[#c8ff00]/30 bg-[#142d20] p-3">
          <p class="text-[9px] uppercase tracking-[0.2em] text-[#b8d8c8]">Playing</p>
          <p class="mt-1 text-3xl font-black tracking-tight text-[#c8ff00]">{{ playingDistance }} <span class="text-xs font-bold text-[#b8d8c8]">YDS</span></p>
        </div>
      </div>
      <p class="mt-3 text-[10px] uppercase tracking-[0.16em] text-[#6f8e80]">{{ tee }} · Course and hole data from API</p>
    </section>

    <div class="mt-5 grid gap-5 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
      <ConditionsCard
        class="lg:col-start-2 lg:row-start-1"
        :wind-speed="conditions.windSpeed"
        :wind-direction="conditions.windDirection"
        :temperature="conditions.temperature"
        :note="conditions.note"
      />

      <CourseMap class="lg:col-start-1 lg:row-span-2 lg:row-start-1" :hole="hole" />

      <RecommendationCard
        class="lg:col-start-2 lg:row-start-2"
        :club-name="recommendation.clubName"
        :confidence="recommendation.confidence"
        :carry="recommendation.carry"
        :tempo="recommendation.tempo"
        :landing="recommendation.landing"
        :target="recommendation.target"
        :rationale="recommendation.rationale"
        :alternative-club="recommendation.alternativeClub"
        :alternative-risk="recommendation.alternativeRisk"
        :locked="isLocked"
        @lock-in="isLocked = !isLocked"
      />
    </div>

    <section class="mt-5 rounded-[26px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
      <div class="flex items-center justify-between">
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Secondary actions</p>
        <span class="text-[9px] uppercase tracking-[0.18em] text-[#6f8e80]">Demo controls</span>
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
            <span class="text-xs uppercase tracking-[0.14em] text-[#8ca49a]">{{ club.carry }} YDS</span>
          </button>
        </div>
        <p v-if="bagMessage" class="mt-3 text-xs text-[#b8d8c8]" role="status">{{ bagMessage }}</p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import RecommendationCard from '../components/RecommendationCard.vue'
import ConditionsCard from '../components/ConditionsCard.vue'
import CourseMap from '../components/CourseMap.vue'
import { demoHole } from '../mock/hole'
import { roundStore } from '../stores/round'
import { authStore } from '../stores/auth'
import { getClubs, getCourses, getGolferProfile, getHole } from '../services/api'
import type { Club, Course, GolferProfile, Hole } from '../types'

const router = useRouter()
const showDispersion = ref(false)
const showBag = ref(false)
const isLocked = ref(false)
const bagMessage = ref('')
const isLoading = ref(true)
const error = ref('')
const course = ref<Course | null>(null)
const hole = ref<Hole | null>(null)
const profile = ref<GolferProfile | null>(null)
const bagOptions = ref<Array<{ name: string; carry: number }>>([
  { name: '9-Iron', carry: 112 },
  { name: 'Pitching Wedge', carry: 106 },
  { name: '8-Iron', carry: 124 }
])

const holeNumber = demoHole.holeNumber
const courseName = computed(() => course.value?.name || 'Golf course')
const par = computed(() => hole.value?.par ?? 0)
const handicap = computed(() => profile.value?.handicap ?? '—')
const tee = computed(() => profile.value?.preferred_tee || '—')
const pinDistance = computed(() => hole.value?.yardage ?? 0)
const playingDistance = computed(() => hole.value?.yardage ? hole.value.yardage + 7 : 0)

const recommendation = roundStore.recommendation
const conditions = roundStore.conditions

async function loadHoleData() {
  isLoading.value = true
  error.value = ''

  try {
    const coursesResponse = await getCourses()
    const selectedCourse = (coursesResponse.data as Course[]).find((item) => item.name === demoHole.courseName) || coursesResponse.data[0]
    if (!selectedCourse) throw new Error('No courses available')

    const holeResponse = await getHole(selectedCourse.id, holeNumber)
    course.value = selectedCourse
    hole.value = holeResponse.data
  } catch {
    error.value = 'Unable to load golf data. Please try again.'
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
    const clubs = response.data as Club[]
    if (clubs.length) {
      bagOptions.value = clubs.map((club) => ({ name: club.name, carry: Math.round(club.carry_distance || club.total_distance || 0) }))
    }
  }).catch(() => undefined)
}

watch(() => authStore.user.value?.id, (userId) => {
  if (userId) {
    loadBagOptions(userId)
    loadProfile(userId)
  }
}, { immediate: true })

loadHoleData()

function selectBagClub(club: { name: string; carry: number }) {
  bagMessage.value = `${club.name} selected for comparison.`
}
</script>
