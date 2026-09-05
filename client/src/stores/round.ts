import { computed, ref } from 'vue'
import type { Club, Conditions, Course, Recommendation } from '../types'
import { demoConditions, demoRecommendation } from '../mock/recommendation'

const selectedCourse = ref<Course | null>(null)
const selectedHole = ref<number>(7)
const selectedClub = ref<Club | null>(null)
const recommendation = ref<Recommendation>(demoRecommendation)
const conditions = ref<Conditions>(demoConditions)

function setCourse(course: Course | null) {
  selectedCourse.value = course
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
