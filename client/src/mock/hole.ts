import type { Hole } from '../types'

export const stonehedgeHoles: Hole[] = [
  { id: 1, course_id: 5, hole_number: 1, par: 4, yardage: 385 },
  { id: 2, course_id: 5, hole_number: 2, par: 5, yardage: 505 },
  { id: 3, course_id: 5, hole_number: 3, par: 3, yardage: 165 },
  { id: 4, course_id: 5, hole_number: 4, par: 4, yardage: 375 },
  { id: 5, course_id: 5, hole_number: 5, par: 4, yardage: 410 },
  { id: 6, course_id: 5, hole_number: 6, par: 3, yardage: 175 },
  { id: 7, course_id: 5, hole_number: 7, par: 4, yardage: 390 },
  { id: 8, course_id: 5, hole_number: 8, par: 5, yardage: 525 },
  { id: 9, course_id: 5, hole_number: 9, par: 4, yardage: 420 },
  { id: 10, course_id: 5, hole_number: 10, par: 4, yardage: 395 },
  { id: 11, course_id: 5, hole_number: 11, par: 5, yardage: 535 },
  { id: 12, course_id: 5, hole_number: 12, par: 4, yardage: 360 },
  { id: 13, course_id: 5, hole_number: 13, par: 3, yardage: 185 },
  { id: 14, course_id: 5, hole_number: 14, par: 4, yardage: 405 },
  { id: 15, course_id: 5, hole_number: 15, par: 5, yardage: 515 },
  { id: 16, course_id: 5, hole_number: 16, par: 4, yardage: 400 },
  { id: 17, course_id: 5, hole_number: 17, par: 3, yardage: 155 },
  { id: 18, course_id: 5, hole_number: 18, par: 4, yardage: 430 }
]

export const demoHole = {
  courseName: 'Stonehedge Golf Course',
  holeNumber: 7,
  handicap: 18,
  tee: 'Back Tee',
  windSpeed: 12,
  windDirection: 'West-Northwest',
  temperature: 64,
  elevation: 22,
  note: 'Demo values for design review only - not live weather data.'
}

export const demoCourse = {
  id: 5,
  name: 'Stonehedge Golf Course',
  city: 'Warsaw',
  state: 'IN'
}
