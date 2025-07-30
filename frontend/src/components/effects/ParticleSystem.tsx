import React, { useEffect, useRef, useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export interface Particle {
  id: number
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  size: number
  color: string
  opacity: number
  rotation: number
  rotationSpeed: number
  type: 'circle' | 'star' | 'heart' | 'sparkle' | 'triangle'
}

interface ParticleSystemProps {
  particles?: Particle[]
  maxParticles?: number
  emissionRate?: number
  gravity?: number
  wind?: number
  fadeOut?: boolean
  className?: string
  style?: React.CSSProperties
}

interface ParticleEmitterProps {
  x: number
  y: number
  count?: number
  spread?: number
  velocity?: number
  colors?: string[]
  size?: { min: number; max: number }
  life?: { min: number; max: number }
  types?: Particle['type'][]
  onComplete?: () => void
}

// Particle shape components
const ParticleShape: React.FC<{ particle: Particle }> = ({ particle }) => {
  const baseStyle = {
    position: 'absolute' as const,
    left: particle.x,
    top: particle.y,
    width: particle.size,
    height: particle.size,
    opacity: particle.opacity,
    transform: `rotate(${particle.rotation}deg)`,
    pointerEvents: 'none' as const
  };

  switch (particle.type) {
    case 'circle':
      return (
        <div
          style={{
            ...baseStyle,
            backgroundColor: particle.color,
            borderRadius: '50%',
            boxShadow: `0 0 ${particle.size}px ${particle.color}40`
          }}
        />
      );
    
    case 'star':
      return (
        <svg
          style={baseStyle}
          viewBox="0 0 24 24"
          fill={particle.color}
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      );
    
    case 'heart':
      return (
        <svg
          style={baseStyle}
          viewBox="0 0 24 24"
          fill={particle.color}
        >
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
        </svg>
      );
    
    case 'sparkle':
      return (
        <svg
          style={baseStyle}
          viewBox="0 0 24 24"
          fill={particle.color}
        >
          <path d="M12 0l2.5 7.5L22 10l-7.5 2.5L12 20l-2.5-7.5L2 10l7.5-2.5L12 0z" />
        </svg>
      );
    
    case 'triangle':
      return (
        <div
          style={{
            ...baseStyle,
            width: 0,
            height: 0,
            borderLeft: `${particle.size / 2}px solid transparent`,
            borderRight: `${particle.size / 2}px solid transparent`,
            borderBottom: `${particle.size}px solid ${particle.color}`,
            filter: `drop-shadow(0 0 ${particle.size / 2}px ${particle.color}40)`
          }}
        />
      );
    
    default:
      return (
        <div
          style={{
            ...baseStyle,
            backgroundColor: particle.color,
            borderRadius: '50%'
          }}
        />
      );
  }
};

// Main particle system component
const ParticleSystem: React.FC<ParticleSystemProps> = ({
  particles: externalParticles = [],
  maxParticles = 100,
  emissionRate = 0,
  gravity = 0.1,
  wind = 0,
  fadeOut = true,
  className = '',
  style = {}
}) => {
  const [particles, setParticles] = useState<Particle[]>(externalParticles);
  const animationRef = useRef<number>();
  const lastEmissionRef = useRef<number>(0);
  const particleIdRef = useRef<number>(0);

  // Update particles animation loop
  const updateParticles = useCallback(() => {
    setParticles(prevParticles => {
      const now = Date.now();
      
      // Add new particles based on emission rate
      let newParticles = [...prevParticles];
      if (emissionRate > 0 && now - lastEmissionRef.current > 1000 / emissionRate) {
        if (newParticles.length < maxParticles) {
          newParticles.push(createRandomParticle());
          lastEmissionRef.current = now;
        }
      }
      
      // Update existing particles
      return newParticles
        .map(particle => ({
          ...particle,
          x: particle.x + particle.vx + wind,
          y: particle.y + particle.vy,
          vy: particle.vy + gravity,
          life: particle.life - 0.016, // ~60fps
          opacity: fadeOut ? particle.life / particle.maxLife : particle.opacity,
          rotation: particle.rotation + particle.rotationSpeed
        }))
        .filter(particle => particle.life > 0);
    });
    
    animationRef.current = requestAnimationFrame(updateParticles);
  }, [emissionRate, maxParticles, gravity, wind, fadeOut]);

  // Create a random particle
  const createRandomParticle = (): Particle => ({
    id: particleIdRef.current++,
    x: Math.random() * (window.innerWidth || 800),
    y: Math.random() * (window.innerHeight || 600),
    vx: (Math.random() - 0.5) * 4,
    vy: (Math.random() - 0.5) * 4,
    life: 3 + Math.random() * 2,
    maxLife: 3 + Math.random() * 2,
    size: 4 + Math.random() * 8,
    color: `hsl(${Math.random() * 360}, 70%, 60%)`,
    opacity: 1,
    rotation: Math.random() * 360,
    rotationSpeed: (Math.random() - 0.5) * 4,
    type: ['circle', 'star', 'heart', 'sparkle', 'triangle'][Math.floor(Math.random() * 5)] as Particle['type']
  });

  // Start/stop animation
  useEffect(() => {
    if (particles.length > 0 || emissionRate > 0) {
      animationRef.current = requestAnimationFrame(updateParticles);
    }
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [particles.length, emissionRate, updateParticles]);

  // Update external particles
  useEffect(() => {
    setParticles(externalParticles);
  }, [externalParticles]);

  return (
    <div
      className={`absolute inset-0 pointer-events-none overflow-hidden ${className}`}
      style={style}
    >
      <AnimatePresence>
        {particles.map(particle => (
          <motion.div
            key={particle.id}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: particle.opacity }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ParticleShape particle={particle} />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

// Particle emitter hook
export const useParticleEmitter = () => {
  const [particles, setParticles] = useState<Particle[]>([]);
  const particleIdRef = useRef<number>(0);

  const emit = useCallback(({
    x,
    y,
    count = 10,
    spread = 45,
    velocity = 3,
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
    size = { min: 4, max: 12 },
    life = { min: 1, max: 3 },
    types = ['circle', 'star', 'sparkle'],
    onComplete
  }: ParticleEmitterProps) => {
    const newParticles: Particle[] = [];
    
    for (let i = 0; i < count; i++) {
      const angle = (Math.random() - 0.5) * spread * (Math.PI / 180);
      const speed = velocity * (0.5 + Math.random() * 0.5);
      const particleLife = life.min + Math.random() * (life.max - life.min);
      
      newParticles.push({
        id: particleIdRef.current++,
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: particleLife,
        maxLife: particleLife,
        size: size.min + Math.random() * (size.max - size.min),
        color: colors[Math.floor(Math.random() * colors.length)],
        opacity: 1,
        rotation: Math.random() * 360,
        rotationSpeed: (Math.random() - 0.5) * 6,
        type: types[Math.floor(Math.random() * types.length)] as Particle['type']
      });
    }
    
    setParticles(prev => [...prev, ...newParticles]);
    
    // Call onComplete after particles should be done
    if (onComplete) {
      setTimeout(onComplete, life.max * 1000);
    }
  }, []);

  const clear = useCallback(() => {
    setParticles([]);
  }, []);

  return { particles, emit, clear };
};

// Preset particle effects
export const ParticlePresets = {
  celebration: {
    count: 50,
    spread: 60,
    velocity: 5,
    colors: ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
    types: ['star', 'circle', 'heart'] as Particle['type'][],
    size: { min: 6, max: 16 },
    life: { min: 2, max: 4 }
  },
  
  magic: {
    count: 30,
    spread: 90,
    velocity: 2,
    colors: ['#667eea', '#764ba2', '#f093fb', '#a8edea'],
    types: ['sparkle', 'star'] as Particle['type'][],
    size: { min: 4, max: 10 },
    life: { min: 1.5, max: 3 }
  },
  
  love: {
    count: 20,
    spread: 30,
    velocity: 1.5,
    colors: ['#FF6B6B', '#FF8E8E', '#FFB3B3'],
    types: ['heart'] as Particle['type'][],
    size: { min: 8, max: 16 },
    life: { min: 2, max: 4 }
  },
  
  success: {
    count: 25,
    spread: 45,
    velocity: 3,
    colors: ['#43e97b', '#38f9d7', '#4facfe'],
    types: ['circle', 'star'] as Particle['type'][],
    size: { min: 5, max: 12 },
    life: { min: 1, max: 2.5 }
  }
};

export default ParticleSystem