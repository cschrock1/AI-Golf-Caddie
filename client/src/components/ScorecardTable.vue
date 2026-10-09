<template>
  <section class="rounded-[28px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Round</p>
        <p class="mt-1 text-lg font-black text-white">{{ courseName }}</p>
      </div>
      <span v-if="!readOnly" class="rounded-full border border-[#274536] bg-[#0d2119] px-3 py-1 text-[10px] font-bold uppercase tracking-[0.1em] text-[#c8ff00]">Auto-saves</span>
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
              <div v-if="!readOnly" class="w-20">
                <input
                  v-model="h.strokesInput"
                  @input="queueSave(h)"
                  @keydown.enter.prevent="focusNext(idx)"
                  @blur="saveHole(h)"
                  type="number"
                  min="1"
                  step="1"
                  :aria-label="`Score for hole ${h.hole ?? h.hole_number ?? idx + 1}`"
                  :aria-invalid="h._invalid ? 'true' : 'false'"
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
import { reactive, ref, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import { getRoundScores, saveRoundScores } from '../services/api'

const emit = defineEmits<{
  scoresSaved: []
  totalUpdated: [total: number | null]
}>()

const props = withDefaults(
  defineProps<{
    courseName?: string
    holes?: Array<any>
    roundId?: number | null
    userId?: number | null
    readOnly?: boolean
  }>(),
  {
    courseName: 'Stonehenge Golf Course',
    holes: () => [
      { hole: 1, par: 4, strokes: null }
    ],
    roundId: null,
    userId: null,
    readOnly: false
  }
)

const message = ref('')
const messageClass = ref('text-[#8ca49a] bg-transparent')
const saveTimers = new Map<string, ReturnType<typeof setTimeout>>()

// local copy with strokesInput for editing
const holesLocal = reactive((props.holes || []).map(h => ({ ...h, strokesInput: h.strokes ?? h.score ?? '' })))

function draftKey() {
  const rid = props.roundId ?? 'no-round'
  const uid = props.userId ?? 'no-user'
  return `scorecard_draft_${rid}_${uid}`
}

function saveDraft() {
  try {
    const unsaved = holesLocal
      .filter(h => String(h.strokesInput ?? '').trim() !== String(h.strokes ?? h.score ?? '').trim())
      .map(h => ({ hole: h.hole ?? h.hole_number ?? null, par: h.par ?? null, strokesInput: h.strokesInput ?? '' }))
    if (unsaved.length) localStorage.setItem(draftKey(), JSON.stringify(unsaved))
    else localStorage.removeItem(draftKey())
  } catch {
    // ignore
  }
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(draftKey())
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function restoreDraft() {
  const draft = loadDraft()
  if (!draft) return

  draft.forEach((d: any) => {
    const match = holesLocal.find(h => (h.hole && h.hole === d.hole) || h.hole_id === d.hole)
    if (match) match.strokesInput = d.strokesInput
  })
}

function mergeScores(scores: Array<any>) {
  for (const s of scores) {
    const match = holesLocal.find(h => h.hole === s.hole_number || h.hole_id === s.hole_id)
    if (match) {
      match.strokesInput = String(s.strokes)
      match.strokes = s.strokes
    } else {
      // try adding entry if hole_id present
      holesLocal.push({ hole: s.hole_number ?? null, hole_id: s.hole_id, par: s.par ?? null, strokes: s.strokes, strokesInput: String(s.strokes) })
    }
  }
}

function currentTotal() {
  const total = holesLocal.reduce((sum, hole) => {
    return sum + (typeof hole.strokes === 'number' ? hole.strokes : 0)
  }, 0)
  return total > 0 ? total : null
}

async function loadScores() {
  if (!props.roundId) {
    restoreDraft()
    return
  }

  try {
    const resp = await getRoundScores(props.roundId)
    mergeScores(resp.data)
  } catch (err) {
    // ignore; leave UI with provided data
  }
  restoreDraft()
  emit('totalUpdated', currentTotal())
}

onMounted(loadScores)

watch(() => [props.roundId, props.userId], loadScores)

watch(() => props.holes, (next) => {
  holesLocal.splice(0, holesLocal.length, ...(next || []).map(h => ({ ...h, strokesInput: h.strokes ?? h.score ?? '' })))
})

watch(holesLocal, () => {
  if (!props.readOnly) saveDraft()
}, { deep: true })

function holeKey(h: any) {
  return String(h.hole_id ?? h.hole ?? h.hole_number ?? 'unknown')
}

function queueSave(h: any) {
  if (props.readOnly) return
  const key = holeKey(h)
  const previousTimer = saveTimers.get(key)
  if (previousTimer) clearTimeout(previousTimer)
  saveTimers.set(key, setTimeout(() => { void saveHole(h) }, 650))
}

async function saveHole(h: any) {
  if (props.readOnly) return
  const key = holeKey(h)
  const timer = saveTimers.get(key)
  if (timer) clearTimeout(timer)
  saveTimers.delete(key)

  const input = String(h.strokesInput ?? '').trim()
  if (!input) return
  const strokes = Number(input)
  if (!Number.isInteger(strokes) || strokes <= 0) {
    h._invalid = true
    message.value = 'Enter a whole-number score greater than 0.'
    messageClass.value = 'text-[#f19b66]'
    return
  }
  h._invalid = false

  const holeNumber = h.hole ?? h.hole_number
  const payload = [{ hole_id: h.hole_id, hole_number: holeNumber, strokes }]
  message.value = `Saving Hole ${holeNumber}…`
  messageClass.value = 'text-[#8ca49a]'

  try {
    if (props.roundId && props.userId) {
      await saveRoundScores(props.userId, props.roundId, payload)
    }
    h.strokes = strokes
    h.strokesInput = String(strokes)
    saveDraft()
    message.value = `Hole ${holeNumber} saved.`
    messageClass.value = 'text-[#8ca49a]'
    emit('scoresSaved')
    emit('totalUpdated', currentTotal())
    if (props.roundId && props.userId) {
      try { window.dispatchEvent(new CustomEvent('scores:updated')) } catch {}
    }
  } catch (err: any) {
    message.value = err?.response
      ? `${err.response.status} ${err.response.data?.detail || err.response.statusText}`
      : err?.message || 'Failed to save this score.'
    messageClass.value = 'text-[#f19b66]'
  }
}

function focusNext(idx: number) {
  const next = document.querySelectorAll('input')[idx + 1] as HTMLElement | undefined
  if (next) next.focus()
}

function displayScore(h: any) {
  return (h.strokes ?? h.score ?? h.strokesInput) || '--'
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

onBeforeUnmount(() => {
  for (const timer of saveTimers.values()) clearTimeout(timer)
  saveTimers.clear()
  if (!props.readOnly) {
    for (const h of holesLocal) {
      if (String(h.strokesInput ?? '').trim() !== String(h.strokes ?? h.score ?? '').trim()) void saveHole(h)
    }
  }
})
</script>
