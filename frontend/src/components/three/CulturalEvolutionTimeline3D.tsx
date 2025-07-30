import React, { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text, Line, Sphere } from '@react-three/drei';
import { Vector3, Color, BufferGeometry, Float32BufferAttribute } from 'three';
import * as THREE from 'three';
import { CulturalMilestone3D, TimelineControls, InteractionState3D } from '../../types/cultural3d.types';

interface CulturalEvolutionTimeline3DProps {
  milestones: CulturalMilestone3D[];
  timelineControls: TimelineControls;
  onMilestoneClick: (milestone: CulturalMilestone3D) => void;
  onMilestoneHover: (milestone: CulturalMilestone3D | null) => void;
  onTimelineScroll: (time: Date) => void;
  interactionState: InteractionState3D;
}

// Individual milestone component
const Milestone3D: React.FC<{
  milestone: CulturalMilestone3D;
  isHovered: boolean;
  isSelected: boolean;
  onClick: () => void;
  onHover: (hovered: boolean) => void;
}> = ({ milestone, isHovered, isSelected, onClick, onHover }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const textRef = useRef<any>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      // Gentle floating animation
      meshRef.current.position.y = milestone.position.y + Math.sin(state.clock.elapsedTime * 2) * 0.1;
      
      // Scale animation on hover
      const targetScale = isHovered ? 1.5 : isSelected ? 1.3 : 1;
      meshRef.current.scale.lerp(new Vector3(targetScale, targetScale, targetScale), 0.1);
      
      // Rotation animation
      meshRef.current.rotation.y += 0.01;
    }
    
    if (textRef.current && (isHovered || isSelected)) {
      textRef.current.lookAt(state.camera.position);
    }
  });

  const milestoneColor = new Color(milestone.color);
  const glowIntensity = isHovered ? 2 : isSelected ? 1.5 : 1;

  return (
    <group position={milestone.position}>
      {/* Main milestone sphere */}
      <Sphere
        ref={meshRef}
        args={[milestone.size, 32, 32]}
        onClick={onClick}
        onPointerOver={() => onHover(true)}
        onPointerOut={() => onHover(false)}
      >
        <meshStandardMaterial
          color={milestoneColor}
          emissive={milestoneColor}
          emissiveIntensity={0.2 * glowIntensity}
          transparent
          opacity={0.8}
        />
      </Sphere>
      
      {/* Glow effect */}
      <Sphere args={[milestone.size * 1.2, 16, 16]}>
        <meshBasicMaterial
          color={milestoneColor}
          transparent
          opacity={0.1 * glowIntensity}
        />
      </Sphere>
      
      {/* Milestone label */}
      {(isHovered || isSelected) && (
        <Text
          ref={textRef}
          position={[0, milestone.size + 1, 0]}
          fontSize={0.5}
          color={milestone.color}
          anchorX="center"
          anchorY="bottom"
        >
          {milestone.event}
        </Text>
      )}
      
      {/* Confidence indicator */}
      <Sphere
        position={[0, -milestone.size - 0.3, 0]}
        args={[0.1 * milestone.confidence, 8, 8]}
      >
        <meshBasicMaterial
          color={milestone.confidence > 0.7 ? '#4ade80' : milestone.confidence > 0.4 ? '#fbbf24' : '#ef4444'}
        />
      </Sphere>
    </group>
  );
};

// Timeline path component
const TimelinePath: React.FC<{ milestones: CulturalMilestone3D[] }> = ({ milestones }) => {
  const pathPoints = useMemo(() => {
    return milestones
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .map(m => m.position);
  }, [milestones]);

  if (pathPoints.length < 2) return null;

  return (
    <Line
      points={pathPoints}
      color="#667eea"
      lineWidth={2}
      transparent
      opacity={0.6}
    />
  );
};

// Timeline scrubber component
const TimelineScrubber: React.FC<{
  timelineControls: TimelineControls;
  onTimeChange: (time: Date) => void;
  milestones: CulturalMilestone3D[];
}> = ({ timelineControls, onTimeChange, milestones }) => {
  const scrubberRef = useRef<THREE.Mesh>(null);
  const [isDragging, setIsDragging] = useState(false);
  const { raycaster, mouse, camera } = useThree();

  const timelineStart = useMemo(() => {
    return milestones.reduce((min, m) => m.timestamp < min ? m.timestamp : min, new Date());
  }, [milestones]);

  const timelineEnd = useMemo(() => {
    return milestones.reduce((max, m) => m.timestamp > max ? m.timestamp : max, new Date());
  }, [milestones]);

  const currentProgress = useMemo(() => {
    const total = timelineEnd.getTime() - timelineStart.getTime();
    const current = timelineControls.currentTime.getTime() - timelineStart.getTime();
    return Math.max(0, Math.min(1, current / total));
  }, [timelineControls.currentTime, timelineStart, timelineEnd]);

  const scrubberPosition = useMemo(() => {
    const startPos = new Vector3(-10, -5, 0);
    const endPos = new Vector3(10, -5, 0);
    return startPos.lerp(endPos, currentProgress);
  }, [currentProgress]);

  useFrame(() => {
    if (scrubberRef.current && !isDragging) {
      scrubberRef.current.position.copy(scrubberPosition);
    }
  });

  const handleScrubberDrag = (event: any) => {
    if (!isDragging) return;
    
    // Calculate new time based on mouse position
    const progress = Math.max(0, Math.min(1, (event.point.x + 10) / 20));
    const newTime = new Date(timelineStart.getTime() + progress * (timelineEnd.getTime() - timelineStart.getTime()));
    onTimeChange(newTime);
  };

  return (
    <group>
      {/* Timeline track */}
      <Line
        points={[[-10, -5, 0], [10, -5, 0]]}
        color="#333"
        lineWidth={4}
      />
      
      {/* Progress line */}
      <Line
        points={[[-10, -5, 0], [scrubberPosition.x, -5, 0]]}
        color="#667eea"
        lineWidth={4}
      />
      
      {/* Scrubber handle */}
      <Sphere
        ref={scrubberRef}
        args={[0.3, 16, 16]}
        position={scrubberPosition}
        onPointerDown={() => setIsDragging(true)}
        onPointerUp={() => setIsDragging(false)}
        onPointerMove={handleScrubberDrag}
      >
        <meshStandardMaterial color="#667eea" emissive="#667eea" emissiveIntensity={0.3} />
      </Sphere>
      
      {/* Time labels */}
      <Text
        position={[-10, -6, 0]}
        fontSize={0.3}
        color="#888"
        anchorX="center"
      >
        {timelineStart.toLocaleDateString()}
      </Text>
      <Text
        position={[10, -6, 0]}
        fontSize={0.3}
        color="#888"
        anchorX="center"
      >
        {timelineEnd.toLocaleDateString()}
      </Text>
      <Text
        position={[0, -6, 0]}
        fontSize={0.3}
        color="#667eea"
        anchorX="center"
      >
        {timelineControls.currentTime.toLocaleDateString()}
      </Text>
    </group>
  );
};

export const CulturalEvolutionTimeline3D: React.FC<CulturalEvolutionTimeline3DProps> = ({
  milestones,
  timelineControls,
  onMilestoneClick,
  onMilestoneHover,
  onTimelineScroll,
  interactionState
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredMilestone, setHoveredMilestone] = useState<string | null>(null);

  // Filter milestones based on current time
  const visibleMilestones = useMemo(() => {
    return milestones.filter(m => m.timestamp <= timelineControls.currentTime);
  }, [milestones, timelineControls.currentTime]);

  // Auto-rotation when playing
  useFrame(() => {
    if (groupRef.current && timelineControls.isPlaying) {
      groupRef.current.rotation.y += 0.005 * timelineControls.playbackSpeed;
    }
  });

  const handleMilestoneHover = (milestone: CulturalMilestone3D | null) => {
    setHoveredMilestone(milestone?.id || null);
    onMilestoneHover(milestone);
  };

  return (
    <group ref={groupRef}>
      {/* Timeline path */}
      <TimelinePath milestones={visibleMilestones} />
      
      {/* Milestones */}
      {visibleMilestones.map((milestone) => (
        <Milestone3D
          key={milestone.id}
          milestone={milestone}
          isHovered={hoveredMilestone === milestone.id}
          isSelected={interactionState.selectedObject === milestone.id}
          onClick={() => onMilestoneClick(milestone)}
          onHover={(hovered) => handleMilestoneHover(hovered ? milestone : null)}
        />
      ))}
      
      {/* Timeline scrubber */}
      <TimelineScrubber
        timelineControls={timelineControls}
        onTimeChange={onTimelineScroll}
        milestones={milestones}
      />
      
      {/* Playback controls indicator */}
      {timelineControls.isPlaying && (
        <Text
          position={[0, 8, 0]}
          fontSize={0.8}
          color="#4ade80"
          anchorX="center"
        >
          ▶ Playing {timelineControls.playbackSpeed}x
        </Text>
      )}
    </group>
  );
};

export default CulturalEvolutionTimeline3D;