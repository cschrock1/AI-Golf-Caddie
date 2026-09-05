<template>
  <div :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']">
    <div
      :class="[
        'max-w-[85%] rounded-[22px] border px-3 py-2.5 text-sm leading-6',
        message.role === 'user'
          ? 'border-[#224236] bg-[#c8ff00] text-[#07140f]'
          : 'border-[#1d3a2d] bg-[#10271f] text-[#ecf5ef]'
      ]"
    >
      <div class="mb-1 flex items-center justify-between gap-4 text-[10px] uppercase tracking-[0.18em] opacity-70">
        <span>{{ message.role === 'user' ? 'You' : 'AI Caddie' }}</span>
        <span>{{ message.timestamp }}</span>
      </div>
      <p>{{ message.content }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage as ChatMessageType } from '../types'

defineProps<{
  message: ChatMessageType
}>()
</script>
