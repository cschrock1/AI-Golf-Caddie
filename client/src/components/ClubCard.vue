<template>
  <div class="rounded-[24px] border border-[#1e3b32] bg-[#0d2119] p-4">
    <div class="flex items-center justify-between gap-3">
      <div>
        <p class="text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]">Club</p>
        <h3 class="mt-1 text-xl font-bold text-white">{{ club.name }}</h3>
      </div>
      <div class="flex gap-2">
        <button
          type="button"
          class="rounded-full border border-[#2b4d43] bg-[#10271f] px-2.5 py-1.5 text-[10px] uppercase tracking-[0.14em] text-[#dfeee6]"
          @click="$emit('edit', club)"
        >
          Edit
        </button>
        <button
          type="button"
          class="rounded-full border border-[#5a2f33] bg-[#1c191b] px-2.5 py-1.5 text-[10px] uppercase tracking-[0.14em] text-[#f1b2b9]"
          @click="$emit('delete', club.id)"
        >
          Delete
        </button>
      </div>
    </div>

    <div class="mt-4 grid grid-cols-2 gap-3">
      <div class="rounded-2xl border border-[#1e3b32] bg-[#10271f] p-3">
        <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Carry</p>
        <p class="mt-2 text-xl font-black text-white">{{ club.carry_distance ?? '—' }}</p>
      </div>
      <div class="rounded-2xl border border-[#1e3b32] bg-[#10271f] p-3">
        <p class="text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">Total</p>
        <p class="mt-2 text-xl font-black text-white">{{ club.total_distance ?? '—' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Club } from '../types'

defineProps<{
  club: Club
}>()

defineEmits<{
  edit: [club: Club]
  delete: [id: number]
}>()
</script>
