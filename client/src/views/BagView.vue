<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="'Smart Bag'" :hole-label="'Your clubs'" />

    <section class="mt-6 rounded-[30px] border border-[#1d3a2d] bg-[#0d2119] p-5">
      <div class="flex items-center justify-between gap-3">
        <div>
          <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Smart Bag</p>
          <h1 class="mt-2 text-3xl font-black text-white">Your clubs</h1>
        </div>
        <button type="button" class="rounded-full bg-[#c8ff00] px-4 py-2 text-[10px] font-black uppercase tracking-[0.18em] text-[#07140f]" @click="openForm()">
          + Add club
        </button>
      </div>

      <div v-if="loading" class="mt-5 rounded-[24px] border border-[#214335] bg-[#10271f] p-4 text-sm text-[#dfeee6]">
        Loading your golf bag...
      </div>

      <div v-else-if="error" class="mt-5 rounded-[24px] border border-[#5a2f33] bg-[#1c191b] p-4 text-sm text-[#f1b2b9]" role="alert">
        <p>{{ error }}</p>
        <button type="button" class="mt-3 rounded-full bg-[#c8ff00] px-3 py-2 text-[10px] font-black uppercase tracking-[0.16em] text-[#07140f]" @click="loadClubs">Retry</button>
      </div>

      <div v-else-if="clubs.length === 0" class="mt-5 rounded-[24px] border border-dashed border-[#214335] bg-[#10271f] p-5 text-center text-sm text-[#a7b8b0]">
        No clubs added yet.
      </div>

      <div v-else class="mt-5 space-y-4">
        <ClubCard v-for="club in clubs" :key="club.id" :club="club" @edit="openForm(club)" @delete="removeClub(club.id)" />
      </div>
    </section>

    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-[#010b08]/75 p-4">
      <div class="w-full max-w-md rounded-[28px] border border-[#1d3a2d] bg-[#0d2119] p-5">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-xl font-black text-white">{{ editingId ? 'Edit club' : 'Add club' }}</h2>
          <button type="button" class="text-sm text-[#dfeee6]" @click="closeForm">Close</button>
        </div>

        <form class="mt-5 space-y-4" @submit.prevent="submitClub">
          <div>
            <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="club-name">Club name</label>
            <input id="club-name" v-model="form.name" type="text" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="Driver" required />
          </div>

          <div class="grid gap-4 sm:grid-cols-2">
            <div>
              <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="carry-distance">Carry</label>
              <input id="carry-distance" v-model.number="form.carry_distance" type="number" min="0" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" />
            </div>
            <div>
              <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="total-distance">Total</label>
              <input id="total-distance" v-model.number="form.total_distance" type="number" min="0" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" />
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" class="rounded-full border border-[#214335] bg-[#0d2119] px-4 py-2.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#dfeee6]" @click="closeForm">
              Cancel
            </button>
            <button type="submit" class="rounded-full bg-[#c8ff00] px-4 py-2.5 text-[10px] font-black uppercase tracking-[0.18em] text-[#07140f]">
              Save
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import ClubCard from '../components/ClubCard.vue'
import { createClub, deleteClub, getClubs, updateClub } from '../services/api'
import type { Club } from '../types'
import { authStore } from '../stores/auth'

const clubs = ref<Club[]>([])
const loading = ref(false)
const error = ref('')
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ name: '', carry_distance: null as number | null, total_distance: null as number | null })

function resetForm() {
  form.value = { name: '', carry_distance: null, total_distance: null }
  editingId.value = null
}

function openForm(club?: Club) {
  if (club) {
    editingId.value = club.id
    form.value = {
      name: club.name,
      carry_distance: club.carry_distance ?? null,
      total_distance: club.total_distance ?? null
    }
  } else {
    resetForm()
  }
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  resetForm()
}

async function loadClubs() {
  const user = authStore.user.value
  if (!user) return

  loading.value = true
  error.value = ''

  try {
    const response = await getClubs(user.id)
    clubs.value = response.data
  } catch {
    error.value = 'Unable to load your golf bag. Try again.'
  } finally {
    loading.value = false
  }
}

async function submitClub() {
  const user = authStore.user.value
  if (!user || !form.value.name.trim()) return

  const payload = {
    name: form.value.name.trim(),
    carry_distance: form.value.carry_distance,
    total_distance: form.value.total_distance
  }

  try {
    if (editingId.value) {
      const response = await updateClub(editingId.value, user.id, payload)
      const idx = clubs.value.findIndex((item) => item.id === editingId.value)
      if (idx >= 0) clubs.value[idx] = response.data
    } else {
      const response = await createClub(user.id, payload)
      clubs.value.unshift(response.data)
    }
    closeForm()
  } catch {
    error.value = 'Unable to save your club right now.'
  }
}

async function removeClub(clubId: number) {
  const user = authStore.user.value
  if (!user) return

  try {
    await deleteClub(clubId, user.id)
    clubs.value = clubs.value.filter((item) => item.id !== clubId)
  } catch {
    error.value = 'Unable to remove this club.'
  }
}

watch(() => authStore.user.value?.id, (userId) => {
  if (userId) loadClubs()
}, { immediate: true })
</script>
