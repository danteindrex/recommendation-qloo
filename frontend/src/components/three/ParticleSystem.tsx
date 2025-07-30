import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Points, PointsMaterial } from '@react-three/drei';
import { Vector3, Color, BufferGeometry, Float32BufferAttribute, AdditiveBlending } from 'three';
import * as THREE from 'three';
import { Particle3D } from '../types/cultural3d.types';

interface ParticleSystemProps {
  particleCount?: number;
  position?: Vector3;
  spread?: number;
  speed?: number;
  life?: number;
  size?: number;
  color?: string | string[];
  emissionRate?: number;
  gravity?: Vector3;
  turbulence?: number;
  fadeIn?: boolean;
  fadeOut?: boolean;
  burst?: boolean;
  burstCount?: number;
  shape?: 'sphere' | 'cone' | 'box' | 'plane';
  texture?: THREE.Texture;
  blending?: THREE.Blending;
  onParticleUpdate?: (particle: Particle3D, index: number) => void;
}

interface ParticleState {
  position: Vector3;
  velocity: Vector3;
  life: number;
  maxLife: number;
  size: number;
  color: Color;
  opacity: number;
  active: boolean;
}

const ParticleSystem: React.FC<ParticleSystemProps> = ({
  particleCount = 1000,
  position = new Vector3(0, 0, 0),
  spread = 5,
  speed = 1,
  life = 3,
  size = 0.1,
  color = '#ffffff',
  emissionRate = 100,
  gravity = new Vector3(0, -0.01, 0),
  turbulence = 0.1,
  fadeIn = true,
  fadeOut = true,
  burst = false,
  burstCount = 100,
  shape = 'sphere',
  texture,
  blending = AdditiveBlending,
  onParticleUpdate
}) => {
  const pointsRef = useRef<THREE.Points>(null);
  const particles = useRef<ParticleState[]>([]);
  const emissionTimer = useRef(0);
  const geometryRef = useRef<BufferGeometry>(null);

  // Initialize particles
  useEffect(() => {
    particles.current = Array.from({ length: particleCount }, () => ({
      position: new Vector3(),
      velocity: new Vector3(),
      life: 0,
      maxLife: life + Math.random() * life * 0.5,
      size: size + Math.random() * size * 0.5,
      color: new Color(Array.isArray(color) ? color[Math.floor(Math.random() * color.length)] : color),
      opacity: 0,
      active: false
    }));

    if (burst) {
      // Emit burst of particles immediately
      for (let i = 0; i < Math.min(burstCount, particleCount); i++) {
        emitParticle(i);
      }
    }
  }, [particleCount, life, size, color, burst, burstCount]);

  // Particle emission function
  const emitParticle = (index: number) => {
    const particle = particles.current[index];
    if (!particle) return;

    // Reset particle properties
    particle.position.copy(position);
    particle.life = particle.maxLife;
    particle.opacity = fadeIn ? 0 : 1;
    particle.active = true;

    // Generate initial velocity based on shape
    switch (shape) {
      case 'sphere':
        particle.velocity.set(
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2,
          (Math.random() - 0.5) * 2
        ).normalize().multiplyScalar(speed * (0.5 + Math.random() * 0.5));
        break;

      case 'cone':
        const angle = Math.random() * Math.PI * 2;
        const radius = Math.random() * spread;
        particle.velocity.set(
          Math.cos(angle) * radius,
          Math.random() * speed,
          Math.sin(angle) * radius
        );
        break;

      case 'box':
        particle.velocity.set(
          (Math.random() - 0.5) * spread,
          (Math.random() - 0.5) * spread,
          (Math.random() - 0.5) * spread
        ).multiplyScalar(speed);
        break;

      case 'plane':
        particle.velocity.set(
          (Math.random() - 0.5) * spread,
          0,
          (Math.random() - 0.5) * spread
        ).multiplyScalar(speed);
        break;
    }

    // Add some randomness to initial position
    particle.position.add(
      new Vector3(
        (Math.random() - 0.5) * spread * 0.1,
        (Math.random() - 0.5) * spread * 0.1,
        (Math.random() - 0.5) * spread * 0.1
      )
    );
  };

  // Update particle system
  useFrame((state, delta) => {
    if (!geometryRef.current) return;

    const positions = [];
    const colors = [];
    const sizes = [];
    const opacities = [];

    // Update emission timer
    if (!burst) {
      emissionTimer.current += delta;
      const emissionInterval = 1 / emissionRate;

      while (emissionTimer.current >= emissionInterval) {
        // Find inactive particle to emit
        const inactiveIndex = particles.current.findIndex(p => !p.active);
        if (inactiveIndex !== -1) {
          emitParticle(inactiveIndex);
        }
        emissionTimer.current -= emissionInterval;
      }
    }

    // Update each particle
    particles.current.forEach((particle, index) => {
      if (!particle.active) {
        // Add inactive particle data (invisible)
        positions.push(0, 0, 0);
        colors.push(0, 0, 0);
        sizes.push(0);
        opacities.push(0);
        return;
      }

      // Update life
      particle.life -= delta;
      if (particle.life <= 0) {
        particle.active = false;
        positions.push(0, 0, 0);
        colors.push(0, 0, 0);
        sizes.push(0);
        opacities.push(0);
        return;
      }

      // Update position
      particle.position.add(particle.velocity.clone().multiplyScalar(delta));

      // Apply gravity
      particle.velocity.add(gravity.clone().multiplyScalar(delta));

      // Apply turbulence
      if (turbulence > 0) {
        const turbulenceForce = new Vector3(
          (Math.random() - 0.5) * turbulence,
          (Math.random() - 0.5) * turbulence,
          (Math.random() - 0.5) * turbulence
        );
        particle.velocity.add(turbulenceForce.multiplyScalar(delta));
      }

      // Update opacity based on life
      const lifeRatio = particle.life / particle.maxLife;
      if (fadeIn && lifeRatio > 0.8) {
        particle.opacity = (1 - lifeRatio) * 5; // Fade in during first 20% of life
      } else if (fadeOut && lifeRatio < 0.2) {
        particle.opacity = lifeRatio * 5; // Fade out during last 20% of life
      } else {
        particle.opacity = 1;
      }

      // Custom particle update callback
      if (onParticleUpdate) {
        const particle3D: Particle3D = {
          id: index.toString(),
          position: particle.position.clone(),
          velocity: particle.velocity.clone(),
          life: particle.life,
          maxLife: particle.maxLife,
          size: particle.size,
          color: `#${particle.color.getHexString()}`,
          opacity: particle.opacity
        };
        onParticleUpdate(particle3D, index);
      }

      // Add particle data to arrays
      positions.push(particle.position.x, particle.position.y, particle.position.z);
      colors.push(particle.color.r, particle.color.g, particle.color.b);
      sizes.push(particle.size);
      opacities.push(particle.opacity);
    });

    // Update geometry attributes
    geometryRef.current.setAttribute('position', new Float32BufferAttribute(positions, 3));
    geometryRef.current.setAttribute('color', new Float32BufferAttribute(colors, 3));
    geometryRef.current.setAttribute('size', new Float32BufferAttribute(sizes, 1));
    geometryRef.current.setAttribute('opacity', new Float32BufferAttribute(opacities, 1));
    geometryRef.current.attributes.position.needsUpdate = true;
    geometryRef.current.attributes.color.needsUpdate = true;
    geometryRef.current.attributes.size.needsUpdate = true;
    geometryRef.current.attributes.opacity.needsUpdate = true;
  });

  // Create geometry
  const geometry = useMemo(() => {
    const geom = new BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    const sizes = new Float32Array(particleCount);
    const opacities = new Float32Array(particleCount);

    geom.setAttribute('position', new Float32BufferAttribute(positions, 3));
    geom.setAttribute('color', new Float32BufferAttribute(colors, 3));
    geom.setAttribute('size', new Float32BufferAttribute(sizes, 1));
    geom.setAttribute('opacity', new Float32BufferAttribute(opacities, 1));

    return geom;
  }, [particleCount]);

  // Custom shader material for advanced particle effects
  const particleMaterial = useMemo(() => {
    return new THREE.ShaderMaterial({
      uniforms: {
        pointTexture: { value: texture || null },
        time: { value: 0 }
      },
      vertexShader: `
        attribute float size;
        attribute float opacity;
        varying vec3 vColor;
        varying float vOpacity;
        uniform float time;

        void main() {
          vColor = color;
          vOpacity = opacity;
          
          vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
          
          // Animated size variation
          float animatedSize = size * (1.0 + sin(time * 5.0 + position.x * 10.0) * 0.1);
          
          gl_PointSize = animatedSize * (300.0 / -mvPosition.z);
          gl_Position = projectionMatrix * mvPosition;
        }
      `,
      fragmentShader: `
        uniform sampler2D pointTexture;
        varying vec3 vColor;
        varying float vOpacity;

        void main() {
          vec2 coords = gl_PointCoord;
          
          // Create circular particles if no texture
          float distance = length(coords - 0.5);
          if (distance > 0.5) discard;
          
          // Soft edges
          float alpha = 1.0 - smoothstep(0.3, 0.5, distance);
          
          // Apply texture if available
          vec4 textureColor = texture2D(pointTexture, coords);
          vec3 finalColor = vColor;
          
          if (textureColor.a > 0.0) {
            finalColor = textureColor.rgb * vColor;
            alpha *= textureColor.a;
          }
          
          gl_FragColor = vec4(finalColor, alpha * vOpacity);
        }
      `,
      blending: blending,
      depthTest: false,
      transparent: true,
      vertexColors: true
    });
  }, [texture, blending]);

  // Update time uniform
  useFrame((state) => {
    if (particleMaterial.uniforms.time) {
      particleMaterial.uniforms.time.value = state.clock.elapsedTime;
    }
  });

  return (
    <points ref={pointsRef} geometry={geometry} material={particleMaterial}>
      <bufferGeometry ref={geometryRef} attach="geometry" />
    </points>
  );
};

// Preset particle systems
export const FireworksParticles: React.FC<{ position: Vector3; trigger: boolean }> = ({ 
  position, 
  trigger 
}) => {
  return trigger ? (
    <ParticleSystem
      particleCount={200}
      position={position}
      spread={3}
      speed={5}
      life={2}
      size={0.2}
      color={['#ff6b6b', '#4ecdc4', '#45b7d1', '#feca57', '#ff9ff3']}
      gravity={new Vector3(0, -2, 0)}
      fadeOut={true}
      burst={true}
      burstCount={200}
      shape="sphere"
    />
  ) : null;
};

export const TrailParticles: React.FC<{ 
  position: Vector3; 
  velocity: Vector3; 
  active: boolean 
}> = ({ position, velocity, active }) => {
  return active ? (
    <ParticleSystem
      particleCount={50}
      position={position}
      spread={0.5}
      speed={0.5}
      life={1}
      size={0.1}
      color="#667eea"
      emissionRate={50}
      gravity={new Vector3(0, 0, 0)}
      fadeOut={true}
      shape="sphere"
      onParticleUpdate={(particle, index) => {
        // Make particles follow the trail
        particle.velocity.add(velocity.clone().multiplyScalar(0.1));
      }}
    />
  ) : null;
};

export const AmbientParticles: React.FC<{ 
  bounds: Vector3; 
  density?: number 
}> = ({ bounds, density = 0.1 }) => {
  const particleCount = Math.floor(bounds.x * bounds.y * bounds.z * density);

  return (
    <ParticleSystem
      particleCount={particleCount}
      position={new Vector3(0, 0, 0)}
      spread={Math.max(bounds.x, bounds.y, bounds.z)}
      speed={0.1}
      life={10}
      size={0.05}
      color="#ffffff"
      emissionRate={particleCount / 10}
      gravity={new Vector3(0, 0, 0)}
      turbulence={0.05}
      fadeIn={true}
      fadeOut={true}
      shape="box"
      blending={AdditiveBlending}
    />
  );
};

export const InteractionParticles: React.FC<{ 
  position: Vector3; 
  intensity: number;
  color: string;
}> = ({ position, intensity, color }) => {
  return (
    <ParticleSystem
      particleCount={Math.floor(intensity * 100)}
      position={position}
      spread={1}
      speed={2 * intensity}
      life={0.5}
      size={0.15}
      color={color}
      emissionRate={intensity * 200}
      gravity={new Vector3(0, 1, 0)}
      fadeOut={true}
      shape="sphere"
      blending={AdditiveBlending}
    />
  );
};

export default ParticleSystem;