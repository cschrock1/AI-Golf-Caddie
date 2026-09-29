import axios, { type AxiosInstance } from 'axios'
import { Capacitor } from '@capacitor/core'
import type { Club, Conditions, Course, GolferProfile, Hole, Recommendation, Round, Shot, User } from '../types'

const configuredBaseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL
const baseURL = Capacitor.isNativePlatform()
  ? import.meta.env.VITE_MOBILE_API_URL || configuredBaseURL || 'http://localhost:8000/api'
  : configuredBaseURL || 'http://localhost:8000/api'

const api: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api

export const getCurrentUser = async () => api.get<User>('/auth/me')
export const getGolferProfile = async (userId: number) => api.get<GolferProfile>(`/golfer/${userId}`)
export const getClubs = async (userId: number) => api.get<Club[]>('/clubs/', { params: { user_id: userId } })
export const createClub = async (userId: number, payload: { name: string; carry_distance?: number | null; total_distance?: number | null }) =>
  api.post<Club>('/clubs/', payload, { params: { user_id: userId } })
export const updateClub = async (clubId: number, userId: number, payload: { name: string; carry_distance?: number | null; total_distance?: number | null }) =>
  api.put<Club>(`/clubs/${clubId}`, payload, { params: { user_id: userId } })
export const deleteClub = async (clubId: number, userId: number) => api.delete(`/clubs/${clubId}`, { params: { user_id: userId } })
export const getCourses = async () => api.get<Course[]>('/courses/')
export const importCourse = async (payload: Record<string, unknown>) => api.post('/courses/import', payload)
export const importCourseFromProvider = async (payload: { name: string; city?: string; state?: string }) =>
  api.post('/courses/import/provider', payload)
export const getCourse = async (courseId: number) => api.get<Course>(`/courses/${courseId}`)
export const getCourseHoles = async (courseId: number) => api.get<Hole[]>(`/courses/${courseId}/holes`)
export const getHole = async (courseId: number, holeNumber: number) => api.get<Hole>(`/courses/${courseId}/holes/${holeNumber}`)
export const getRounds = async (userId: number) => api.get<Round[]>('/rounds/', { params: { user_id: userId } })
export const createRound = async (payload: { user_id: number; course_id: number; date: string; score?: number | null }) =>
  api.post<Round>('/rounds/', payload)
export const getShots = async (roundId: number) => api.get<Shot[]>('/shots/', { params: { round_id: roundId } })
export const createShot = async (payload: Omit<Shot, 'id'>) => api.post<Shot>('/shots/', payload)
export const getRecommendation = async (holeId: number, playerLocation: [number, number]) =>
  api.post<Recommendation>('/recommendations/', { hole_id: holeId, player_location: playerLocation })
export const getCurrentWeather = async (courseId: number, holeNumber: number) => {
  const response = await api.get<{
    temperature_f: number | null
    wind_speed_mph: number | null
    wind_direction_degrees: number | null
    observed_at: string | null
    timezone: string | null
    source: string
  }>('/weather/current', { params: { course_id: courseId, hole_number: holeNumber } })
  const weather: Conditions = {
    temperature: response.data.temperature_f,
    windSpeed: response.data.wind_speed_mph,
    windDirectionDegrees: response.data.wind_direction_degrees,
    observedAt: response.data.observed_at,
    timezone: response.data.timezone,
    source: response.data.source,
  }
  return { ...response, data: weather }
}
export const getCaddieExplanation = async (holeId: number, playerLocation: [number, number], question: string) =>
  api.post<{
    recommendation: Recommendation
    explanation: string
    explanation_source: 'openai' | 'rules'
  }>('/caddie/explain', { hole_id: holeId, player_location: playerLocation, question })
export const getRoundScores = async (roundId: number) => api.get('/round_scores/', { params: { round_id: roundId } })
export const saveRoundScores = async (userId: number, roundId: number, scores: Array<{ hole_id?: number; hole_number?: number; strokes: number }>) =>
  api.post('/round_scores/batch', scores, { params: { user_id: userId, round_id: roundId } })
