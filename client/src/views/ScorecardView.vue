<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="courseName" :hole-label="'Round 2'" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Scorecard</p>
          <h1 class="mt-2 text-3xl font-black text-white">Stonehedge Golf Course</h1>
        </div>
        <div class="text-sm text-[#dfeee6]">
          <span class="text-[#8ca49a]">Player:</span> {{ playerName }}
        </div>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Round</p>
          <p class="mt-2 text-base font-bold text-white">Sep 4, 2026</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Total</p>
          <p class="mt-2 text-base font-bold text-white">{{ liveTotal ?? '--' }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Par</p>
          <p class="mt-2 text-base font-bold text-white">72</p>
        </div>
      </div>
    </section>

    <div class="mt-6">
      <ScorecardTable
        :course-name="courseName"
        :holes="holes"
        :round-id="roundId"
        :user-id="userId"
        @total-updated="updateLiveTotal"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import ScorecardTable from '../components/ScorecardTable.vue'
import { createRound, getCourses, getRounds, getCourse } from '../services/api'
import { roundStore } from '../stores/round'
import { authStore } from '../stores/auth'

const playerName = computed(() => authStore.user.value?.full_name || 'Golfer')

const courseName = 'Stonehedge Golf Course'

const holes = [
  { hole: 1, par: 4, score: null },
  { hole: 2, par: 5, score: null },
  { hole: 3, par: 3, score: null },
  { hole: 4, par: 4, score: null },
  { hole: 5, par: 4, score: null },
  { hole: 6, par: 3, score: null },
  { hole: 7, par: 3, score: null },
  { hole: 8, par: 5, score: null },
  { hole: 9, par: 4, score: null },
  { hole: 10, par: 4, score: null },
  { hole: 11, par: 5, score: null },
  { hole: 12, par: 4, score: null },
  { hole: 13, par: 3, score: null },
  { hole: 14, par: 4, score: null },
  { hole: 15, par: 5, score: null },
  { hole: 16, par: 4, score: null },
  { hole: 17, par: 3, score: null },
  { hole: 18, par: 4, score: null }
]
const userId = computed(() => authStore.user.value?.id ?? null)
const roundId = ref<number | null>(null)
const liveTotal = ref<number | null>(null)

function updateLiveTotal(total: number | null) {
  liveTotal.value = total
}

onMounted(async () => {
  if (!userId.value) return

  try {
    const response = await getRounds(userId.value)
    const existingRound = response.data.reduce((latest, candidate) => (
      candidate.id > latest.id ? candidate : latest
    ), response.data[0])
    if (existingRound) {
      roundId.value = existingRound.id
      try {
        const courseResp = await getCourse(existingRound.course_id)
        console.log('ScorecardView: existingRound selected', { existingRound })
        console.log('ScorecardView: fetched course for existingRound', courseResp.data)
        roundStore.setCourse(courseResp.data)
        // set shared active round id
        try { roundStore.setRoundId(existingRound.id) } catch {}
        // clear demo conditions when a real round is active
        roundStore.setConditions({ windSpeed: undefined as any, windDirection: '', temperature: undefined as any, elevation: undefined as any, note: '' })
        roundStore.setHole(1)
      } catch {
        // ignore if course lookup fails
      }
      return
    }

    const coursesResponse = await getCourses()
    const course = coursesResponse.data.find(item => item.name === courseName) ?? coursesResponse.data[0]
    if (!course) return

    const newRound = await createRound({
      user_id: userId.value,
      course_id: course.id,
      date: new Date().toISOString().slice(0, 10),
      score: null
    })
    roundId.value = newRound.data.id
    console.log('ScorecardView: created new round', { newRound: newRound.data, course })
    // set the active course/hole in the central round store so Caddie and other views update
    roundStore.setCourse(course)
    try { roundStore.setRoundId(newRound.data.id) } catch {}
    // clear demo conditions when a real round is active; CourseMap will publish GPS distance into conditions
    roundStore.setConditions({ windSpeed: undefined as any, windDirection: '', temperature: undefined as any, elevation: undefined as any, note: '' })
    roundStore.setHole(1)
  } catch {
    roundId.value = null
  }
})
</script>
