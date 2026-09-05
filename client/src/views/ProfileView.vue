<template>
  <div class="max-w-2xl mx-auto mt-8">
    <h1 class="text-2xl font-bold mb-4">My Profile</h1>

    <div class="bg-white p-4 rounded shadow mb-6">
      <h2 class="font-semibold">Golfer Profile</h2>
        <div v-if="!editing">
          <p class="text-sm text-gray-600">Name: {{ user?.full_name || '—' }}</p>
          <p class="text-sm text-gray-600">Email: {{ user?.email || '—' }}</p>
          <p class="text-sm text-gray-600">Handicap: {{ profile?.handicap ?? '—' }}</p>
          <p class="text-sm text-gray-600">Preferred Tee: {{ profile?.preferred_tee || '—' }}</p>
          <div class="mt-3">
            <button @click="startEdit" class="px-3 py-2 bg-blue-600 text-white rounded">Edit Profile</button>
          </div>
        </div>
        <div v-else>
          <form @submit.prevent="saveProfile" class="space-y-3">
            <input v-model="form.full_name" placeholder="Full name" class="w-full p-2 border rounded" />
            <input v-model.number="form.handicap" placeholder="Handicap" type="number" class="w-full p-2 border rounded" />
            <select v-model="form.preferred_tee" class="w-full p-2 border rounded">
              <option value="">Select tee</option>
              <option>Black</option>
              <option>Blue</option>
              <option>White</option>
              <option>Gold</option>
              <option>Red</option>
            </select>
            <div class="flex gap-2 justify-end">
              <button type="button" @click="cancelEdit" class="px-3 py-2 bg-gray-200 rounded">Cancel</button>
              <button class="px-3 py-2 bg-green-600 text-white rounded">Save</button>
            </div>
          </form>
        </div>
    </div>

    <div class="bg-white p-4 rounded shadow">
      <h2 class="font-semibold mb-2">My Golf Bag</h2>
      <div v-if="clubs.length === 0" class="text-gray-600">No clubs yet.</div>
      <ul>
        <li v-for="c in clubs" :key="c.id" class="flex justify-between py-2 border-b">
          <div>{{ c.name }}</div>
          <div class="text-gray-600">{{ c.total_distance ?? '—' }} yds</div>
        </li>
      </ul>
    </div>

    <div class="flex gap-2 mt-4">
      <router-link to="/dashboard" class="px-3 py-2 bg-gray-200 rounded">Dashboard</router-link>
      <router-link to="/clubs" class="px-3 py-2 bg-blue-600 text-white rounded">Manage Clubs</router-link>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue'
import api from '../services/api'
import { setAuthHeaderFromStorage, getToken } from '../services/auth'

export default defineComponent({
  setup() {
    const user = ref<any | null>(null)
    const profile = ref<any | null>(null)
    const editing = ref(false)
    const form = ref({ full_name: '', handicap: null as number | null, preferred_tee: '' })
    const clubs = ref<any[]>([])

    setAuthHeaderFromStorage()

    async function load() {
      if (!getToken()) return
      const me = await api.get('/auth/me')
      user.value = me.data
      // load profile
      const prof = await api.get(`/golfer/${user.value.id}`)
      profile.value = prof.data
      form.value.full_name = user.value.full_name || ''
      form.value.handicap = profile.value?.handicap ?? null
      form.value.preferred_tee = profile.value?.preferred_tee || ''
      // load clubs
      const clubsRes = await api.get(`/clubs`, { params: { user_id: user.value.id } })
      clubs.value = clubsRes.data
    }

    function startEdit() {
      editing.value = true
    }

    function cancelEdit() {
      editing.value = false
    }

    async function saveProfile() {
      // update user full_name
      await api.put(`/auth/me`, { full_name: form.value.full_name })
      // create or update golfer profile
      try {
        await api.put(`/golfer/${user.value.id}`, { user_id: user.value.id, handicap: form.value.handicap, preferred_tee: form.value.preferred_tee })
      } catch (e: any) {
        // if profile doesn't exist, create it
        if (e.response?.status === 404) {
          await api.post(`/golfer`, { user_id: user.value.id, handicap: form.value.handicap, preferred_tee: form.value.preferred_tee })
        } else {
          throw e
        }
      }
      editing.value = false
      await load()
    }

    onMounted(() => { load() })
    return { user, profile, clubs, editing, form, startEdit, cancelEdit, saveProfile }
  }
})
</script>
