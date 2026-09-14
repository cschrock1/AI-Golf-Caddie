<template>
  <section class="rounded-[28px] border border-[#bfd4b0] bg-[#f7faf4] p-5 shadow-[0_18px_35px_rgba(24,60,42,0.08)]">
    <div>
      <p class="text-[10px] uppercase tracking-[0.24em] text-[#5d7159]">Round setup</p>
      <h2 class="mt-2 text-2xl font-black text-[#183c2a]">Where are you playing?</h2>
      <p class="mt-1 text-sm text-[#5d7159]">Search by course name or location.</p>
    </div>

    <label class="sr-only" for="course-search">Search golf courses</label>
    <div class="relative mt-4">
      <input
        id="course-search"
        v-model="query"
        type="search"
        autocomplete="off"
        placeholder="Search golf courses"
        class="w-full rounded-full border border-[#c5d5bd] bg-white px-4 py-3 pr-24 text-[#183c2a] placeholder:text-[#7a8d7a] focus:border-[#335e42] focus:outline-none"
        @keydown.enter.prevent="searchCourses"
      />
      <button type="button" class="absolute right-1.5 top-1.5 rounded-full bg-[#1f5d3a] px-3 py-2 text-[10px] font-black uppercase tracking-[0.12em] text-[#effae4] disabled:opacity-50" :disabled="isSearching || query.trim().length < 2" @click="searchCourses">
        {{ isSearching ? 'Searching' : 'Search' }}
      </button>
    </div>

    <p v-if="errorMessage" class="mt-3 text-sm text-[#a53d3d]" role="alert">{{ errorMessage }}</p>
    <p v-else-if="hasSearched && !results.length && !isSearching" class="mt-3 text-sm text-[#5d7159]" role="status">No golf courses found. Try a nearby city or state.</p>

    <div v-if="results.length" class="mt-3 space-y-2" role="listbox" aria-label="Golf course search results">
      <button
        v-for="result in results"
        :key="`${result.name}-${result.map_center?.join('-')}`"
        type="button"
        class="flex w-full items-center justify-between gap-3 rounded-2xl border border-[#d9e6d0] bg-white p-3 text-left transition hover:border-[#1f5d3a] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1f5d3a]"
        role="option"
        @click="selectCourse(result)"
      >
        <span class="min-w-0">
          <span class="block truncate font-bold text-[#183c2a]">{{ result.name }}</span>
          <span class="mt-1 block truncate text-xs text-[#5d7159]">{{ result.city }}<span v-if="result.state">, {{ result.state }}</span></span>
        </span>
        <span class="shrink-0 rounded-full bg-[#edf5ea] px-2 py-1 text-[9px] font-black uppercase tracking-[0.12em] text-[#1e5d3f]">Select</span>
      </button>
    </div>

    <div v-if="selectedCourse" class="mt-4 flex items-center justify-between gap-3 rounded-2xl border border-[#bfd4b0] bg-[#edf5ea] p-3">
      <div>
        <p class="text-[9px] uppercase tracking-[0.18em] text-[#5d7159]">Selected course</p>
        <p class="mt-1 font-bold text-[#183c2a]">{{ selectedCourse.name }}</p>
      </div>
      <span class="rounded-full bg-[#1f5d3a] px-2 py-1 text-[9px] font-black uppercase tracking-[0.12em] text-[#effae4]">Ready</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'
import type { Course } from '../types'

const emit = defineEmits<{
  select: [course: Course]
}>()

const query = ref('')
const results = ref<Course[]>([])
const selectedCourse = ref<Course | null>(null)
const isSearching = ref(false)
const hasSearched = ref(false)
const errorMessage = ref('')
const mapToken = import.meta.env.VITE_MAPBOX_TOKEN as string | undefined
let searchRequest = 0

async function searchCourses() {
  const searchTerm = query.value.trim()
  if (searchTerm.length < 2 || !mapToken) return

  const requestId = ++searchRequest
  isSearching.value = true
  hasSearched.value = true
  errorMessage.value = ''
  results.value = []

  try {
    const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(searchTerm)}.json?access_token=${mapToken}&types=poi&autocomplete=true&limit=10`)
    if (!response.ok) throw new Error('Course search failed')
    const data = await response.json() as { features?: Array<{
      id?: string
      text?: string
      place_name?: string
      center?: [number, number]
      properties?: { category?: string }
      context?: Array<{ id?: string; text?: string; short_code?: string }>
    }> }

    if (requestId !== searchRequest) return
    results.value = (data.features || [])
      .filter((feature) => {
        const searchableText = [feature.text, feature.place_name, feature.properties?.category].filter(Boolean).join(' ')
        return /\bgolf(?:\s+(course|club))?\b|\bgolf_course\b/i.test(searchableText) && Boolean(feature.center)
      })
      .map((feature) => {
        const city = feature.context?.find((item) => item.id?.startsWith('place') || item.id?.startsWith('locality'))?.text
        const region = feature.context?.find((item) => item.id?.startsWith('region'))
        return {
          id: 0,
          name: feature.text || feature.place_name || 'Golf course',
          city,
          state: region?.short_code?.split('-').pop()?.toUpperCase() || region?.text,
          map_center: feature.center
        }
      })
  } catch {
    if (requestId === searchRequest) errorMessage.value = 'Unable to search courses right now.'
  } finally {
    if (requestId === searchRequest) isSearching.value = false
  }
}

function selectCourse(course: Course) {
  selectedCourse.value = course
  emit('select', course)
  results.value = []
}

onBeforeUnmount(() => {
  searchRequest += 1
})
</script>
