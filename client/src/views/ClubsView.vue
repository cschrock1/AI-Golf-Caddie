<template>
  <div class="max-w-2xl mx-auto mt-8">
    <h1 class="text-2xl font-bold mb-4">My Golf Bag</h1>

    <div class="bg-white p-4 rounded shadow mb-4">
      <h2 class="font-semibold mb-2">Add Club</h2>
      <form @submit.prevent="addClub" class="flex gap-2">
        <input v-model="name" placeholder="Club name" class="p-2 border rounded flex-1" />
        <input v-model.number="distance" placeholder="Yards" type="number" class="p-2 border rounded w-28" />
        <button class="px-3 py-2 bg-blue-600 text-white rounded">Add</button>
      </form>
      <p v-if="error" class="text-red-600 mt-2">{{ error }}</p>
    </div>

    <div class="bg-white p-4 rounded shadow">
      <h2 class="font-semibold mb-2">Clubs</h2>
      <div v-if="clubs.length === 0" class="text-gray-600">No clubs yet.</div>
      <ul>
        <li v-for="c in clubs" :key="c.id" class="flex justify-between items-center py-2 border-b">
          <div>
            <div class="font-medium">{{ c.name }}</div>
            <div class="text-sm text-gray-600">{{ c.total_distance ?? '—' }} yds</div>
          </div>
          <div class="flex gap-2">
            <button @click="editClub(c)" class="px-2 py-1 bg-yellow-400 rounded">Edit</button>
            <button @click="removeClub(c.id)" class="px-2 py-1 bg-red-500 text-white rounded">Delete</button>
          </div>
        </li>
      </ul>
    </div>

    <div v-if="editing" class="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div class="bg-white p-4 rounded w-96">
        <h3 class="font-semibold mb-2">Edit Club</h3>
        <form @submit.prevent="updateClub">
          <input v-model="name" placeholder="Club name" class="w-full p-2 border rounded mb-2" />
          <input v-model.number="distance" placeholder="Yards" type="number" class="w-full p-2 border rounded mb-2" />
          <div class="flex justify-end gap-2">
            <button type="button" @click="cancelEdit" class="px-3 py-2 bg-gray-200 rounded">Cancel</button>
            <button class="px-3 py-2 bg-blue-600 text-white rounded">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import api from '../services/api'
import { getToken } from '../services/auth'

export default defineComponent({
  setup() {
    const clubs = ref<any[]>([])
    const name = ref('')
    const distance = ref<number | null>(null)
    const error = ref('')
    const editing = ref(false)
    const editId = ref<number | null>(null)
    const user = ref<any | null>(null)

    async function load() {
      if (!getToken()) return
      const me = await api.get('/auth/me')
      user.value = me.data
      const res = await api.get('/clubs', { params: { user_id: user.value.id } })
      clubs.value = res.data
    }

    async function addClub() {
      error.value = ''
      if (!name.value) {
        error.value = 'Club name required'
        return
      }
      try {
        const payload = { name: name.value, total_distance: distance.value }
        const res = await api.post('/clubs', payload, { params: { user_id: user.value.id } })
        clubs.value.unshift(res.data)
        name.value = ''
        distance.value = null
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Unable to add club'
      }
    }

    function editClub(c: any) {
      editing.value = true
      editId.value = c.id
      name.value = c.name
      distance.value = c.total_distance
    }

    function cancelEdit() {
      editing.value = false
      editId.value = null
      name.value = ''
      distance.value = null
    }

    async function updateClub() {
      if (!editId.value) return
      try {
        const payload = { name: name.value, total_distance: distance.value }
        const res = await api.put(`/clubs/${editId.value}`, payload, { params: { user_id: user.value.id } })
        const idx = clubs.value.findIndex((x: any) => x.id === editId.value)
        if (idx !== -1) clubs.value[idx] = res.data
        cancelEdit()
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Unable to update club'
      }
    }

    async function removeClub(id: number) {
      try {
        await api.delete(`/clubs/${id}`, { params: { user_id: user.value.id } })
        clubs.value = clubs.value.filter((c: any) => c.id !== id)
      } catch (e: any) {
        error.value = e.response?.data?.detail || 'Unable to delete club'
      }
    }

    onMounted(() => { load() })

    return { clubs, name, distance, addClub, error, editing, editId, editClub, cancelEdit, updateClub, removeClub }
  }
})
</script>

<style scoped></style>
