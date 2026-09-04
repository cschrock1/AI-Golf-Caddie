<template>
  <div class="max-w-2xl mx-auto mt-8">
    <h1 class="text-2xl font-bold mb-4">My Profile</h1>

    <div class="bg-white p-4 rounded shadow mb-6">
      <h2 class="font-semibold">Golfer Profile</h2>
      <p class="text-sm text-gray-600">Name: {{ user?.full_name || '—' }}</p>
      <p class="text-sm text-gray-600">Email: {{ user?.email || '—' }}</p>
      <p class="text-sm text-gray-600">Handicap: {{ profile?.handicap ?? '—' }}</p>
      <p class="text-sm text-gray-600">Preferred Tee: {{ profile?.preferred_tee || '—' }}</p>
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
    const clubs = ref<any[]>([])

    setAuthHeaderFromStorage()

    async function load() {
      if (!getToken()) return
      const me = await api.get('/auth/me')
      user.value = me.data
      // load profile
      const prof = await api.get(`/golfer/${user.value.id}`)
      profile.value = prof.data
      // load clubs
      const clubsRes = await api.get(`/clubs`, { params: { user_id: user.value.id } })
      clubs.value = clubsRes.data
    }

    onMounted(() => { load() })
    return { user, profile, clubs }
  }
})
</script>
