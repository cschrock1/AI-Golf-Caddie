<template>
  <section class="relative overflow-hidden border border-[#214335] bg-[#d9e1d8] shadow-[inset_0_0_0_1px_rgba(255,255,255,0.08)]" :class="fullScreen ? 'rounded-none border-x-0 border-t-0' : 'rounded-[30px]'">
    <div ref="mapElement" class="w-full" :class="fullScreen ? 'h-[100dvh]' : 'h-[620px]'" role="img" aria-label="Interactive Mapbox GPS map showing the current golf hole"></div>
    <div
      v-if="distanceLabelPosition && playerDistance != null"
      class="course-distance-chip pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-1/2"
      :style="{ left: `${distanceLabelPosition.x}px`, top: `${distanceLabelPosition.y}px` }"
      aria-live="polite"
    >{{ playerDistance }} yd</div>

    <div v-if="fullScreen" class="absolute right-3 top-44 z-10 flex flex-col gap-2">
      <button type="button" class="flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-[#111814]/90 text-2xl font-semibold text-white shadow-lg backdrop-blur" aria-label="Zoom in" @click="map?.zoomIn()">+</button>
      <button type="button" class="flex h-11 w-11 items-center justify-center rounded-xl border border-white/15 bg-[#111814]/90 text-2xl font-semibold text-white shadow-lg backdrop-blur" aria-label="Zoom out" @click="map?.zoomOut()">−</button>
    </div>

    <p v-if="mapError" class="absolute inset-x-3 z-10 rounded-xl bg-black/65 p-2 text-[10px] leading-5 text-[#f7dfe2]" :class="fullScreen ? 'top-36' : 'top-14'" role="alert">{{ mapError }}</p>
  </section>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { roundStore } from '../stores/round'
import mapboxgl, { type Map, type Marker } from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import type { Course, GeoJsonArea, GeoJsonPoint, GeoJsonPosition, Hole } from '../types'

const props = withDefaults(defineProps<{ hole: Hole | null; course?: Course | null; fullScreen?: boolean }>(), { course: null, fullScreen: false })
const emit = defineEmits<{ 'distance-change': [distance: number] }>()
const mapElement = ref<HTMLElement | null>(null)
const mapError = ref('')
const playerDistance = ref<number | null>(null)
const distanceLabelPosition = ref<{ x: number; y: number } | null>(null)
const distanceMidpoint = ref<GeoJsonPosition | null>(null)
const mapToken = (import.meta.env.VITE_MAPBOX_TOKEN || import.meta.env.VITE_MAPBOX_ACCESS_TOKEN) as string | undefined
let map: Map | null = null
let teeMarker: Marker | null = null
let pinMarker: Marker | null = null
let geocodedCourse = ''
const KML_HOLE_1_TEE: GeoJsonPosition = [-85.78491237783246, 41.2053717585335]
const KML_HOLE_1_GREEN_CENTER: GeoJsonPosition = [-85.78498208763907, 41.20273912570412]

function isPosition(position: GeoJsonPosition | null | undefined): position is GeoJsonPosition {
  return Boolean(position && Number.isFinite(position[0]) && Number.isFinite(position[1]))
}

function pointCoordinates(point: GeoJsonPoint | null | undefined): GeoJsonPosition | null {
  return point && isPosition(point.coordinates) ? point.coordinates : null
}

function teeCoordinates(hole: Hole | null | undefined): GeoJsonPosition | null {
  if (hole?.hole_number === 1 && props.course?.name.toLowerCase().includes('stonehenge')) return KML_HOLE_1_TEE
  return pointCoordinates(hole?.tee_location)
}

function greenCoordinates(hole: Hole | null | undefined): GeoJsonPosition | null {
  if (hole?.hole_number === 1 && props.course?.name.toLowerCase().includes('stonehenge')) return KML_HOLE_1_GREEN_CENTER
  return pointCoordinates(hole?.pin_location)
}

function markerElement(kind: 'tee' | 'pin', label: string) {
  const element = document.createElement('div')
  element.className = `course-marker course-marker-${kind}`
  element.setAttribute('aria-label', label)
  element.title = label
  if (kind === 'tee') {
    element.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-7.2 8-13a8 8 0 1 0-16 0c0 5.8 8 13 8 13Z"/><circle cx="12" cy="9" r="2.7"/></svg>'
  }
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
  const tee = teeCoordinates(hole)
  const green = greenCoordinates(hole)
  if (hole?.hole_number === 1 && props.course?.name.toLowerCase().includes('stonehenge')) {
    return [tee, green].filter((point): point is GeoJsonPosition => isPosition(point))
  }
  return [
    ...areaPositions(hole?.fairway_geometry),
    ...areaPositions(hole?.green_geometry),
    ...areaPositions(hole?.bunker_geometry),
    ...areaPositions(hole?.water_geometry),
    tee,
    green,
  ].filter((point): point is GeoJsonPosition => isPosition(point))
}

function bearingBetween(from: GeoJsonPosition, to: GeoJsonPosition): number {
  const toRadians = Math.PI / 180
  const latitude1 = from[1] * toRadians
  const latitude2 = to[1] * toRadians
  const longitudeDelta = (to[0] - from[0]) * toRadians
  const y = Math.sin(longitudeDelta) * Math.cos(latitude2)
  const x = Math.cos(latitude1) * Math.sin(latitude2)
    - Math.sin(latitude1) * Math.cos(latitude2) * Math.cos(longitudeDelta)
  return (Math.atan2(y, x) / toRadians + 360) % 360
}

function holeBearing(): number | null {
  const tee = teeCoordinates(props.hole)
  const green = greenCoordinates(props.hole)
  return tee && green ? bearingBetween(tee, green) : null
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
  teeMarker = null
  pinMarker = null
  if (!props.hole) {
    await centerOnCourse()
    return
  }

  const tee = teeCoordinates(props.hole)
  const pin = greenCoordinates(props.hole)
  if (tee) {
    teeMarker = new mapboxgl.Marker({ element: markerElement('tee', 'TEE'), anchor: 'bottom', draggable: props.fullScreen })
      .setLngLat(tee)
      .setPopup(new mapboxgl.Popup().setText('Drag this marker to set your position'))
      .addTo(map)
    const updateDraggedTee = (centerMap: boolean, publishPosition: boolean) => {
      const position = teeMarker?.getLngLat()
      if (position) updateDistanceLine([position.lng, position.lat], centerMap, publishPosition)
    }
    teeMarker.on('drag', () => updateDraggedTee(false, false))
    teeMarker.on('dragend', () => updateDraggedTee(true, true))
  }
  if (pin) pinMarker = new mapboxgl.Marker({ element: markerElement('pin', 'Center of green'), anchor: 'bottom' }).setLngLat(pin).setPopup(new mapboxgl.Popup().setText('Center of green')).addTo(map)

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

  if (tee && pin) updateDistanceLine(tee, true, true)
}

function updateCourseLayers() {
  if (!map) return
  const source = map.getSource('hole-features') as mapboxgl.GeoJSONSource | undefined
  if (!source) return
  source?.setData(holeFeatureCollection() as Parameters<mapboxgl.GeoJSONSource['setData']>[0])
  void updateMarkers()
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

function updateDistanceLabelPosition() {
  if (!map || !distanceMidpoint.value) return
  const point = map.project(distanceMidpoint.value)
  distanceLabelPosition.value = { x: point.x, y: point.y }
}

function updateDistanceLine(player: [number, number], centerMap = false, publishPosition = false) {
  const green = greenCoordinates(props.hole)
  if (!map || !green) return
  const pin = green
  playerDistance.value = distanceInYards(player, pin)
  const source = map.getSource('player-pin-line') as mapboxgl.GeoJSONSource | undefined
  source?.setData({ type: 'Feature', properties: {}, geometry: { type: 'LineString', coordinates: [player, pin] } } as Parameters<mapboxgl.GeoJSONSource['setData']>[0])
  distanceMidpoint.value = [(player[0] + pin[0]) / 2, (player[1] + pin[1]) / 2]
  updateDistanceLabelPosition()
  emit('distance-change', playerDistance.value)

  if (centerMap) {
    // Keep the green at the top of the screen by rotating toward it, independent
    // of the golfer's compass heading or the way the hole is oriented.
    const center: [number, number] = [(player[0] + pin[0]) / 2, (player[1] + pin[1]) / 2]
    map.easeTo({ center, bearing: bearingBetween(player, pin), duration: 450, essential: false })
  }

  // publish a best-effort hole distance into the shared round store so other views (Caddie) can read it
  try {
    if (!publishPosition) return
    const currentConditions = (roundStore.conditions && (roundStore.conditions as any).value) || {}
    roundStore.setConditions({ ...currentConditions, holeDistance: playerDistance.value, playerLocation: player, locationAccuracy: null })
  } catch {
    // noop
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
  map.on('move', updateDistanceLabelPosition)
  map.on('resize', updateDistanceLabelPosition)
  // Keep the camera locked to Hole 1; golfers can zoom, and the draggable tee
  // marker still adjusts the starting position without panning away from the hole.
  map.dragPan.disable()
  map.scrollZoom.disable()
  map.dragRotate.disable()
  map.touchZoomRotate.disableRotation()
  map.on('load', () => {
    map?.addSource('hole-features', { type: 'geojson', data: holeFeatureCollection() as Parameters<mapboxgl.GeoJSONSource['setData']>[0] })
    map?.addSource('player-pin-line', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } })
    map?.addLayer({ id: 'hole-fairway', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'fairway'], paint: { 'fill-color': '#44775a', 'fill-opacity': 0.4 } })
    map?.addLayer({ id: 'hole-green', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'green'], paint: { 'fill-color': '#73a875', 'fill-opacity': 0.65 } })
    map?.addLayer({ id: 'hole-bunker', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'bunker'], paint: { 'fill-color': '#d5b078', 'fill-opacity': 0.8 } })
    map?.addLayer({ id: 'hole-water', type: 'fill', source: 'hole-features', filter: ['==', ['get', 'kind'], 'water'], paint: { 'fill-color': '#287bb5', 'fill-opacity': 0.55 } })
    map?.addLayer({ id: 'player-pin-line', type: 'line', source: 'player-pin-line', paint: { 'line-color': '#ffffff', 'line-width': 2.5, 'line-opacity': 0.95, 'line-dasharray': [2, 2] } })
    updateCourseLayers()
  })
  map.on('error', () => { mapError.value = 'Mapbox could not load the map. Check the token and network connection.' })
})

watch(() => [props.hole, props.course], updateCourseLayers, { deep: true })

onBeforeUnmount(() => {
  teeMarker?.remove()
  pinMarker?.remove()
  map?.remove()
})
</script>

<style scoped>
:deep(.course-marker) {
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

:deep(.course-marker-tee) {
  display: grid;
  width: 20px;
  height: 20px;
  place-items: center;
  padding: 0;
  border: 1.5px solid #ffffff;
  border-radius: 50% 50% 50% 3px;
  background: #c8ff00;
  cursor: grab;
  touch-action: none;
  transform: rotate(-45deg);
}

:deep(.course-marker-tee svg) {
  width: 11px;
  height: 11px;
  fill: none;
  stroke: #07140f;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.5;
  transform: rotate(45deg);
}

:deep(.course-marker-tee:active) {
  cursor: grabbing;
}

:deep(.course-marker-pin) {
  position: relative;
  width: 28px;
  height: 36px;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  color: transparent;
  box-shadow: none;
}

:deep(.course-marker-pin::before) {
  position: absolute;
  inset: 0;
  background: #c8ff00;
  clip-path: polygon(50% 100%, 5% 45%, 7% 25%, 18% 8%, 35% 0, 65% 0, 82% 8%, 93% 25%, 95% 45%);
  content: '';
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.55));
}

:deep(.course-marker-pin::after) {
  position: absolute;
  top: 8px;
  left: 50%;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #07140f;
  content: '';
  transform: translateX(-50%);
}

.course-distance-chip {
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 999px;
  background: #07140f;
  padding: 7px 10px;
  color: #c8ff00;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.04em;
  white-space: nowrap;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.55);
}

.legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin-right: 4px;
  border-radius: 999px;
}
</style>
