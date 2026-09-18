<template>
  <section class="rounded-[28px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Round</p>
        <p class="mt-1 text-lg font-black text-white">Pebble Beach</p>
      </div>
      <div class="flex items-center gap-2">
        <button v-if="!editing" @click="startEditing" class="rounded-full border border-[#274536] bg-[#0d2119] px-3 py-1 text-[12px] font-black uppercase tracking-[0.12em] text-[#c8ff00]">Edit Scores</button>
        <div v-else class="flex gap-2">
          <button @click="saveChanges" :disabled="saving" class="rounded-full border border-[#274536] bg-[#0d2119] px-3 py-1 text-[12px] font-black uppercase tracking-[0.12em] text-[#c8ff00]">Save Changes</button>
          <button @click="cancelEditing" :disabled="saving" class="rounded-full border border-[#274536] bg-transparent px-3 py-1 text-[12px] font-black uppercase tracking-[0.12em] text-[#c8ff00]">Cancel</button>
        </div>
      </div>
    </div>

    <div class="overflow-hidden rounded-2xl border border-[#214335]">
      <table class="w-full border-collapse text-left text-sm">
        <thead class="bg-[#0d2119] text-[#b8d8c8]">
          <tr>
            <th class="px-2 py-3 font-medium">Hole</th>
            <th class="px-2 py-3 font-medium">Par</th>
            <th class="px-2 py-3 font-medium">Score</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(h, idx) in holesLocal" :key="h.hole || h.hole_id || idx" class="border-t border-[#214335] bg-[#10271f] text-[#edf6f0]">
            <td class="px-2 py-3">{{ h.hole ?? h.hole_number ?? (idx + 1) }}</td>
            <td class="px-2 py-3">{{ h.par }}</td>
            <td class="px-2 py-3 font-semibold">
              <div v-if="editing" class="w-20">
                <input
                  v-model="h.strokesInput"
                  @keydown.enter.prevent="focusNext(idx)"
                  @blur="normalizeInput(h)"
                  type="number"
                  min="1"
                  class="w-full rounded-md border border-[#214335] bg-[#0d2119] px-2 py-1 text-white placeholder-[#8ca49a]"
                />
              </div>
              <div v-else :class="scoreClass(h)">{{ displayScore(h) }}</div>
            </td>
          </tr>
        </tbody>
        <tfoot class="bg-[#0d2119] text-[#b8d8c8]">
          <tr>
            <td class="px-2 py-3 font-medium">Totals</td>
            <td class="px-2 py-3 font-medium">{{ parTotal }}</td>
            <td class="px-2 py-3 font-medium">{{ totalStrokes }} <span class="text-[#8ca49a]">({{ relativeToPar }})</span></td>
          </tr>
          <tr>
            <td class="px-2 py-3 font-medium">Out (1-9)</td>
            <td class="px-2 py-3 font-medium">{{ parOut }}</td>
            <td class="px-2 py-3 font-medium">{{ outStrokes }}</td>
          </tr>
          <tr>
            <td class="px-2 py-3 font-medium">In (10-18)</td>
            <td class="px-2 py-3 font-medium">{{ parIn }}</td>
            <td class="px-2 py-3 font-medium">{{ inStrokes }}</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div v-if="message" :class="messageClass" class="mt-3 inline-block rounded px-3 py-1 text-sm">{{ message }}</div>
  </section>
</template>

<script setup lang="ts">
import { reactive, ref, watch, onMounted, computed } from 'vue'
import { getRoundScores, saveRoundScores } from '../services/api'

const props = withDefaults(
  defineProps<{
    holes?: Array<any>
    roundId?: number | null
    userId?: number | null
  }>(),
  {
    holes: () => [
      { hole: 1, par: 4, strokes: null }
    ],
    roundId: null,
    userId: null
  }
)

const editing = ref(false)
const saving = ref(false)
const message = ref('')
const messageClass = ref('text-[#8ca49a] bg-transparent')

// local copy with strokesInput for editing
const holesLocal = reactive((props.holes || []).map(h => ({ ...h, strokesInput: h.strokes ?? h.score ?? '' })))

function mergeScores(scores: Array<any>) {
  for (const s of scores) {
    const match = holesLocal.find(h => (h.hole && h.hole === (s.hole_number ?? s.hole_id)) || h.hole_id === s.hole_id)
    if (match) {
      match.strokesInput = String(s.strokes)
      match.strokes = s.strokes
    } else {
      // try adding entry if hole_id present
      holesLocal.push({ hole: s.hole_number ?? null, hole_id: s.hole_id, par: s.par ?? null, strokes: s.strokes, strokesInput: String(s.strokes) })
    }
  }
}

async function loadScores() {
  if (!props.roundId) return
  try {
    const resp = await getRoundScores(props.roundId)
    mergeScores(resp.data)
  } catch (err) {
    // ignore; leave UI with provided data
  }
}

onMounted(() => {
  loadScores()
})

watch(() => props.holes, (next) => {
  // reset local copy if holes prop changes
  holesLocal.splice(0, holesLocal.length, ...(next || []).map(h => ({ ...h, strokesInput: h.strokes ?? h.score ?? '' })))
})

function startEditing() {
  message.value = ''
  editing.value = true
}

function cancelEditing() {
  // restore from original prop values or saved strokes
  holesLocal.forEach((h, idx) => {
    const original = (props.holes || [])[idx]
    h.strokesInput = original ? (original.strokes ?? original.score ?? '') : ''
  })
  editing.value = false
}

function normalizeInput(h: any) {
  const v = Number(h.strokesInput)
  if (!Number.isFinite(v) || v <= 0) {
    // invalid - keep input but mark
    h._invalid = true
  } else {
    h._invalid = false
    h.strokes = Math.trunc(v)
    h.strokesInput = String(h.strokes)
  }
}

function focusNext(idx: number) {
  const next = document.querySelectorAll('input')[idx + 1] as HTMLElement | undefined
  if (next) next.focus()
}

function displayScore(h: any) {
  return h.strokes ?? h.score ?? h.strokesInput ?? '-' 
}

function scoreClass(h: any) {
  const strokes = h.strokes ?? (h.score ?? null)
  if (strokes == null || h.par == null) return 'text-white'
  const diff = strokes - h.par
  if (diff <= -1) return 'text-[#7be29a]'
  if (diff === 0) return 'text-white'
  if (diff === 1) return 'text-[#f7d36a]'
  return 'text-[#f19b66]'
}

function computeTotals() {
  let out = 0
  let inSt = 0
  let pOut = 0
  let pIn = 0
  let total = 0
  let parTotal = 0
  holesLocal.forEach((h: any, idx: number) => {
    const strokes = typeof h.strokes === 'number' ? h.strokes : (h.strokesInput ? Number(h.strokesInput) : null)
    const par = h.par ?? 0
    if (idx < 9) {
      if (strokes) out += strokes
      pOut += par
    } else {
      if (strokes) inSt += strokes
      pIn += par
    }
    if (strokes) total += strokes
    parTotal += par
  })
  return { out, inSt, total, pOut, pIn, parTotal }
}

const totals = computed(() => computeTotals())
const outStrokes = computed(() => totals.value.out)
const inStrokes = computed(() => totals.value.inSt)
const totalStrokes = computed(() => totals.value.total)
const parOut = computed(() => totals.value.pOut)
const parIn = computed(() => totals.value.pIn)
const parTotal = computed(() => totals.value.parTotal)

const relativeToPar = computed(() => {
  if (!parTotal.value) return ''
  const diff = totalStrokes.value - parTotal.value
  if (diff === 0) return 'E'
  return diff > 0 ? `+${diff}` : `${diff}`
})

async function saveChanges() {
  // validate
  const payload: Array<{ hole_id?: number; hole_number?: number; strokes: number }> = []
  for (const h of holesLocal) {
    const v = Number(h.strokesInput)
    if (!Number.isFinite(v) || v <= 0) {
      message.value = 'Please enter valid whole-number scores greater than 0.'
      messageClass.value = 'text-[#f19b66]'
      return
    }
    payload.push({ hole_id: h.hole_id, hole_number: h.hole ?? h.hole_number, strokes: Math.trunc(v) })
  }

  if (!props.roundId || !props.userId) {
    // operate locally only
    payload.forEach((p, idx) => {
      holesLocal[idx].strokes = p.strokes
      holesLocal[idx].strokesInput = String(p.strokes)
    })
    message.value = 'Scorecard saved locally.'
    messageClass.value = 'text-[#8ca49a]'
    editing.value = false
    return
  }

  saving.value = true
  message.value = ''
  try {
    await saveRoundScores(props.userId, props.roundId, payload.map(p => ({ hole_id: p.hole_id ?? p.hole_number, strokes: p.strokes })))
    // apply saved values
    payload.forEach((p, idx) => {
      holesLocal[idx].strokes = p.strokes
      holesLocal[idx].strokesInput = String(p.strokes)
    })
    message.value = 'Scorecard saved.'
    messageClass.value = 'text-[#8ca49a]'
    editing.value = false
  } catch (err: any) {
    message.value = err?.response?.data?.detail || 'Failed to save scores.'
    messageClass.value = 'text-[#f19b66]'
  } finally {
    saving.value = false
  }
}
</script>
