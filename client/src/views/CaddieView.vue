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
          <p class="mt-2 text-base font-bold text-white">{{ courseName }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Hole</p>
          <p class="mt-2 text-base font-bold text-white">{{ holeNumber }}</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Distance</p>
          <p class="mt-2 text-base font-bold text-white">{{ dist }} YDS</p>
        </div>
        <div class="rounded-2xl border border-[#214335] bg-[#10271f] p-3">
          <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Wind</p>
          <p class="mt-2 text-base font-bold text-white">{{ conditions.windSpeed }} MPH</p>
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
import { computed, ref } from 'vue'
import { demoMessages } from '../mock/recommendation'
import AppHeader from '../components/AppHeader.vue'
import ChatMessage from '../components/ChatMessage.vue'
import { roundStore } from '../stores/round'

const courseName = 'Pebble Beach'
const holeNumber = 7
const dist = 114
const currentTime = '10:42 AM'
const conditions = roundStore.conditions

const chatMessages = ref(demoMessages)
const newMessage = ref('')
const isLoading = ref(false)

const canSend = computed(() => newMessage.value.trim().length > 0 && !isLoading.value)

async function sendMessage() {
  if (!canSend.value) return

  const text = newMessage.value.trim()
  chatMessages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    content: text,
    timestamp: 'Now'
  })
  newMessage.value = ''
  isLoading.value = true

  setTimeout(() => {
    chatMessages.value.push({
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content:
        'Play for the fat of the green, 12 feet left of the flag. The green slopes left-to-right toward the bunker, so the center gives you a safer miss while still leaving a good birdie opportunity.',
      timestamp: 'Now'
    })
    isLoading.value = false
  }, 700)
}
</script>
