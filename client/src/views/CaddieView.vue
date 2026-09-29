<template>
  <div class="mx-auto max-w-4xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="courseName" :hole-label="`Hole ${holeNumber}`" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">Caddie preview</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-white">Course briefing</h1>
        </div>
        <div class="text-right text-[10px] uppercase tracking-[0.18em] text-[#8ca49a]">
          <p>{{ currentTime }}</p>
        </div>
      </div>

      <div class="mt-5 grid gap-3 sm:grid-cols-4">
          <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
            <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Course</p>
          <p class="mt-2 text-base font-bold text-white">{{ courseName ?? 'No active round' }}</p>
        </div>
          <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
            <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Hole</p>
          <p class="mt-2 text-base font-bold text-white">{{ holeNumber }}</p>
        </div>
          <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
            <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Distance</p>
          <p class="mt-2 text-base font-bold text-white">{{ dist != null ? dist + ' YDS' : 'Distance unavailable' }}</p>
        </div>
          <div class="rounded-2xl border border-white/10 bg-[#10271f] p-3">
            <p class="text-[10px] uppercase tracking-[0.16em] text-[#91a69a]">Wind</p>
          <p class="mt-2 text-base font-bold text-white">{{ conditions.windSpeed != null ? conditions.windSpeed + ' MPH' : 'Unavailable' }}</p>
        </div>
      </div>
    </section>

    <section class="mt-6 rounded-[30px] border border-white/10 bg-[#0d1d16] p-4 shadow-[0_18px_45px_rgba(0,0,0,0.18)] sm:p-5">
      <p class="mb-4 text-xs leading-5 text-[#91a69a]">This prototype uses a local sample response. It is not connected to an AI service yet.</p>
      <div class="space-y-4">
        <ChatMessage v-for="message in chatMessages" :key="message.id" :message="message" />

        <div v-if="isLoading" class="flex justify-start">
          <div class="max-w-[85%] rounded-[22px] border border-[#1d3a2d] bg-[#10271f] px-3 py-2.5 text-sm text-[#dfeee6]">
            Building an explanation from the current hole and your club distances…
          </div>
        </div>

        <div v-if="chatMessages.length === 0" class="rounded-[24px] border border-dashed border-[#214335] bg-[#10271f] p-5 text-center text-sm text-[#a7b8b0]">
          Ask a strategic question about the hole, club selection, or risk profile.
        </div>
      </div>

      <form class="mt-5 flex gap-3" @submit.prevent="sendMessage">
        <label class="sr-only" for="chat-input">Ask the caddie preview</label>
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
import { getCaddieExplanation, getHole } from '../services/api'

const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const selectedCourse = roundStore.selectedCourse
const courseName = computed(() => selectedCourse.value?.name ?? null)
const holeNumber = computed(() => roundStore.selectedHole.value ?? 1)
const conditions = roundStore.conditions

// derive a best-effort distance: use recommendation or conditions or placeholder
const dist = computed(() => {
  const rec = roundStore.recommendation.value
  if (rec?.target_yards) return rec.target_yards
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
    timestamp: currentTime,
    provider: 'Course briefing'
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

  try {
    const course = selectedCourse.value
    const playerLocation = conditions.value.playerLocation
    if (!course?.id || !playerLocation) {
      throw new Error('Go to the mapped hole and use Locate before asking for a shot explanation.')
    }
    const holeResponse = await getHole(course.id, holeNumber.value)
    const response = await getCaddieExplanation(holeResponse.data.id, playerLocation, text)
    roundStore.setRecommendation(response.data.recommendation)
    chatMessages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: response.data.explanation,
      timestamp: 'Now',
      provider: response.data.explanation_source === 'openai' ? 'AI Caddie' : 'Caddie fallback'
    })
  } catch (requestError: unknown) {
    const detail = (requestError as { response?: { data?: { detail?: string } }; message?: string })
    chatMessages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: detail.response?.data?.detail || detail.message || 'Unable to create a shot explanation right now.',
      timestamp: 'Now',
      provider: 'Caddie'
    })
  } finally {
    isLoading.value = false
  }
}
</script>
