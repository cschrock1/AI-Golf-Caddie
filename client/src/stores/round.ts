import { computed, ref } from 'vue'
import type { Club, Conditions, Course, Recommendation } from '../types'

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
    // Only rounds explicitly marked active by the current app flow should
    // restore GPS and scorecard tabs. Ignore orphaned IDs from older versions.
    if (localStorage.getItem('aigc_round_in_progress') !== 'true') {
      localStorage.removeItem('aigc_active_round_id')
      return null
    }
    const raw = localStorage.getItem('aigc_active_round_id')
    return raw ? Number(raw) : null
  } catch {
    return null
  }
}
const selectedRoundId = ref<number | null>(storedRoundId())
const activeRoundValidated = ref(false)
const selectedHole = ref<number>(1)
const selectedClub = ref<Club | null>(null)
const recommendation = ref<Recommendation | null>(null)
const conditions = ref<Conditions>({})

function setCourse(course: Course | null) {
  selectedCourse.value = course
  if (typeof window !== 'undefined') {
    if (course) localStorage.setItem('aigc_selected_course', JSON.stringify(course))
    else localStorage.removeItem('aigc_selected_course')
  }
}

function setRoundId(roundId: number | null) {
  selectedRoundId.value = roundId
  activeRoundValidated.value = true
  if (typeof window !== 'undefined') {
    if (roundId !== null) {
      localStorage.setItem('aigc_active_round_id', String(roundId))
      localStorage.setItem('aigc_round_in_progress', 'true')
    } else {
      localStorage.removeItem('aigc_active_round_id')
      localStorage.removeItem('aigc_round_in_progress')
    }
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

function clearRecommendation() {
  recommendation.value = null
}

function setConditions(nextConditions: Conditions) {
  conditions.value = nextConditions
}

export const roundStore = {
  selectedRoundId: computed(() => selectedRoundId.value),
  hasActiveRound: computed(() => activeRoundValidated.value && selectedRoundId.value !== null),
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
  clearRecommendation,
  setConditions
}
