import axios, { type AxiosInstance } from 'axios'
import { Capacitor } from '@capacitor/core'
import type { Club, Course, GolferProfile, Hole, Round, User } from '../types'

const configuredBaseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL
const baseURL = Capacitor.isNativePlatform()
  ? import.meta.env.VITE_MOBILE_API_URL || 'http://192.168.86.38:8000/api'
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
export const getShots = async (roundId: number) => api.get('/shots/', { params: { round_id: roundId } })
export const createShot = async (payload: Record<string, unknown>) => api.post('/shots/', payload)
export const getRecommendation = async () => Promise.resolve({ data: null })
