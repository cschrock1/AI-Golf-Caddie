<template>
  <div class="mx-auto max-w-4xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="courseName" :hole-label="`Hole ${holeNumber}`" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">AI Caddie</p>
          <h1 class="mt-2 text-3xl font-black text-white">Course briefing</h1>
        </div>
        <div class="text-right text-[10px] uppercase tracking-[0.18em] text-[#8ca49a]">
          <p>{{ currentTime }}</p>
        </div>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-4">
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Course</p>
          <p class="mt-2 text-base font-bold text-white">{{ courseName ?? 'No active round' }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Hole</p>
          <p class="mt-2 text-base font-bold text-white">{{ holeNumber }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Distance</p>
          <p class="mt-2 text-base font-bold text-white">{{ dist != null ? dist + ' YDS' : 'Distance unavailable' }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Wind</p>
          <p class="mt-2 text-base font-bold text-white">{{ conditions.windSpeed != null ? conditions.windSpeed + ' MPH' : 'Wind unavailable' }}</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-4 sm:p-5">
      <div class="space-y-4">
        <ChatMessage v-for="message in chatMessages" :key="message.id" :message="message" />

        <div v-if="isLoading" class="flex justify-start">
          <div class="max-w-[85%] rounded-[22px] border border-[#1d3a2d] bg-[#10271f] px-3 py-2.5 text-sm text-[#dfeee6]">
            Thinking through the wind, green, and miss pattern...
          </div>
        </div>

        <div v-if="chatMessages.length === 0" class="rounded-[24px] border border-dashed border-[#214335] bg-[#10271f] p-5 text-center text-sm text-[#a7b8b0]">
          Ask a strategic question about the hole, club selection, or risk profile.
        </div>
      </div>

      <form class="mt-5 flex gap-3" @submit.prevent="sendMessage">
        <label class="sr-only" for="chat-input">Ask AI Caddie</label>
        <input
          id="chat-input"
          v-model="newMessage"
          type="text"
          placeholder="Should I attack the pin or play safe?"
          class="flex-1 rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-sm text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none"
        />
        <button type="submit" class="rounded-full bg-[#c8ff00] px-5 py-3 text-xs font-black uppercase tracking-[0.18em] text-[#07140f] disabled:opacity-60" :disabled="isLoading || !newMessage.trim()">
          Send
        </button>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import ChatMessage from '../components/ChatMessage.vue'
import { roundStore } from '../stores/round'

const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const courseName = computed(() => roundStore.selectedCourse?.value?.name ?? null)
const holeNumber = computed(() => roundStore.selectedHole.value ?? 1)
const conditions = roundStore.conditions

// debug: log active selection at component setup
try {
  console.log('CaddieView: startup selectedCourse', roundStore.selectedCourse?.value)
  console.log('CaddieView: startup selectedHole', roundStore.selectedHole.value)
  console.log('CaddieView: startup conditions', (roundStore.conditions as any).value)
  console.log('CaddieView: startup selectedRoundId', (roundStore as any).selectedRoundId?.value)
} catch {}

// derive a best-effort distance: use recommendation or conditions or placeholder
const dist = computed(() => {
  const rec = roundStore.recommendation.value
  if (rec && (rec as any).distance) return (rec as any).distance
  if (conditions.value && (conditions.value.distance || (conditions.value as any).holeDistance)) return conditions.value.distance ?? (conditions.value as any).holeDistance
  return null
})

function briefingText() {
  const parts: string[] = []
  if (courseName.value) parts.push(`Course: ${courseName.value}`)
  else parts.push('No active round')
  parts.push(`Hole: ${holeNumber.value}`)
  if (dist.value != null) parts.push(`Distance: ${dist.value} YDS`)
  if (conditions.value?.windSpeed != null) parts.push(`Wind: ${conditions.value.windSpeed} MPH`)
  return parts.join(' · ')
}

// chatMessages starts with a Course Briefing assistant message based on active round
const chatMessages = ref([
  {
    id: `system-${Date.now()}`,
    role: 'assistant',
    content: briefingText(),
    timestamp: currentTime
  }
])
const newMessage = ref('')
const isLoading = ref(false)

const canSend = computed(() => newMessage.value.trim().length > 0 && !isLoading.value)

// keep briefing message in sync when round/hole changes
watch([courseName, () => holeNumber.value, () => dist.value, () => conditions.value?.windSpeed], () => {
  // debug: log briefing change
  try { console.log('CaddieView: briefing change', { courseName: courseName.value, holeNumber: holeNumber.value, dist: dist.value, wind: conditions.value?.windSpeed }) } catch {}
  // update first assistant message (system briefing)
  if (chatMessages.value.length > 0 && chatMessages.value[0].role === 'assistant') {
    chatMessages.value[0].content = briefingText()
    chatMessages.value[0].timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } else {
    chatMessages.value.unshift({ id: `system-${Date.now()}`, role: 'assistant', content: briefingText(), timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) })
  }
})

async function sendMessage() {
  if (!canSend.value) return

  const text = newMessage.value.trim()
  chatMessages.value.push({ id: `user-${Date.now()}`, role: 'user', content: text, timestamp: 'Now' })
  newMessage.value = ''
  isLoading.value = true

  // build context payload from active round and golfer data
  const context = {
    courseName: courseName.value,
    courseId: roundStore.selectedCourse?.value?.id ?? null,
    holeNumber: holeNumber.value,
    par: roundStore.selectedCourse?.value?.holes?.find?.((h: any) => h.hole_number === holeNumber.value)?.par ?? null,
    distance: dist.value,
    wind: conditions.value?.windSpeed ?? null,
    golferProfile: null,
    clubs: null
  }

  // Create a safe, context-aware assistant reply (no invented courses)
  setTimeout(() => {
    let reply = ''
    if (context.courseName) reply += `You're playing Hole ${context.holeNumber} at ${context.courseName}. `
    if (context.distance != null) reply += `You have approximately ${context.distance} yards to the target. `
    if (context.wind != null) reply += `Wind is ${context.wind} mph. `
    reply += `Based on your question: "${text}", consider attacking the center of the green to reduce wind effects.`

    chatMessages.value.push({ id: `assistant-${Date.now()}`, role: 'assistant', content: reply.trim(), timestamp: 'Now' })
    isLoading.value = false
  }, 700)
}
</script>
