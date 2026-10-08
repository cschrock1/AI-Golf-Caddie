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

    <section v-if="scoreTrend" class="mt-6 rounded-[28px] border border-[#294b3c] bg-[#10271f] p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)]">
      <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Practice insight · same holes</p>
      <h2 class="mt-2 text-xl font-black text-white">{{ scoreTrend.title }}</h2>
      <p class="mt-2 text-sm leading-6 text-[#a9bbb0]">{{ scoreTrend.detail }}</p>
      <button type="button" class="mt-4 rounded-full border border-white/10 px-4 py-2 text-xs font-bold text-white transition hover:border-[#c8ff00]/50" @click="router.push('/rounds')">Compare scorecards</button>
    </section>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import CourseSearch from '../components/CourseSearch.vue'
import { authStore } from '../stores/auth'
import { getCourses, getGolferProfile, getRoundScores, getRounds } from '../services/api'
import { roundStore } from '../stores/round'
import type { Course, Round, RoundScore } from '../types'

const router = useRouter()
const rounds = ref<Round[]>([])
const scoreTrend = ref<{ title: string; detail: string } | null>(null)

const userName = computed(() => authStore.user.value?.full_name || 'Golfer')
const firstName = computed(() => userName.value.split(/\s+/)[0])
const averageScore = ref<string | number>('—')
const handicap = ref('—')

function selectCourse(course: Course) {
  roundStore.setCourse(course)
}

function startCourseRound(course: Course) {
  roundStore.setCourse(course)
  roundStore.setRoundId(null)
  router.push({ path: '/hole', query: { course: String(course.id), hole: '1', new: '1' } })
}

async function loadScoreTrend(completedRounds: Round[]) {
  const candidates = [...completedRounds]
    .filter((round) => round.is_complete !== false)
    .sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id)
    .slice(0, 24)
  const scoreResults = await Promise.allSettled(candidates.map((round) => getRoundScores(round.id)))
  const groups = new Map<string, Array<{ round: Round; scores: RoundScore[]; total: number }>>()
  scoreResults.forEach((result, index) => {
    if (result.status !== 'fulfilled' || result.value.data.length === 0) return
    const scores = result.value.data
    const signature = scores.map((score) => score.hole_id).sort((a, b) => a - b).join(',')
    const group = groups.get(signature) ?? []
    group.push({ round: candidates[index], scores, total: scores.reduce((sum, score) => sum + score.strokes, 0) })
    groups.set(signature, group)
  })
  const comparable = [...groups.values()]
    .filter((group) => group.length >= 6)
    .sort((a, b) => b[0].round.date.localeCompare(a[0].round.date))[0]
  if (!comparable) return
  const recent = comparable.slice(0, 3)
  const previous = comparable.slice(3, 6)
  const recentAverage = recent.reduce((sum, item) => sum + item.total, 0) / recent.length
  const previousAverage = previous.reduce((sum, item) => sum + item.total, 0) / previous.length
  const difference = recentAverage - previousAverage
  const recentText = recentAverage.toFixed(1).replace(/\.0$/, '')
  if (difference <= -0.5) {
    scoreTrend.value = { title: 'Your scores are moving down', detail: `Across the same ${recent[0].scores.length} scored ${recent[0].scores.length === 1 ? 'hole' : 'holes'}, your latest three rounds averaged ${recentText} strokes—${Math.abs(difference).toFixed(1).replace(/\.0$/, '')} lower than the three before. Keep doing what’s working.` }
  } else if (difference >= 0.5) {
    scoreTrend.value = { title: 'Pick one hole to work on', detail: `Across the same ${recent[0].scores.length} scored ${recent[0].scores.length === 1 ? 'hole' : 'holes'}, your latest three rounds averaged ${recentText} strokes—${difference.toFixed(1).replace(/\.0$/, '')} higher than the three before. Compare those scorecards to spot where shots are adding up.` }
  } else {
    scoreTrend.value = { title: 'Your scoring is steady', detail: `Your latest six comparable rounds are staying close to the same score across ${recent[0].scores.length} scored ${recent[0].scores.length === 1 ? 'hole' : 'holes'}. Track club and shot results to build a more specific practice focus.` }
  }
}

async function computeAverageFromRounds(currentRounds: Round[]) {
  const me = authStore.user.value
  if (!me) {
    averageScore.value = '—'
    return
  }

  // consider all rounds returned; prefer server-stored round totals when available
  const candidates = currentRounds
  if (!candidates.length) {
    averageScore.value = '—'
    return
  }

  let totalSum = 0
  let count = 0

  // first pass: use any server-stored round.score when present and valid
  for (const r of candidates) {
    if (typeof r.score === 'number') {
      totalSum += r.score
      count += 1
    }
  }

  // second pass: for rounds without stored score, fetch their per-hole scores and include only those with 18 numeric entries
  const toFetch = candidates.filter((r) => typeof r.score !== 'number')
  if (toFetch.length) {
    const results = await Promise.allSettled(toFetch.map((r) => getRoundScores(r.id)))
    results.forEach((res, idx) => {
      if (res.status !== 'fulfilled') return
      const scores = res.value.data
      if (!scores || scores.length < 18) return
      if (!scores.every((s) => typeof s.strokes === 'number')) return
      const roundTotal = scores.reduce((s, it) => s + it.strokes, 0)
      totalSum += roundTotal
      count += 1
    })
  }

  if (count === 0) {
    averageScore.value = '—'
    return
  }
  const avg = totalSum / count
  averageScore.value = Number.isInteger(avg) ? Math.round(avg) : Number(avg.toFixed(1))
}

function handleRoundsUpdate() {
  const me = authStore.user.value
  if (!me) return
  // refresh rounds from server and recompute
  void getRounds(me.id).then((resp) => {
    rounds.value = resp.data
    void computeAverageFromRounds(resp.data)
    void loadScoreTrend(resp.data)
  }).catch(() => {
    rounds.value = []
    averageScore.value = '—'
    scoreTrend.value = null
  })
}

onMounted(async () => {
  const me = authStore.user.value
  if (!me) return

  try {
    const [roundsResponse, profileResponse, coursesResponse] = await Promise.all([
      getRounds(me.id),
      getGolferProfile(me.id),
      getCourses()
    ])
    rounds.value = roundsResponse.data
    handicap.value = profileResponse.data.handicap ?? '—'
    const activeRoundId = roundStore.selectedRoundId.value
    const activeRound = activeRoundId === null
      ? undefined
      : roundsResponse.data.find((round) => round.id === activeRoundId && !round.is_complete)
    if (activeRound) {
      roundStore.setRoundId(activeRound.id)
      const activeCourse = coursesResponse.data.find((course) => course.id === activeRound.course_id)
      if (activeCourse) roundStore.setCourse(activeCourse)
    } else {
      roundStore.setRoundId(null)
    }
    void loadScoreTrend(roundsResponse.data)
    void computeAverageFromRounds(roundsResponse.data)
    // listen for round/score changes elsewhere in the app
    window.addEventListener('round:completed', handleRoundsUpdate)
    window.addEventListener('scores:updated', handleRoundsUpdate)
  } catch {
    rounds.value = []
    handicap.value = '—'
    scoreTrend.value = null
    roundStore.setRoundId(null)
  }
})

onUnmounted(() => {
  window.removeEventListener('round:completed', handleRoundsUpdate)
  window.removeEventListener('scores:updated', handleRoundsUpdate)
})
</script>
