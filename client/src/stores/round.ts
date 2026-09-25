import { computed, ref } from 'vue'
import type { Club, Conditions, Course, Recommendation } from '../types'
import { demoConditions, demoRecommendation } from '../mock/recommendation'

function storedCourse() {
  if (typeof window === 'undefined') return null
  try {
    return JSON.parse(localStorage.getItem('aigc_selected_course') || 'null') as Course | null
  } catch {
    return null
  }
}

const selectedCourse = ref<Course | null>(storedCourse())
function storedRoundId() {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem('aigc_active_round_id')
    return raw ? Number(raw) : null
  } catch {
    return null
  }
}
const selectedRoundId = ref<number | null>(storedRoundId())
const selectedHole = ref<number>(1)
const selectedClub = ref<Club | null>(null)
const recommendation = ref<Recommendation>(demoRecommendation)
const conditions = ref<Conditions>(demoConditions)

function setCourse(course: Course | null) {
  selectedCourse.value = course
  if (typeof window !== 'undefined') {
    if (course) localStorage.setItem('aigc_selected_course', JSON.stringify(course))
    else localStorage.removeItem('aigc_selected_course')
  }
}

function setRoundId(roundId: number | null) {
  selectedRoundId.value = roundId
  if (typeof window !== 'undefined') {
    if (roundId !== null) localStorage.setItem('aigc_active_round_id', String(roundId))
    else localStorage.removeItem('aigc_active_round_id')
  }
}

function setHole(holeNumber: number) {
  selectedHole.value = holeNumber
}

function setClub(club: Club | null) {
  selectedClub.value = club
}

function setRecommendation(nextRecommendation: Recommendation) {
  recommendation.value = nextRecommendation
}

function setConditions(nextConditions: Conditions) {
  conditions.value = nextConditions
}

export const roundStore = {
  selectedRoundId: computed(() => selectedRoundId.value),
  selectedCourse: computed(() => selectedCourse.value),
  selectedHole: computed(() => selectedHole.value),
  selectedClub: computed(() => selectedClub.value),
  recommendation: computed(() => recommendation.value),
  conditions: computed(() => conditions.value),
  setRoundId,
  setCourse,
  setHole,
  setClub,
  setRecommendation,
  setConditions
}
