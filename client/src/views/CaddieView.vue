<template>
  <div class="mx-auto flex h-[100dvh] max-w-4xl flex-col overflow-hidden px-4 pb-[calc(4.5rem+env(safe-area-inset-bottom))] pt-3 sm:px-6 sm:pt-4">
    <AppHeader class="shrink-0" :course-name="hasActiveRound ? courseName : null" :hole-label="hasActiveRound ? `Hole ${holeNumber}` : 'General golf Q&A'" />

    <section class="mt-3 shrink-0 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-4 sm:mt-4 sm:p-5">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-[10px] font-bold uppercase tracking-[0.24em] text-[#c8ff00]">AI Caddie</p>
          <h1 class="mt-2 text-3xl font-black tracking-tight text-white">{{ hasActiveRound ? 'Course briefing' : 'Golf Q&A' }}</h1>
        </div>
        <div class="text-right text-[10px] uppercase tracking-[0.18em] text-[#8ca49a]">
          <p>{{ currentTime }}</p>
        </div>
      </div>

      <div v-if="hasActiveRound" class="mt-3 grid gap-2 sm:mt-4 sm:grid-cols-4 sm:gap-3">
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

    <section class="mt-3 flex min-h-0 flex-1 flex-col rounded-[30px] border border-white/10 bg-[#0d1d16] p-4 shadow-[0_18px_45px_rgba(0,0,0,0.18)] sm:mt-4 sm:p-5">
      <p class="mb-3 shrink-0 text-xs leading-5 text-[#91a69a] sm:mb-4">
        {{ hasActiveRound
          ? 'Ask about club choice, target, or risk for this hole. Your conversation stays here until you move to another hole.'
          : 'Ask general questions about golf, rules, strategy, or equipment.' }}
      </p>
      <div ref="chatScrollContainer" class="min-h-0 flex-1 space-y-4 overflow-y-auto overscroll-contain pr-1">
        <ChatMessage v-for="message in chatMessages" :key="message.id" :message="message" />

        <div v-if="isLoading" class="flex justify-start">
          <div class="max-w-[85%] rounded-[22px] border border-[#1d3a2d] bg-[#10271f] px-3 py-2.5 text-sm text-[#dfeee6]">
            {{ isTakingLong
              ? 'Still waiting for the AI service. This can take up to 30 seconds…'
              : hasActiveRound
                ? 'Building advice from this hole and your club distances…'
                : 'Thinking through your golf question…' }}
          </div>
        </div>

        <div v-if="chatMessages.length === 0" class="rounded-[24px] border border-dashed border-[#214335] bg-[#10271f] p-5 text-center text-sm text-[#a7b8b0]">
          {{ hasActiveRound
            ? 'Ask a strategic question about this hole, club selection, or risk profile.'
            : 'Ask any general question about golf to get started.' }}
        </div>
      </div>

      <form class="mt-3 flex shrink-0 gap-3 sm:mt-4" @submit.prevent="sendMessage">
        <label class="sr-only" for="chat-input">Ask the AI caddie</label>
        <input
          id="chat-input"
          v-model="newMessage"
          type="text"
          maxlength="500"
          :placeholder="hasActiveRound ? 'What club should I use from here?' : 'How does match play scoring work?'"
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
import { computed, nextTick, ref, watch } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import ChatMessage from '../components/ChatMessage.vue'
import { authStore } from '../stores/auth'
import { roundStore } from '../stores/round'
import { getCaddieExplanation, getGeneralCaddieAnswer, getHole } from '../services/api'

const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const selectedCourse = roundStore.selectedCourse
const courseName = computed(() => selectedCourse.value?.name ?? null)
const holeNumber = computed(() => roundStore.selectedHole.value ?? 1)
const conditions = roundStore.conditions
const hasActiveRound = roundStore.hasActiveRound
const selectedRoundId = roundStore.selectedRoundId
const chatMessages = roundStore.caddieChatMessages

// derive a best-effort distance: use recommendation or conditions or placeholder
const dist = computed(() => {
  const rec = roundStore.recommendation.value
  if (rec?.target_yards) return rec.target_yards
  if (conditions.value?.holeDistance) return conditions.value.holeDistance
  return null
})

const newMessage = ref('')
const isLoading = ref(false)
const isTakingLong = ref(false)
const chatScrollContainer = ref<HTMLElement | null>(null)

const canSend = computed(() => newMessage.value.trim().length > 0 && !isLoading.value)

watch(
  [() => authStore.user.value?.id, hasActiveRound, selectedRoundId, holeNumber],
  ([userId, activeRound, roundId, hole]) => {
    if (userId) roundStore.setCaddieChatContext(userId, activeRound ? roundId : null, hole)
  },
  { immediate: true }
)

watch(
  [chatMessages, isLoading],
  async () => {
    await nextTick()
    const container = chatScrollContainer.value
    if (container) container.scrollTop = container.scrollHeight
  },
  { deep: true, flush: 'post', immediate: true }
)

async function sendMessage() {
  if (!canSend.value) return

  const text = newMessage.value.trim()
  const activeRound = hasActiveRound.value
  const roundId = selectedRoundId.value
  const requestedHole = holeNumber.value
  roundStore.addCaddieChatMessage({ id: `user-${Date.now()}`, role: 'user', content: text, timestamp: 'Now' })
  newMessage.value = ''
  isLoading.value = true
  isTakingLong.value = false
  const slowResponseTimer = setTimeout(() => {
    isTakingLong.value = true
  }, 8_000)

  try {
    const conversation = chatMessages.value.slice(0, -1).slice(-20).map(({ role, content }) => ({ role, content }))
    if (!activeRound) {
      const response = await getGeneralCaddieAnswer(text, conversation)
      if (!hasActiveRound.value) {
        roundStore.addCaddieChatMessage({
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: response.data.answer,
          timestamp: 'Now',
          provider: response.data.answer_source === 'rules' ? 'Caddie' : 'AI Caddie'
        })
      }
      return
    }

    const course = selectedCourse.value
    if (!course?.id) throw new Error('Select a course before asking about this round.')
    const holeResponse = await getHole(course.id, requestedHole)
    const playerLocation = conditions.value.playerLocation ?? holeResponse.data.tee_location?.coordinates
    if (!playerLocation) throw new Error('This hole has no mapped tee location. Set your location on the hole map before asking for shot advice.')
    const response = await getCaddieExplanation(holeResponse.data.id, playerLocation, text, conversation)
    const isSameHole = hasActiveRound.value && selectedRoundId.value === roundId && holeNumber.value === requestedHole
    if (!isSameHole) return
    roundStore.setRecommendation(response.data.recommendation)
    roundStore.addCaddieChatMessage({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: response.data.explanation,
      timestamp: 'Now',
      provider: response.data.explanation_source === 'rules' ? 'Caddie fallback' : 'AI Caddie'
    })
  } catch (requestError: unknown) {
    const isSameContext = activeRound
      ? hasActiveRound.value && selectedRoundId.value === roundId && holeNumber.value === requestedHole
      : !hasActiveRound.value
    if (isSameContext) {
      const detail = requestError as { response?: { data?: { detail?: string } }; message?: string }
      const message = ['ECONNABORTED', 'ETIMEDOUT'].includes((requestError as { code?: string }).code ?? '')
        ? 'The AI service took too long to respond. Please try again.'
        : detail.response?.data?.detail || detail.message || 'Unable to answer right now.'
      roundStore.addCaddieChatMessage({
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: message,
        timestamp: 'Now',
        provider: 'Caddie'
      })
    }
  } finally {
    clearTimeout(slowResponseTimer)
    isLoading.value = false
    isTakingLong.value = false
  }
}
</script>
