<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader course-name="Round history" hole-label="Previous scorecards" />

    <main class="mt-6">
      <section class="rounded-[30px] border border-white/10 bg-[#0d1d16] p-5 sm:p-7">
        <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Your rounds</p>
        <h1 class="mt-2 text-3xl font-black text-white">Previous rounds & scorecards</h1>
        <p class="mt-2 text-sm text-[#a6b6ad]">Open a round to review its saved scores.</p>
      </section>

      <p v-if="loading" class="mt-4 rounded-2xl border border-white/10 bg-[#10271f] p-4 text-sm text-[#a6b6ad]" role="status">Loading your rounds…</p>
      <div v-else-if="error" class="mt-4 rounded-2xl border border-[#70434a] bg-[#211719] p-4 text-sm text-[#f0b9ba]" role="alert">
        <p>{{ error }}</p>
        <button type="button" class="mt-3 rounded-full bg-[#c8ff00] px-4 py-2 text-xs font-black uppercase tracking-wide text-[#07140f]" @click="loadRounds">Try again</button>
      </div>
      <div v-else-if="rounds.length" class="mt-4 space-y-3">
        <div
          v-for="round in rounds"
          :key="round.id"
          class="flex items-center gap-3 rounded-[24px] border border-white/10 bg-[#10271f] p-4 transition hover:border-[#c8ff00]/45 sm:p-5"
        >
          <button type="button" class="flex min-w-0 flex-1 items-center justify-between gap-4 text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c8ff00]" @click="openScorecard(round.id)">
            <span class="min-w-0">
              <span class="block truncate text-lg font-bold text-white">{{ courseName(round.course_id) }}</span>
              <span class="mt-1 block text-sm text-[#a6b6ad]">{{ formatDate(round.date) }}</span>
            </span>
            <span class="shrink-0 text-right">
              <span class="block text-2xl font-black text-[#c8ff00]">{{ round.scoreTotal ?? '—' }}</span>
              <span class="mt-1 block text-[10px] font-bold uppercase tracking-[0.14em] text-[#91a69a]">{{ round.scoreTotal == null ? 'No scores' : 'Strokes' }}</span>
            </span>
          </button>
          <button type="button" :disabled="deletingRoundId === round.id" class="shrink-0 rounded-xl border border-[#ffaaa9]/30 px-3 py-2 text-xs font-bold text-[#ffcfce] disabled:opacity-50" :aria-label="`Delete round at ${courseName(round.course_id)} from ${formatDate(round.date)}`" @click="deleteHistoryRound(round.id)">
            {{ deletingRoundId === round.id ? 'Deleting…' : 'Delete' }}
          </button>
        </div>
        <p v-if="deleteError" class="rounded-xl border border-[#70434a] bg-[#211719] p-3 text-sm text-[#f0b9ba]" role="alert">{{ deleteError }}</p>
      </div>
      <div v-else class="mt-4 rounded-[24px] border border-dashed border-white/15 bg-[#10271f] p-6 text-center">
        <p class="text-lg font-bold text-white">{{ inProgressCount ? 'Round in progress' : 'No rounds yet' }}</p>
        <p class="mt-2 text-sm text-[#a6b6ad]">{{ inProgressCount ? 'End your current round from GPS → More round tools to move it into history.' : 'Start a round and your saved scorecards will appear here.' }}</p>
        <button type="button" class="mt-4 rounded-full bg-[#c8ff00] px-5 py-3 text-xs font-black uppercase tracking-wide text-[#07140f]" @click="router.push(inProgressCount ? '/hole' : '/dashboard')">{{ inProgressCount ? 'Return to GPS' : 'Find a course' }}</button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import { deleteRound as deleteRoundRequest, getCourses, getRoundScores, getRounds } from '../services/api'
import { authStore } from '../stores/auth'
import { roundStore } from '../stores/round'
import type { Course, Round } from '../types'

type HistoryRound = Round & { scoreTotal: number | null }

const router = useRouter()
const loading = ref(true)
const error = ref('')
const rounds = ref<HistoryRound[]>([])
const courses = ref<Course[]>([])
const deletingRoundId = ref<number | null>(null)
const deleteError = ref('')
const inProgressCount = ref(0)

function courseName(courseId: number) {
  return courses.value.find((course) => course.id === courseId)?.name ?? 'Golf course'
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(new Date(`${date}T00:00:00`))
}

function openScorecard(roundId: number) {
  router.push({ path: '/scorecard', query: { round: String(roundId) } })
}

async function deleteHistoryRound(roundId: number) {
  const user = authStore.user.value
  const round = rounds.value.find((item) => item.id === roundId)
  if (!user || !round || deletingRoundId.value != null) return
  if (!window.confirm(`Delete this ${courseName(round.course_id)} round and its saved scores and shots? This cannot be undone.`)) return
  deletingRoundId.value = roundId
  deleteError.value = ''
  try {
    await deleteRoundRequest(roundId, user.id)
    rounds.value = rounds.value.filter((item) => item.id !== roundId)
    if (roundStore.selectedRoundId.value === roundId) roundStore.setRoundId(null)
  } catch (requestError: any) {
    deleteError.value = requestError?.response?.data?.detail || 'Unable to delete this round. Try again.'
  } finally {
    deletingRoundId.value = null
  }
}

async function loadRounds() {
  const user = authStore.user.value
  if (!user) {
    error.value = 'Sign in to view your rounds.'
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [roundResponse, courseResponse] = await Promise.all([getRounds(user.id), getCourses()])
    courses.value = courseResponse.data
    // Older deployed APIs omit is_complete; treat those legacy rows as history during rollout.
    inProgressCount.value = roundResponse.data.filter((round) => round.is_complete === false).length
    const sorted = [...roundResponse.data].filter((round) => round.is_complete !== false).sort((first, second) => second.date.localeCompare(first.date) || second.id - first.id)
    rounds.value = await Promise.all(sorted.map(async (round) => {
      try {
        const scores = await getRoundScores(round.id)
        const total = scores.data.reduce((sum, score) => sum + score.strokes, 0)
        return { ...round, scoreTotal: total || round.score || null }
      } catch {
        return { ...round, scoreTotal: round.score ?? null }
      }
    }))
  } catch {
    error.value = 'Unable to load your rounds. Check your connection and try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadRounds)
</script>
