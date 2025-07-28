export interface CulturalProfile {
  userId: string
  culturalDiversityScore: number
  evolutionTimeline: CulturalMilestone[]
  influenceNetwork: InfluenceNode[]
  blindSpots: CulturalBlindSpot[]
  recommendations: CulturalRecommendation[]
  predictionAccuracy: number
}

export interface CulturalMilestone {
  timestamp: Date
  event: string
  culturalShift: number
  confidence: number
  platforms: SocialPlatform[]
}

export interface InfluenceNode {
  source: string
  influence: number
  category: CulturalCategory
  connections: string[]
}

export interface CulturalBlindSpot {
  category: string
  description: string
  severity: 'low' | 'medium' | 'high'
  recommendations: string[]
}

export interface CulturalRecommendation {
  id: string
  type: 'content' | 'experience' | 'challenge'
  title: string
  description: string
  confidenceScore: number
  culturalCategory: string
  status: 'pending' | 'accepted' | 'dismissed'
}

export type SocialPlatform = 'instagram' | 'tiktok' | 'spotify'
export type CulturalCategory = 'music' | 'art' | 'food' | 'travel' | 'lifestyle' | 'entertainment'