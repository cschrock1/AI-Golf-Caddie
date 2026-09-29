<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-4 sm:px-6 sm:pt-7">
    <AppHeader :course-name="'Dashboard'" :hole-label="'Home'" />

    <section class="mt-5 overflow-hidden rounded-[30px] border border-white/10 bg-[radial-gradient(ellipse_at_top_right,_rgba(200,255,0,0.13),_transparent_45%),linear-gradient(135deg,#10271f,#0a1711)] p-5 shadow-[0_24px_70px_rgba(0,0,0,0.28)] sm:p-7">
      <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Your golf, at a glance</p>
      <h1 class="mt-2 text-3xl font-black tracking-tight text-white sm:text-4xl">Welcome back, {{ firstName }}</h1>
      <p class="mt-2 max-w-lg text-sm leading-6 text-[#a9bbb0]">Pick a course to start a round, or head back to the hole you were playing.</p>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Rounds logged</p>
          <p class="mt-2 text-2xl font-black text-white">{{ rounds.length }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Avg. completed score</p>
          <p class="mt-2 text-2xl font-black text-white">{{ averageScore }}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Handicap</p>
          <p class="mt-2 text-2xl font-black text-white">{{ handicap }}</p>
        </div>
      </div>
    </section>

    <CourseSearch class="mt-6" @select="selectCourse" @start="startCourseRound" />

    <section class="mt-6 rounded-[28px] border border-white/10 bg-[#0d1d16] p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)]">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Latest round</p>
          <h2 class="mt-2 text-xl font-black text-white">{{ latestRound ? formatDate(latestRound.date) : 'Your rounds will show up here' }}</h2>
          <p class="mt-1 text-sm text-[#9aada2]">{{ latestRound ? (latestRound.score ? `Final score ${latestRound.score}` : 'Score not recorded yet') : 'Start a round to begin building your history.' }}</p>
        </div>
        <button v-if="latestRound" type="button" class="rounded-full border border-white/10 px-4 py-2.5 text-xs font-bold text-white transition hover:border-[#c8ff00]/50" @click="router.push('/scorecard')">Open scorecard</button>
      </div>
    </section>

    <section class="mt-6 rounded-[28px] border border-white/10 bg-[#0d1d16] p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)]">
      <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Quick actions</p>
      <div class="mt-4 grid gap-3 sm:grid-cols-3">
        <button type="button" class="rounded-full bg-[#c8ff00] px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-[#07140f] transition hover:brightness-110" @click="router.push('/hole')">
          Start round
        </button>
        <button type="button" class="rounded-full border border-white/10 bg-[#10271f] px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-white transition hover:border-[#c8ff00]/50" @click="router.push('/bag')">
          View bag
        </button>
        <button type="button" class="rounded-full border border-white/10 bg-[#10271f] px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-white transition hover:border-[#c8ff00]/50" @click="router.push('/scorecard')">
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
import CourseSearch from '../components/CourseSearch.vue'
import { authStore } from '../stores/auth'
import { getGolferProfile, getRounds } from '../services/api'
import { roundStore } from '../stores/round'
import type { Course } from '../types'

const router = useRouter()
const rounds = ref<Array<{ id: number; date: string; score?: number | null }>>([])

const userName = computed(() => authStore.user.value?.full_name || 'Golfer')
const firstName = computed(() => userName.value.split(/\s+/)[0])
const latestRound = computed(() => [...rounds.value].sort((a, b) => b.id - a.id)[0] ?? null)
const averageScore = computed(() => {
  const completed = rounds.value.filter((round) => typeof round.score === 'number')
  if (!completed.length) return '—'
  return Math.round(completed.reduce((sum, round) => sum + round.score!, 0) / completed.length)
})
const handicap = ref('—')

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(`${date}T00:00:00`))
}

function selectCourse(course: Course) {
  roundStore.setCourse(course)
}

function startCourseRound(course: Course) {
  roundStore.setCourse(course)
  router.push({ path: '/hole', query: { course: String(course.id), hole: '1' } })
}

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
