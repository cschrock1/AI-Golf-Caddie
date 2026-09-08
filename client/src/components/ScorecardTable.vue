<template>
  <section class="rounded-[28px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">Round</p>
        <p class="mt-1 text-lg font-black text-white">Pebble Beach</p>
      </div>
      <div class="rounded-full border border-[#274536] bg-[#0d2119] px-2 py-1 text-[10px] uppercase tracking-[0.16em] text-[#c8ff00]">Out 38</div>
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
          <tr v-for="hole in holes" :key="hole.hole" class="border-t border-[#214335] bg-[#10271f] text-[#edf6f0]">
            <td class="px-2 py-3">{{ hole.hole }}</td>
            <td class="px-2 py-3">{{ hole.par }}</td>
            <td class="px-2 py-3 font-semibold" :class="hole.score > hole.par ? 'text-[#f7d36a]' : 'text-white'">{{ hole.score }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    holes?: Array<{ hole: number; par: number; score: number }>
  }>(),
  {
    holes: () => [
      { hole: 1, par: 4, score: 4 },
      { hole: 2, par: 5, score: 5 },
      { hole: 3, par: 3, score: 4 },
      { hole: 4, par: 4, score: 5 },
      { hole: 5, par: 4, score: 4 },
      { hole: 6, par: 3, score: 3 },
      { hole: 7, par: 3, score: 4 }
    ]
  }
)
</script>
