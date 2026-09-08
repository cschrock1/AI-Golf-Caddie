<template>
  <section class="rounded-[28px] border border-[#1d3a2d] bg-[#10271f] p-4 sm:p-5">
    <div class="mb-3 flex items-center justify-between">
      <div>
        <p class="text-[10px] uppercase tracking-[0.24em] text-[#8ca49a]">GPS hole view</p>
        <p class="mt-1 text-sm font-bold text-white">Live course position</p>
      </div>
      <button
        type="button"
        class="rounded-full border border-[#315441] px-3 py-2 text-[10px] font-bold uppercase tracking-[0.12em] text-[#dfeee6] transition hover:border-[#c8ff00] focus-visible:outline-none"
        :disabled="isLocating"
        @click="locatePlayer"
      >
        {{ isLocating ? 'Locating' : 'Locate me' }}
      </button>
    </div>

    <div ref="mapElement" class="h-80 overflow-hidden rounded-[24px] border border-[#214335] bg-[#d9e1d8]" role="img" aria-label="Interactive Mapbox GPS map showing the current golf hole"></div>
    <p v-if="mapError" class="mt-3 text-xs leading-5 text-[#f7dfe2]" role="alert">{{ mapError }}</p>
    <p v-if="locationError" class="mt-3 text-xs leading-5 text-[#f7dfe2]" role="alert">{{ locationError }}</p>
    <div v-if="playerDistance !== null" class="mt-3 flex items-center justify-between rounded-2xl border border-[#c8ff00]/30 bg-[#142d20] px-3 py-3">
      <span class="text-[10px] uppercase tracking-[0.18em] text-[#b8d8c8]">You to pin</span>
      <strong class="text-xl font-black text-[#c8ff00]">{{ playerDistance }} <span class="text-[10px] tracking-[0.14em] text-[#b8d8c8]">YDS</span></strong>
    </div>
    <div class="mt-3 flex items-center justify-between text-[10px] uppercase tracking-[0.16em] text-[#8ca49a]">
      <span><i class="legend-dot bg-[#173f31]"></i> tee</span>
      <span><i class="legend-dot bg-[#c8ff00]"></i> pin</span>
      <span><i class="legend-dot bg-[#2f80ed]"></i> you</span>
    </div>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import mapboxgl, { type Map, type Marker } from 'mapbox-gl'
import { Geolocation } from '@capacitor/geolocation'
import 'mapbox-gl/dist/mapbox-gl.css'
import type { GeoJsonMultiPolygon, GeoJsonPoint, GeoJsonPolygon, Hole } from '../types'

const props = defineProps<{ hole: Hole | null }>()
const mapElement = ref<HTMLElement | null>(null)
const isLocating = ref(false)
const locationError = ref('')
const mapError = ref('')
const playerDistance = ref<number | null>(null)
const mapToken = import.meta.env.VITE_MAPBOX_TOKEN as string | undefined
let map: Map | null = null
let teeMarker: Marker | null = null
let pinMarker: Marker | null = null
let playerMarker: Marker | null = null
let locationWatchId: string | null = null

function pointCoordinates(point: GeoJsonPoint | null | undefined): [number, number] | null {
  return point ? point.coordinates : null
}

function markerElement(kind: 'tee' | 'pin' | 'player', label: string) {
  const element = document.createElement('div')
  element.className = `course-marker course-marker-${kind}`
  element.textContent = label
  return element
}

function geometryFeature(geometry: GeoJsonPolygon | GeoJsonMultiPolygon | null | undefined, kind: string) {
  return geometry ? { type: 'Feature', properties: { kind }, geometry } : null
}

function holeFeatureCollection() {
  const hole = props.hole
  return {
    type: 'FeatureCollection',
    features: [
      geometryFeature(hole?.fairway_geometry, 'fairway'),
      geometryFeature(hole?.green_geometry, 'green'),
      geometryFeature(hole?.bunker_geometry, 'bunker'),
      geometryFeature(hole?.water_geometry, 'water')
    ].filter(Boolean)
  }
}

function updateMarkers() {
  if (!map || !props.hole) return
  teeMarker?.remove()
  pinMarker?.remove()
  const tee = pointCoordinates(props.hole.tee_location)
  const pin = pointCoordinates(props.hole.pin_location)
  if (tee) teeMarker = new mapboxgl.Marker({ element: markerElement('tee', 'TEE'), anchor: 'bottom' }).setLngLat(tee).setPopup(new mapboxgl.Popup().setText('Tee')).addTo(map)
  if (pin) pinMarker = new mapboxgl.Marker({ element: markerElement('pin', 'PIN'), anchor: 'bottom' }).setLngLat(pin).setPopup(new mapboxgl.Popup().setText('Pin')).addTo(map)

  const points = [tee, pin].filter((point): point is [number, number] => point !== null)
  if (points.length === 2) {
    const bounds = points.reduce((result, point) => result.extend(point), new mapboxgl.LngLatBounds(points[0], points[0]))
    map.fitBounds(bounds, { padding: 44, maxZoom: 17 })
  } else if (points.length === 1) {
    map.setCenter(points[0])
  }
}

function updateCourseLayers() {
  if (!map || !map.isStyleLoaded()) return
  const source = map.getSource('hole-features') as mapboxgl.GeoJSONSource | undefined
  source?.setData(holeFeatureCollection() as GeoJSON.FeatureCollection)
  updateMarkers()
}

function updatePlayerPosition(longitude: number, latitude: number) {
  if (!map) return
  const position: [number, number] = [longitude, latitude]
  if (!playerMarker) {
    playerMarker = new mapboxgl.Marker({ element: markerElement('player', 'YOU'), anchor: 'bottom' }).setLngLat(position).setPopup(new mapboxgl.Popup().setText('You')).addTo(map)
  } else {
    playerMarker.setLngLat(position)
  }
  updateDistanceLine(position)
}

function distanceInYards(from: [number, number], to: [number, number]) {
  const earthRadiusMeters = 6371000
  const latitudeDelta = (to[1] - from[1]) * Math.PI / 180
  const longitudeDelta = (to[0] - from[0]) * Math.PI / 180
  const latitude = from[1] * Math.PI / 180
  const targetLatitude = to[1] * Math.PI / 180
  const a = Math.sin(latitudeDelta / 2) ** 2 + Math.cos(latitude) * Math.cos(targetLatitude) * Math.sin(longitudeDelta / 2) ** 2
  return Math.round((earthRadiusMeters * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))) * 1.09361)
}

function updateDistanceLine(player: [number, number]) {
  if (!map || !props.hole?.pin_location) return
  const pin = props.hole.pin_location.coordinates
  playerDistance.value = distanceInYards(player, pin)
  const source = map.getSource('player-pin-line') as mapboxgl.GeoJSONSource | undefined
  source?.setData({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: [player, pin] } } as GeoJSON.Feature)
}

function startLocationWatch() {
  if (locationWatchId !== null) return
  Geolocation.watchPosition({ enableHighAccuracy: true, timeout: 10000, maximumAge: 3000 }, (position, error) => {
    if (error || !position) return
    updatePlayerPosition(position.coords.longitude, position.coords.latitude)
  }).then((watchId) => { locationWatchId = watchId }).catch(() => undefined)
}

async function locatePlayer() {
  isLocating.value = true
  locationError.value = ''
  try {
    const permission = await Geolocation.requestPermissions()
    if (permission.location === 'denied') throw new Error('Location permission was denied.')
    const position = await Geolocation.getCurrentPosition({ enableHighAccuracy: true })
    updatePlayerPosition(position.coords.longitude, position.coords.latitude)
    startLocationWatch()
    map?.flyTo({ center: [position.coords.longitude, position.coords.latitude], zoom: 17 })
  } catch {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          updatePlayerPosition(position.coords.longitude, position.coords.latitude)
          if (navigator.geolocation) {
            navigator.geolocation.watchPosition((nextPosition) => updatePlayerPosition(nextPosition.coords.longitude, nextPosition.coords.latitude))
          }
        },
        () => { locationError.value = 'Location is unavailable. Check device permissions and try again.' },
        { enableHighAccuracy: true }
      )
    } else {
      locationError.value = 'Location is unavailable on this device.'
    }
  } finally {
    isLocating.value = false
  }
}

onMounted(async () => {
  await nextTick()
  if (!mapElement.value) return
  if (!mapToken) {
    mapError.value = 'Mapbox is not configured. Add VITE_MAPBOX_TOKEN to client/.env.'
    return
  }

  mapboxgl.accessToken = mapToken
  map = new mapboxgl.Map({
    container: mapElement.value,
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-85.856, 41.574],
    zoom: 16,
    attributionControl: true
  })
  map.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'bottom-right')
  map.on('load', () => {
    map?.addSource('hole-features', { type: 'geojson', data: holeFeatureCollection() as GeoJSON.FeatureCollection })
    map?.addSource('player-pin-line', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
    map?.addLayer({ id: 'player-pin-line', type: 'line', source: 'player-pin-line', paint: { 'line-color': '#c8ff00', 'line-width': 3, 'line-dasharray': [2, 2] } })
    map?.addLayer({ id: 'hole-fairway', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'fairway'], paint: { 'fill-color': '#44775a', 'fill-opacity': 0.4 } })
    map?.addLayer({ id: 'hole-green', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'green'], paint: { 'fill-color': '#73a875', 'fill-opacity': 0.65 } })
    map?.addLayer({ id: 'hole-bunker', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'bunker'], paint: { 'fill-color': '#d5b078', 'fill-opacity': 0.8 } })
    map?.addLayer({ id: 'hole-water', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'water'], paint: { 'fill-color': '#287bb5', 'fill-opacity': 0.55 } })
    updateCourseLayers()
  })
  map.on('error', () => { mapError.value = 'Mapbox could not load the map. Check the token and network connection.' })
})

watch(() => props.hole, updateCourseLayers)

onBeforeUnmount(() => {
  teeMarker?.remove()
  pinMarker?.remove()
  playerMarker?.remove()
  if (locationWatchId !== null) void Geolocation.clearWatch({ id: locationWatchId })
  map?.remove()
})
</script>

<style scoped>
.course-marker {
  padding: 5px 7px;
  border: 2px solid #ffffff;
  border-radius: 999px;
  color: #ffffff;
  font-size: 9px;
  font-weight: 900;
  letter-spacing: 0.12em;
  line-height: 1;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
}

.course-marker-tee {
  background: #173f31;
}

.course-marker-pin {
  border-color: #07140f;
  background: #c8ff00;
  color: #07140f;
}

.course-marker-player {
  background: #2f80ed;
}

.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 4px;
  border-radius: 999px;
}
</style>
