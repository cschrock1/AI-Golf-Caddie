export interface User {
  id: number
  email: string
  full_name?: string | null
}

export interface GolferProfile {
  id: number
  user_id: number
  handicap?: number | null
  preferred_tee?: string | null
}

export interface Club {
  id: number
  user_id: number
  name: string
  carry_distance?: number | null
  total_distance?: number | null
}

export interface Hole {
  id: number
  course_id: number
  hole_number: number
  par: number
  yardage: number
  tee_location?: GeoJsonPoint | null
  pin_location?: GeoJsonPoint | null
  green_geometry?: GeoJsonArea | null
  fairway_geometry?: GeoJsonArea | null
  bunker_geometry?: GeoJsonArea | null
  water_geometry?: GeoJsonArea | null
}

export type GeoJsonArea = GeoJsonPolygon | GeoJsonMultiPolygon

export interface GeoJsonPoint {
  type: 'Point'
  coordinates: GeoJsonPosition
}

export type GeoJsonPosition = [longitude: number, latitude: number]

export interface GeoJsonPolygon {
  type: 'Polygon'
  coordinates: GeoJsonPosition[][]
}

export interface GeoJsonMultiPolygon {
  type: 'MultiPolygon'
  coordinates: GeoJsonPosition[][][]
}

export interface ApiErrorResponse {
  detail?: string
}

export interface Course {
  id: number
  name: string
  city?: string | null
  state?: string | null
  map_center?: [number, number]
  holes?: Hole[]
}

export interface Round {
  id: number
  user_id: number
  course_id: number
  date: string
  score?: number | null
  is_complete?: boolean
}

export interface Shot {
  id: number
  round_id: number
  club_id: number
  hole_id: number
  start_distance?: number | null
  end_distance?: number | null
  result?: string | null
}

export interface RoundScore {
  id: number
  round_id: number
  hole_id: number
  hole_number: number
  strokes: number
}

export interface Conditions {
  windSpeed?: number | null
  windDirectionDegrees?: number | null
  temperature?: number | null
  observedAt?: string | null
  timezone?: string | null
  source?: string | null
  note?: string | null
  holeDistance?: number | null
  playerLocation?: GeoJsonPosition | null
  locationAccuracy?: number | null
}

export interface Recommendation {
  club_id: number
  club_name: string
  carry_yards: number
  target_yards: number
  target_location: GeoJsonPosition
  target_name: string
  risk: 'Low' | 'Medium' | 'High'
  rationale: string
  alternative_club?: string | null
  alternative_carry_yards?: number | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  provider?: string
}

export interface CaddieConversationMessage {
  role: 'user' | 'assistant'
  content: string
}
