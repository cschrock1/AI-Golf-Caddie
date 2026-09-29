<template>
  <section class="relative overflow-hidden border border-[#214335] bg-[#d9e1d8] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]" :class="fullScreen ? 'rounded-none border-x-0 border-t-0' : 'rounded-[30px]'">
    <div ref="mapElement" class="h-[620px] w-full" :class="fullScreen ? 'h-[clamp(320px,calc(100svh-155px),720px)]' : ''" role="img" aria-label="Interactive Mapbox GPS map showing the current golf hole"></div>

    <div class="absolute right-3 z-10 flex gap-2" :class="fullScreen ? 'top-16' : 'top-3'">
      <button
        type="button"
        class="rounded-full border border-white/40 bg-black/25 px-3 py-2 text-[10px] font-bold uppercase tracking-[0.14em] text-white backdrop-blur-sm transition hover:bg-black/35"
        :disabled="isLocating"
        @click="locatePlayer"
      >
        {{ isLocating ? 'Locating' : 'Locate' }}
      </button>
    </div>

    <div v-if="playerDistance !== null" class="absolute bottom-4 left-1/2 z-10 -translate-x-1/2 rounded-full border border-white/30 bg-black/55 px-4 py-2 text-white shadow-lg backdrop-blur-sm" :class="fullScreen ? 'bottom-24' : ''">
      <span class="text-[10px] uppercase tracking-[0.18em] text-white/75">You to pin</span>
      <div class="mt-1 text-center text-xl font-black text-[#c8ff00]">{{ playerDistance }} <span class="text-[10px] tracking-[0.14em] text-white/75">YDS</span></div>
    </div>

    <p v-if="mapError" class="absolute inset-x-3 top-14 z-10 rounded-xl bg-black/55 p-2 text-[10px] leading-5 text-[#f7dfe2]" role="alert">{{ mapError }}</p>
    <p v-if="locationError" class="absolute inset-x-3 top-14 z-10 rounded-xl bg-black/55 p-2 text-[10px] leading-5 text-[#f7dfe2]" role="alert">{{ locationError }}</p>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { roundStore } from '../stores/round'
import mapboxgl, { type Map, type Marker } from 'mapbox-gl'
import { Geolocation } from '@capacitor/geolocation'
import 'mapbox-gl/dist/mapbox-gl.css'
import type { Course, GeoJsonArea, GeoJsonPoint, GeoJsonPosition, Hole } from '../types'

const props = withDefaults(defineProps<{ hole: Hole | null; course?: Course | null; target?: GeoJsonPosition | null; fullScreen?: boolean }>(), { course: null, target: null, fullScreen: false })
const mapElement = ref<HTMLElement | null>(null)
const isLocating = ref(false)
const locationError = ref('')
const mapError = ref('')
const playerDistance = ref<number | null>(null)
const mapToken = (import.meta.env.VITE_MAPBOX_TOKEN || import.meta.env.VITE_MAPBOX_ACCESS_TOKEN) as string | undefined
let map: Map | null = null
let teeMarker: Marker | null = null
let pinMarker: Marker | null = null
let targetMarker: Marker | null = null
let playerMarker: Marker | null = null
let locationWatchId: string | null = null
let geocodedCourse = ''

function isPosition(position: GeoJsonPosition | null | undefined): position is GeoJsonPosition {
  return Boolean(position && Number.isFinite(position[0]) && Number.isFinite(position[1]))
}

function pointCoordinates(point: GeoJsonPoint | null | undefined): GeoJsonPosition | null {
  return point && isPosition(point.coordinates) ? point.coordinates : null
}

function markerElement(kind: 'tee' | 'pin' | 'player' | 'target', label: string) {
  const element = document.createElement('div')
  element.className = `course-marker course-marker-${kind}`
  element.textContent = label
  return element
}

interface HoleAreaFeature {
  type: 'Feature'
  properties: { kind: string }
  geometry: GeoJsonArea
}

interface HoleFeatureCollection {
  type: 'FeatureCollection'
  features: HoleAreaFeature[]
}

function geometryFeature(geometry: GeoJsonArea | null | undefined, kind: string): HoleAreaFeature | null {
  return geometry ? { type: 'Feature', properties: { kind }, geometry } : null
}

function holeFeatureCollection(): HoleFeatureCollection {
  const hole = props.hole
  return {
    type: 'FeatureCollection',
    features: [
      geometryFeature(hole?.fairway_geometry, 'fairway'),
      geometryFeature(hole?.green_geometry, 'green'),
      geometryFeature(hole?.bunker_geometry, 'bunker'),
      geometryFeature(hole?.water_geometry, 'water')
    ].filter((feature): feature is HoleAreaFeature => feature !== null)
  }
}

function holeCoordinates(): GeoJsonPosition[] {
  const hole = props.hole
  return [
    ...areaPositions(hole?.fairway_geometry),
    ...areaPositions(hole?.green_geometry),
    ...areaPositions(hole?.bunker_geometry),
    ...areaPositions(hole?.water_geometry),
    pointCoordinates(hole?.tee_location),
    pointCoordinates(hole?.pin_location),
    props.target
  ].filter((point): point is GeoJsonPosition => isPosition(point))
}

function holeBearing(): number | null {
  const tee = pointCoordinates(props.hole?.tee_location)
  const green = pointCoordinates(props.hole?.pin_location)
  if (!tee || !green) return null

  const toRadians = Math.PI / 180
  const latitude1 = tee[1] * toRadians
  const latitude2 = green[1] * toRadians
  const longitudeDelta = (green[0] - tee[0]) * toRadians
  const y = Math.sin(longitudeDelta) * Math.cos(latitude2)
  const x = Math.cos(latitude1) * Math.sin(latitude2)
    - Math.sin(latitude1) * Math.cos(latitude2) * Math.cos(longitudeDelta)
  return (Math.atan2(y, x) / toRadians + 360) % 360
}

function areaPositions(geometry: GeoJsonArea | null | undefined): GeoJsonPosition[] {
  if (!geometry) return []
  return geometry.type === 'Polygon'
    ? geometry.coordinates.flat(1)
    : geometry.coordinates.flat(2)
}

async function centerOnCourse() {
  if (!map || !props.course) return
  if (props.course.map_center) {
    map.flyTo({ center: props.course.map_center, zoom: 15 })
    return
  }
  const courseQuery = [props.course.name, props.course.city, props.course.state].filter(Boolean).join(', ')
  if (!courseQuery || geocodedCourse === courseQuery) return

  try {
    const courseName = props.course.name
    const searchQueries = [
      courseQuery,
      `${courseName.replace(/hedge/gi, 'henge')}, ${props.course.state || ''}`,
      `${courseName.replace(/golf course/gi, 'golf club')}, ${props.course.state || ''}`,
      `${courseName}, ${props.course.state || ''}`
    ].map((query) => query.replace(/,\s*,/g, ',').trim())
    let fallbackFeature: { center?: [number, number]; place_type?: string[] } | undefined

    for (const query of searchQueries) {
      const response = await fetch(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${mapToken}&limit=5`)
      const data = await response.json() as { features?: Array<{ center?: [number, number]; place_type?: string[] }> }
      fallbackFeature ||= data.features?.find((feature) => feature.center)
      const courseFeature = data.features?.find((feature) => feature.center && feature.place_type?.includes('poi'))
      if (courseFeature?.center) {
        map.flyTo({ center: courseFeature.center, zoom: 15 })
        geocodedCourse = courseQuery
        return
      }
    }

    if (fallbackFeature?.center) {
      map.flyTo({ center: fallbackFeature.center, zoom: 12 })
      geocodedCourse = courseQuery
    }
  } catch {
    geocodedCourse = ''
  }
}

async function updateMarkers() {
  if (!map) return
  teeMarker?.remove()
  pinMarker?.remove()
  targetMarker?.remove()
  teeMarker = null
  pinMarker = null
  targetMarker = null
  if (!props.hole) {
    await centerOnCourse()
    return
  }

  const tee = pointCoordinates(props.hole.tee_location)
  const pin = pointCoordinates(props.hole.pin_location)
  if (tee) teeMarker = new mapboxgl.Marker({ element: markerElement('tee', 'TEE'), anchor: 'bottom' }).setLngLat(tee).setPopup(new mapboxgl.Popup().setText('Tee')).addTo(map)
  if (pin) pinMarker = new mapboxgl.Marker({ element: markerElement('pin', 'PIN'), anchor: 'bottom' }).setLngLat(pin).setPopup(new mapboxgl.Popup().setText('Pin')).addTo(map)
  if (props.target && isPosition(props.target)) targetMarker = new mapboxgl.Marker({ element: markerElement('target', 'AIM'), anchor: 'bottom' }).setLngLat(props.target).setPopup(new mapboxgl.Popup().setText('Suggested target')).addTo(map)

  const points = holeCoordinates()
  const bearing = holeBearing()
  if (points.length > 1) {
    const bounds = points.reduce((result, point) => result.extend(point), new mapboxgl.LngLatBounds(points[0], points[0]))
    map.fitBounds(bounds, { padding: 44, maxZoom: 17, bearing: bearing ?? 0 })
  } else if (points.length === 1) {
    map.flyTo({ center: points[0], zoom: 17, bearing: bearing ?? 0 })
  } else {
    await centerOnCourse()
  }

  const playerPosition = playerMarker?.getLngLat()
  if (playerPosition) updateDistanceLine([playerPosition.lng, playerPosition.lat])
}

function updateCourseLayers() {
  if (!map || !map.isStyleLoaded()) return
  const source = map.getSource('hole-features') as mapboxgl.GeoJSONSource | undefined
  source?.setData(holeFeatureCollection() as Parameters<mapboxgl.GeoJSONSource['setData']>[0])
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
  source?.setData({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: [player, pin] } } as Parameters<mapboxgl.GeoJSONSource['setData']>[0])
  // publish a best-effort hole distance into the shared round store so other views (Caddie) can read it
  try {
    const currentConditions = (roundStore.conditions && (roundStore.conditions as any).value) || {}
    roundStore.setConditions({ ...currentConditions, holeDistance: playerDistance.value, playerLocation: player })
  } catch {
    // noop
  }
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
    mapError.value = 'Mapbox is not configured. Add VITE_MAPBOX_TOKEN to /.env.'
    return
  }

  mapboxgl.accessToken = mapToken
  const initialPoints = holeCoordinates()
  const initialCenter = initialPoints[0] || props.course?.map_center || [0, 0]
  const initialBearing = holeBearing()
  map = new mapboxgl.Map({
    container: mapElement.value,
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: initialCenter,
    zoom: initialPoints.length ? 16 : props.course?.map_center ? 14 : 1,
    bearing: initialBearing ?? 0,
    attributionControl: true
  })
  map.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'bottom-right')
  map.on('load', () => {
    map?.addSource('hole-features', { type: 'geojson', data: holeFeatureCollection() as Parameters<mapboxgl.GeoJSONSource['setData']>[0] })
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

watch(() => [props.hole, props.course, props.target], updateCourseLayers, { deep: true })

onBeforeUnmount(() => {
  teeMarker?.remove()
  pinMarker?.remove()
  targetMarker?.remove()
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

.course-marker-target {
  border-color: #07140f;
  background: #ffffff;
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
