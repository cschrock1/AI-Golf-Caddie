import type { ChatMessage, Conditions, Recommendation } from '../types'

export const demoRecommendation: Recommendation = {
  clubName: '9-Iron',
  confidence: 94,
  carry: 112,
  total: 118,
  tempo: 85,
  landing: 'Soft hold',
  target: '4 yards left of pin',
  rationale:
    'With the gusty 14 mph Pacific headwind, a smooth 9-iron should provide enough carry while keeping the ball below the wind.',
  alternativeClub: 'Pitching Wedge',
  alternativeRisk: 'Higher front bunker risk',
  riskLevel: 'Medium'
}

export const demoConditions: Conditions = {
  windSpeed: 14,
  windDirection: 'South-Southeast',
  temperature: 61,
  elevation: 18,
  note: 'Sample conditions for layout and UI testing.'
}

export const demoMessages: ChatMessage[] = [
  {
    id: 'ai-1',
    role: 'assistant',
    timestamp: '10:42 AM',
    content:
      "We’re standing on the iconic 7th at Pebble Beach. Ocean breeze is gusting at 14 mph directly in your face from the South-Southeast."
  },
  {
    id: 'ai-2',
    role: 'assistant',
    timestamp: '10:42 AM',
    content: 'Recommended: 9-Iron. Carry 112 yards, tempo 85%, landing soft hold.'
  }
]
