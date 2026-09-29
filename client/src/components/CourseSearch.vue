<template>
  <section class="rounded-[28px] border border-white/10 bg-[#0d1d16] p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)] sm:p-6">
    <div>
      <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Round setup</p>
      <h2 class="mt-2 text-2xl font-black tracking-tight text-white">Choose a course</h2>
      <p class="mt-1 text-sm text-[#a6b6ad]">Select a course that is already in your course library.</p>
    </div>

    <label class="sr-only" for="course-search">Search saved courses</label>
    <div class="relative mt-4">
      <input
        id="course-search"
        v-model="query"
        type="search"
        autocomplete="off"
        placeholder="Course name, city, or state"
        class="w-full rounded-full border border-white/10 bg-[#07150f] px-4 py-3 pr-24 text-white placeholder:text-[#71867a] focus:border-[#c8ff00] focus:outline-none"
        @input="hasSearched = query.trim().length > 0"
      />
      <span class="absolute right-4 top-3.5 text-[10px] font-bold uppercase tracking-[0.12em] text-[#71867a]">{{ courses.length }} saved</span>
    </div>

    <p v-if="loading" class="mt-3 text-sm text-[#a6b6ad]" role="status">Loading saved courses…</p>
    <p v-else-if="errorMessage" class="mt-3 text-sm text-[#ffaaa9]" role="alert">{{ errorMessage }}</p>
    <p v-else-if="hasSearched && !results.length" class="mt-3 text-sm text-[#a6b6ad]" role="status">No saved course matches that search. Courses need to be imported before you can start a round.</p>

    <div v-if="results.length" class="mt-3 space-y-2" role="listbox" aria-label="Saved golf courses">
      <button
        v-for="result in results"
        :key="result.id"
        type="button"
        class="flex w-full items-center justify-between gap-3 rounded-2xl border border-white/10 bg-[#10271f] p-3 text-left transition hover:border-[#c8ff00]/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#c8ff00]"
        role="option"
        :aria-selected="selectedCourse?.id === result.id"
        @click="selectCourse(result)"
      >
        <span class="min-w-0">
          <span class="block truncate font-bold text-white">{{ result.name }}</span>
          <span class="mt-1 block truncate text-xs text-[#a6b6ad]">{{ [result.city, result.state].filter(Boolean).join(', ') || 'Location not listed' }} · {{ result.holes?.length ?? 0 }} mapped {{ result.holes?.length === 1 ? 'hole' : 'holes' }}</span>
        </span>
        <span class="shrink-0 rounded-full bg-[#c8ff00]/10 px-2 py-1 text-[9px] font-black uppercase tracking-[0.12em] text-[#c8ff00]">Select</span>
      </button>
    </div>

    <div v-if="selectedCourse" class="mt-4 flex items-center justify-between gap-3 rounded-2xl border border-[#c8ff00]/20 bg-[#c8ff00]/5 p-3">
      <div>
        <p class="text-[9px] uppercase tracking-[0.18em] text-[#91a69a]">Selected course</p>
        <p class="mt-1 font-bold text-white">{{ selectedCourse.name }}</p>
      </div>
      <button type="button" :disabled="!selectedCourse.holes?.length" class="rounded-full bg-[#c8ff00] px-4 py-2 text-[10px] font-black uppercase tracking-[0.12em] text-[#07140f] disabled:cursor-not-allowed disabled:opacity-40" @click="startRound">Start round</button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getCourseHoles, getCourses } from '../services/api'
import type { Course } from '../types'

const emit = defineEmits<{ select: [course: Course]; start: [course: Course] }>()
const query = ref('')
const courses = ref<Course[]>([])
const selectedCourse = ref<Course | null>(null)
const loading = ref(false)
const errorMessage = ref('')
const hasSearched = ref(false)

const results = computed(() => {
  const term = query.value.trim().toLocaleLowerCase()
  if (!term) return []
  return courses.value.filter((course) =>
    [course.name, course.city, course.state].some((value) => value?.toLocaleLowerCase().includes(term))
  )
})

function selectCourse(course: Course) {
  selectedCourse.value = course
  emit('select', course)
}

function startRound() {
  if (selectedCourse.value?.holes?.length) emit('start', selectedCourse.value)
}

onMounted(async () => {
  loading.value = true
  try {
    const response = await getCourses()
    courses.value = await Promise.all(response.data.map(async (course) => {
      try {
        const holesResponse = await getCourseHoles(course.id)
        return { ...course, holes: holesResponse.data }
      } catch {
        return { ...course, holes: [] }
      }
    }))
  } catch {
    errorMessage.value = 'Unable to load saved courses. Try again after reconnecting to the server.'
  } finally {
    loading.value = false
  }
})
</script>
