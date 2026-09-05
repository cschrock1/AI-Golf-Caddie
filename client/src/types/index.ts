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
  green_geometry?: GeoJsonPolygon | GeoJsonMultiPolygon | null
  fairway_geometry?: GeoJsonPolygon | null
  bunker_geometry?: GeoJsonMultiPolygon | null
  water_geometry?: GeoJsonMultiPolygon | null
}

export interface GeoJsonPoint {
  type: 'Point'
  coordinates: [number, number]
}

export interface GeoJsonPolygon {
  type: 'Polygon'
  coordinates: number[][][]
}

export interface GeoJsonMultiPolygon {
  type: 'MultiPolygon'
  coordinates: number[][][][]
}

export interface ApiErrorResponse {
  detail?: string
}

export interface Course {
  id: number
  name: string
  city?: string | null
  state?: string | null
  holes?: Hole[]
}

export interface Round {
  id: number
  user_id: number
  course_id: number
  date: string
  score?: number | null
}

export interface Shot {
  id: number
  round_id: number
  club_id?: number | null
  hole_id?: number | null
  distance?: number | null
  notes?: string | null
}

export interface Conditions {
  windSpeed: number
  windDirection: string
  temperature: number
  elevation?: number
  note: string
}

export interface Recommendation {
  clubName: string
  confidence: number
  carry: number
  total: number
  tempo: number
  landing: string
  target: string
  rationale: string
  alternativeClub: string
  alternativeRisk: string
  riskLevel: 'Low' | 'Medium' | 'High'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}
