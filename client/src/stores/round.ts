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
const selectedHole = ref<number>(7)
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
  selectedCourse: computed(() => selectedCourse.value),
  selectedHole: computed(() => selectedHole.value),
  selectedClub: computed(() => selectedClub.value),
  recommendation: computed(() => recommendation.value),
  conditions: computed(() => conditions.value),
  setCourse,
  setHole,
  setClub,
  setRecommendation,
  setConditions
}
