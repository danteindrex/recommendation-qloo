import { Vector3 } from 'three';

export interface CulturalData3D {
  id: string;
  position: Vector3;
  value: number;
  category: CulturalCategory;
  timestamp: Date;
  confidence: number;
  metadata: Record<string, any>;
}

export interface CulturalMilestone3D {
  id: string;
  position: Vector3;
  timestamp: Date;
  event: string;
  culturalShift: number;
  confidence: number;
  platforms: SocialPlatform[];
  color: string;
  size: number;
  connections: string[];
}

export interface InfluenceNode3D {
  id: string;
  position: Vector3;
  source: string;
  influence: number;
  category: CulturalCategory;
  connections: InfluenceConnection3D[];
  color: string;
  size: number;
  isActive: boolean;
}

export interface InfluenceConnection3D {
  id: string;
  from: string;
  to: string;
  strength: number;
  color: string;
  animated: boolean;
}

export interface DiversityScore3D {
  id: string;
  position: Vector3;
  score: number;
  category: CulturalCategory;
  breakdown: DiversityBreakdown[];
  color: string;
  height: number;
}

export interface DiversityBreakdown {
  category: string;
  value: number;
  color: string;
}

export interface TrendPrediction3D {
  id: string;
  position: Vector3;
  prediction: number;
  confidence: number;
  timeframe: Date;
  category: CulturalCategory;
  confidenceRegion: ConfidenceRegion3D;
}

export interface ConfidenceRegion3D {
  center: Vector3;
  radius: number;
  opacity: number;
  color: string;
}

export interface Particle3D {
  id: string;
  position: Vector3;
  velocity: Vector3;
  life: number;
  maxLife: number;
  size: number;
  color: string;
  opacity: number;
}

export interface GestureEvent3D {
  type: 'pinch' | 'swipe' | 'rotate' | 'tap' | 'drag';
  position: Vector3;
  delta: Vector3;
  scale?: number;
  rotation?: number;
  touches?: number;
}

export interface InteractionState3D {
  hoveredObject: string | null;
  selectedObject: string | null;
  isDragging: boolean;
  dragStart: Vector3 | null;
  cameraPosition: Vector3;
  cameraTarget: Vector3;
  zoom: number;
}

export enum CulturalCategory {
  MUSIC = 'music',
  VISUAL_ARTS = 'visual_arts',
  CUISINE = 'cuisine',
  LITERATURE = 'literature',
  SOCIAL = 'social',
  TECHNOLOGY = 'technology',
  FASHION = 'fashion',
  ENTERTAINMENT = 'entertainment'
}

export enum SocialPlatform {
  INSTAGRAM = 'instagram',
  TIKTOK = 'tiktok',
  SPOTIFY = 'spotify',
  TWITTER = 'twitter',
  YOUTUBE = 'youtube'
}

export interface TimelineControls {
  currentTime: Date;
  startTime: Date;
  endTime: Date;
  isPlaying: boolean;
  playbackSpeed: number;
  scrubbing: boolean;
}

export interface CameraControls3D {
  position: Vector3;
  target: Vector3;
  zoom: number;
  rotation: { x: number; y: number; z: number };
  fov: number;
}

export interface Animation3DState {
  isAnimating: boolean;
  duration: number;
  progress: number;
  easing: string;
  loop: boolean;
}