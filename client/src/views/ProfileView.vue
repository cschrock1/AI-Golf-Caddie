<template>
  <div class="mx-auto max-w-5xl px-4 pb-28 pt-6 sm:px-6">
    <AppHeader :course-name="'Your Profile'" :hole-label="'Golfer account'" />

    <main class="mt-6 space-y-6">
      <section class="overflow-hidden rounded-[30px] border border-[#1d3a2d] bg-[#0d2119]">
        <div class="h-24 bg-[linear-gradient(120deg,#173f2c,#2e6944_52%,#93aa63)]"></div>
        <div class="px-5 pb-5 sm:px-7">
          <div class="-mt-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
            <div class="flex items-end gap-4">
              <div class="flex h-20 w-20 shrink-0 items-center justify-center rounded-[24px] border-4 border-[#0d2119] bg-[#c8ff00] text-2xl font-black text-[#07140f]">{{ profileInitials }}</div>
              <div class="pb-1">
                <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Golfer profile</p>
                <h1 class="mt-1 text-2xl font-black text-white sm:text-3xl">{{ user?.full_name || 'Golfer' }}</h1>
                <p class="mt-1 text-sm text-[#a7b8b0]">{{ user?.email || 'Your golf account' }}</p>
              </div>
            </div>
            <button v-if="!editing" type="button" class="rounded-full border border-[#2b4d43] bg-[#10271f] px-4 py-2 text-[10px] font-black uppercase tracking-[0.16em] text-[#c8ff00]" @click="startEdit">Edit profile</button>
          </div>

          <div v-if="!editing" class="mt-6 grid grid-cols-3 divide-x divide-[#214335] rounded-2xl border border-[#214335] bg-[#10271f]">
            <div class="p-3 text-center"><p class="text-xl font-black text-white">{{ clubs.length }}</p><p class="mt-1 text-[9px] uppercase tracking-[0.14em] text-[#8ca49a]">Clubs</p></div>
            <div class="p-3 text-center"><p class="text-xl font-black text-white">{{ profile?.handicap ?? '—' }}</p><p class="mt-1 text-[9px] uppercase tracking-[0.14em] text-[#8ca49a]">Handicap</p></div>
            <div class="p-3 text-center"><p class="text-xl font-black text-white">{{ profile?.preferred_tee || '—' }}</p><p class="mt-1 text-[9px] uppercase tracking-[0.14em] text-[#8ca49a]">Tee</p></div>
          </div>

          <form v-else class="mt-6 space-y-4 rounded-2xl border border-[#214335] bg-[#10271f] p-4" @submit.prevent="saveProfile">
            <div>
              <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="profile-name">Full name</label>
              <input id="profile-name" v-model="form.full_name" type="text" class="w-full rounded-full border border-[#214335] bg-[#0d2119] px-4 py-3 text-white placeholder:text-[#7d9488] focus:border-[#c8ff00] focus:outline-none" placeholder="Your name" required />
            </div>
            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="profile-handicap">Handicap</label>
                <input id="profile-handicap" v-model.number="form.handicap" type="number" min="0" step="0.1" class="w-full rounded-full border border-[#214335] bg-[#0d2119] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" placeholder="12.5" />
              </div>
              <div>
                <label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="profile-tee">Preferred tee</label>
                <select id="profile-tee" v-model="form.preferred_tee" class="w-full rounded-full border border-[#214335] bg-[#0d2119] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none">
                  <option value="">Select tee</option><option>Black</option><option>Blue</option><option>White</option><option>Gold</option><option>Red</option>
                </select>
              </div>
            </div>
            <div class="flex justify-end gap-3">
              <button type="button" class="rounded-full border border-[#214335] px-4 py-2.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#dfeee6]" @click="cancelEdit">Cancel</button>
              <button type="submit" class="rounded-full bg-[#c8ff00] px-4 py-2.5 text-[10px] font-black uppercase tracking-[0.18em] text-[#07140f]">Save profile</button>
            </div>
          </form>
        </div>
      </section>

      <section class="rounded-[30px] border border-[#1d3a2d] bg-[#10271f] p-5 sm:p-6">
        <div class="flex items-end justify-between gap-3">
          <div><p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Your equipment</p><h2 class="mt-2 text-2xl font-black text-white">Bag & distances</h2></div>
          <button type="button" class="rounded-full bg-[#c8ff00] px-4 py-2 text-[10px] font-black uppercase tracking-[0.16em] text-[#07140f]" @click="openForm()">Add club</button>
        </div>
        <div v-if="loading" class="mt-5 rounded-2xl border border-[#214335] bg-[#0d2119] p-4 text-sm text-[#dfeee6]">Loading your clubs...</div>
        <div v-else-if="error" class="mt-5 rounded-2xl border border-[#5a2f33] bg-[#1c191b] p-4 text-sm text-[#f1b2b9]" role="alert"><p>{{ error }}</p><button type="button" class="mt-3 rounded-full bg-[#c8ff00] px-3 py-2 text-[10px] font-black uppercase tracking-[0.16em] text-[#07140f]" @click="loadProfile">Retry</button></div>
        <div v-else-if="clubs.length === 0" class="mt-5 rounded-2xl border border-dashed border-[#214335] bg-[#0d2119] p-5 text-center text-sm text-[#a7b8b0]">No clubs added yet.</div>
        <div v-else class="mt-5 grid gap-4 sm:grid-cols-2"><ClubCard v-for="club in clubs" :key="club.id" :club="club" @edit="openForm(club)" @delete="removeClub(club.id)" /></div>
      </section>
    </main>

    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-[#010b08]/75 p-4">
      <div class="w-full max-w-md rounded-[28px] border border-[#1d3a2d] bg-[#0d2119] p-5">
        <div class="flex items-center justify-between gap-3"><h2 class="text-xl font-black text-white">{{ editingId ? 'Edit club' : 'Add club' }}</h2><button type="button" class="text-sm text-[#dfeee6]" @click="closeForm">Close</button></div>
        <form class="mt-5 space-y-4" @submit.prevent="submitClub">
          <div><label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="club-name">Club name</label><input id="club-name" v-model="clubForm.name" type="text" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" placeholder="Driver" required /></div>
          <div class="grid gap-4 sm:grid-cols-2"><div><label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="carry-distance">Carry</label><input id="carry-distance" v-model.number="clubForm.carry_distance" type="number" min="0" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" /></div><div><label class="mb-2 block text-[10px] uppercase tracking-[0.2em] text-[#8ca49a]" for="total-distance">Total</label><input id="total-distance" v-model.number="clubForm.total_distance" type="number" min="0" class="w-full rounded-full border border-[#214335] bg-[#10271f] px-4 py-3 text-white focus:border-[#c8ff00] focus:outline-none" /></div></div>
          <div class="flex justify-end gap-3 pt-2"><button type="button" class="rounded-full border border-[#214335] px-4 py-2.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#dfeee6]" @click="closeForm">Cancel</button><button type="submit" class="rounded-full bg-[#c8ff00] px-4 py-2.5 text-[10px] font-black uppercase tracking-[0.18em] text-[#07140f]">Save</button></div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppHeader from '../components/AppHeader.vue'
import ClubCard from '../components/ClubCard.vue'
import { authStore } from '../stores/auth'
import { createClub, deleteClub, getClubs, getGolferProfile, updateClub } from '../services/api'
import api from '../services/api'
import type { Club, GolferProfile } from '../types'

const user = computed(() => authStore.user.value)
const profile = ref<GolferProfile | null>(null)
const clubs = ref<Club[]>([])
const editing = ref(false)
const loading = ref(false)
const error = ref('')
const showForm = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ full_name: '', handicap: null as number | null, preferred_tee: '' })
const clubForm = ref({ name: '', carry_distance: null as number | null, total_distance: null as number | null })

const profileInitials = computed(() => {
  const name = user.value?.full_name?.trim()
  if (!name) return 'G'
  return name.split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase()
})

function resetClubForm() {
  clubForm.value = { name: '', carry_distance: null, total_distance: null }
  editingId.value = null
}

async function loadProfile() {
  const currentUser = user.value
  if (!currentUser) return
  loading.value = true
  error.value = ''
  try {
    const [profileResponse, clubsResponse] = await Promise.all([getGolferProfile(currentUser.id), getClubs(currentUser.id)])
    profile.value = profileResponse.data
    clubs.value = clubsResponse.data
    form.value = { full_name: currentUser.full_name || '', handicap: profile.value.handicap ?? null, preferred_tee: profile.value.preferred_tee || '' }
  } catch {
    error.value = 'Unable to load your profile. Try again.'
  } finally {
    loading.value = false
  }
}

function startEdit() { editing.value = true }
function cancelEdit() {
  editing.value = false
  form.value.full_name = user.value?.full_name || ''
  form.value.handicap = profile.value?.handicap ?? null
  form.value.preferred_tee = profile.value?.preferred_tee || ''
}

async function saveProfile() {
  const currentUser = user.value
  if (!currentUser) return
  await api.put('/auth/me', { full_name: form.value.full_name.trim() })
  await api.put(`/golfer/${currentUser.id}`, { user_id: currentUser.id, handicap: form.value.handicap, preferred_tee: form.value.preferred_tee })
  await authStore.loadUser()
  await loadProfile()
  editing.value = false
}

function openForm(club?: Club) {
  if (club) {
    editingId.value = club.id
    clubForm.value = { name: club.name, carry_distance: club.carry_distance ?? null, total_distance: club.total_distance ?? null }
  } else resetClubForm()
  showForm.value = true
}
function closeForm() { showForm.value = false; resetClubForm() }

async function submitClub() {
  const currentUser = user.value
  if (!currentUser || !clubForm.value.name.trim()) return
  const payload = { name: clubForm.value.name.trim(), carry_distance: clubForm.value.carry_distance, total_distance: clubForm.value.total_distance }
  try {
    if (editingId.value) {
      const response = await updateClub(editingId.value, currentUser.id, payload)
      const index = clubs.value.findIndex((club) => club.id === editingId.value)
      if (index >= 0) clubs.value[index] = response.data
    } else {
      const response = await createClub(currentUser.id, payload)
      clubs.value.unshift(response.data)
    }
    closeForm()
  } catch { error.value = 'Unable to save this club right now.' }
}

async function removeClub(clubId: number) {
  const currentUser = user.value
  if (!currentUser) return
  try {
    await deleteClub(clubId, currentUser.id)
    clubs.value = clubs.value.filter((club) => club.id !== clubId)
  } catch { error.value = 'Unable to remove this club right now.' }
}

watch(() => user.value?.id, (userId) => { if (userId) loadProfile() }, { immediate: true })
</script>