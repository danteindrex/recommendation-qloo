import React, { useRef, useState, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text, Cylinder, Sphere, Box } from '@react-three/drei';
import { Vector3, Color } from 'three';
import * as THREE from 'three';
import { DiversityScore3D, DiversityBreakdown, InteractionState3D, CulturalCategory } from '../../types/cultural3d.types';

interface DiversityScore3DProps {
  diversityScores: DiversityScore3D[];
  onScoreClick: (score: DiversityScore3D) => void;
  onScoreHover: (score: DiversityScore3D | null) => void;
  onBreakdownClick: (breakdown: DiversityBreakdown, score: DiversityScore3D) => void;
  interactionState: InteractionState3D;
  showBreakdown?: boolean;
  animateTransitions?: boolean;
}

// Individual diversity score bar component
const DiversityBar3D: React.FC<{
  score: DiversityScore3D;
  isHovered: boolean;
  isSelected: boolean;
  showBreakdown: boolean;
  onClick: () => void;
  onHover: (hovered: boolean) => void;
  onBreakdownClick: (breakdown: DiversityBreakdown) => void;
}> = ({ score, isHovered, isSelected, showBreakdown, onClick, onHover, onBreakdownClick }) => {
  const barRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);
  const textRef = useRef<any>(null);
  
  useFrame((state) => {
    if (barRef.current) {
      // Animated height growth
      const targetHeight = score.height * score.score;
      const currentHeight = barRef.current.scale.y;
      barRef.current.scale.y = THREE.MathUtils.lerp(currentHeight, targetHeight, 0.1);
      
      // Glow effect on hover
      if (isHovered || isSelected) {
        const glowIntensity = 0.5 + Math.sin(state.clock.elapsedTime * 4) * 0.2;
        (barRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = glowIntensity;
      } else {
        (barRef.current.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.1;
      }
    }
    
    if (groupRef.current && (isHovered || isSelected)) {
      // Gentle floating animation
      groupRef.current.position.y = score.position.y + Math.sin(state.clock.elapsedTime * 2) * 0.2;
    }
    
    if (textRef.current && (isHovered || isSelected)) {
      textRef.current.lookAt(state.camera.position);
    }
  });

  const barColor = new Color(score.color);
  const maxHeight = score.height;

  return (
    <group ref={groupRef} position={score.position}>
      {/* Main diversity bar */}
      <Cylinder
        ref={barRef}
        position={[0, maxHeight / 2, 0]}
        args={[0.5, 0.5, maxHeight, 8]}
        onClick={onClick}
        onPointerOver={() => onHover(true)}
        onPointerOut={() => onHover(false)}
      >
        <meshStandardMaterial
          color={barColor}
          emissive={barColor}
          emissiveIntensity={0.1}
          metalness={0.2}
          roughness={0.3}
        />
      </Cylinder>
      
      {/* Score value indicator */}
      <Sphere
        position={[0, maxHeight * score.score + 0.3, 0]}
        args={[0.2, 16, 16]}
      >
        <meshStandardMaterial
          color={score.score > 0.7 ? '#4ade80' : score.score > 0.4 ? '#fbbf24' : '#ef4444'}
          emissive={score.score > 0.7 ? '#4ade80' : score.score > 0.4 ? '#fbbf24' : '#ef4444'}
          emissiveIntensity={0.3}
        />
      </Sphere>
      
      {/* Category label */}
      <Text
        position={[0, -0.5, 0]}
        fontSize={0.3}
        color={score.color}
        anchorX="center"
        anchorY="top"
        rotation={[-Math.PI / 2, 0, 0]}
      >
        {score.category.replace('_', ' ').toUpperCase()}
      </Text>
      
      {/* Score percentage */}
      {(isHovered || isSelected) && (
        <Text
          ref={textRef}
          position={[0, maxHeight * score.score + 1, 0]}
          fontSize={0.4}
          color={score.color}
          anchorX="center"
          anchorY="bottom"
        >
          {(score.score * 100).toFixed(1)}%
        </Text>
      )}
      
      {/* Breakdown visualization */}
      {showBreakdown && (isHovered || isSelected) && (
        <BreakdownVisualization
          breakdown={score.breakdown}
          position={new Vector3(2, 0, 0)}
          onBreakdownClick={onBreakdownClick}
        />
      )}
    </group>
  );
};

// Breakdown visualization component
const BreakdownVisualization: React.FC<{
  breakdown: DiversityBreakdown[];
  position: Vector3;
  onBreakdownClick: (breakdown: DiversityBreakdown) => void;
}> = ({ breakdown, position, onBreakdownClick }) => {
  const groupRef = useRef<THREE.Group>(null);
  
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.01;
    }
  });

  const totalValue = breakdown.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = 0;

  return (
    <group ref={groupRef} position={position}>
      {/* Breakdown title */}
      <Text
        position={[0, 2, 0]}
        fontSize={0.3}
        color="#888"
        anchorX="center"
      >
        Breakdown
      </Text>
      
      {/* Pie chart segments */}
      {breakdown.map((item, index) => {
        const segmentAngle = (item.value / totalValue) * Math.PI * 2;
        const segmentPosition = new Vector3(
          Math.cos(currentAngle + segmentAngle / 2) * 1.2,
          0,
          Math.sin(currentAngle + segmentAngle / 2) * 1.2
        );
        
        const result = (
          <group key={index}>
            {/* Segment indicator */}
            <Cylinder
              position={segmentPosition}
              args={[0.1, 0.1, item.value * 2, 8]}
              onClick={() => onBreakdownClick(item)}
            >
              <meshStandardMaterial
                color={item.color}
                emissive={item.color}
                emissiveIntensity={0.2}
              />
            </Cylinder>
            
            {/* Segment label */}
            <Text
              position={segmentPosition.clone().add(new Vector3(0, item.value + 0.5, 0))}
              fontSize={0.2}
              color={item.color}
              anchorX="center"
            >
              {item.category}
            </Text>
            
            {/* Segment value */}
            <Text
              position={segmentPosition.clone().add(new Vector3(0, -0.3, 0))}
              fontSize={0.15}
              color="#888"
              anchorX="center"
            >
              {(item.value * 100).toFixed(1)}%
            </Text>
          </group>
        );
        
        currentAngle += segmentAngle;
        return result;
      })}
    </group>
  );
};

// Comparative diversity chart
const ComparativeDiversityChart: React.FC<{
  scores: DiversityScore3D[];
  selectedCategory: CulturalCategory | null;
}> = ({ scores, selectedCategory }) => {
  const chartRef = useRef<THREE.Group>(null);
  
  useFrame(() => {
    if (chartRef.current) {
      chartRef.current.rotation.y += 0.005;
    }
  });

  const filteredScores = selectedCategory 
    ? scores.filter(s => s.category === selectedCategory)
    : scores;

  const averageScore = filteredScores.reduce((sum, s) => sum + s.score, 0) / filteredScores.length;

  return (
    <group ref={chartRef} position={[0, 8, 0]}>
      {/* Chart title */}
      <Text
        fontSize={0.6}
        color="#667eea"
        anchorX="center"
      >
        Cultural Diversity Overview
      </Text>
      
      {/* Average score indicator */}
      <Box
        position={[0, -1, 0]}
        args={[6, 0.2, 0.2]}
      >
        <meshStandardMaterial
          color="#667eea"
          transparent
          opacity={0.3}
        />
      </Box>
      
      <Box
        position={[-3 + (averageScore * 6), -1, 0]}
        args={[0.2, 0.5, 0.2]}
      >
        <meshStandardMaterial
          color="#4ade80"
          emissive="#4ade80"
          emissiveIntensity={0.3}
        />
      </Box>
      
      <Text
        position={[0, -2, 0]}
        fontSize={0.3}
        color="#888"
        anchorX="center"
      >
        Average: {(averageScore * 100).toFixed(1)}%
      </Text>
      
      {/* Category filter indicator */}
      {selectedCategory && (
        <Text
          position={[0, -2.8, 0]}
          fontSize={0.25}
          color="#667eea"
          anchorX="center"
        >
          Filtered: {selectedCategory.replace('_', ' ').toUpperCase()}
        </Text>
      )}
    </group>
  );
};

export const DiversityScore3DVisualization: React.FC<DiversityScore3DProps> = ({
  diversityScores,
  onScoreClick,
  onScoreHover,
  onBreakdownClick,
  interactionState,
  showBreakdown = true,
  animateTransitions = true
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredScore, setHoveredScore] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<CulturalCategory | null>(null);

  // Arrange scores in a circular pattern
  const arrangedScores = useMemo(() => {
    return diversityScores.map((score, index) => {
      const angle = (index / diversityScores.length) * Math.PI * 2;
      const radius = 5;
      return {
        ...score,
        position: new Vector3(
          Math.cos(angle) * radius,
          0,
          Math.sin(angle) * radius
        )
      };
    });
  }, [diversityScores]);

  // Auto-rotation
  useFrame(() => {
    if (groupRef.current && !interactionState.isDragging) {
      groupRef.current.rotation.y += 0.003;
    }
  });

  const handleScoreHover = (score: DiversityScore3D | null) => {
    setHoveredScore(score?.id || null);
    onScoreHover(score);
  };

  const handleScoreClick = (score: DiversityScore3D) => {
    onScoreClick(score);
    setSelectedCategory(score.category);
  };

  const handleBreakdownClick = (breakdown: DiversityBreakdown, score: DiversityScore3D) => {
    onBreakdownClick(breakdown, score);
  };

  return (
    <group ref={groupRef}>
      {/* Comparative chart */}
      <ComparativeDiversityChart
        scores={arrangedScores}
        selectedCategory={selectedCategory}
      />
      
      {/* Diversity score bars */}
      {arrangedScores.map((score) => (
        <DiversityBar3D
          key={score.id}
          score={score}
          isHovered={hoveredScore === score.id}
          isSelected={interactionState.selectedObject === score.id}
          showBreakdown={showBreakdown}
          onClick={() => handleScoreClick(score)}
          onHover={(hovered) => handleScoreHover(hovered ? score : null)}
          onBreakdownClick={(breakdown) => handleBreakdownClick(breakdown, score)}
        />
      ))}
      
      {/* Center platform */}
      <Cylinder
        position={[0, -0.1, 0]}
        args={[8, 8, 0.2, 32]}
      >
        <meshStandardMaterial
          color="#1a1a1a"
          transparent
          opacity={0.3}
        />
      </Cylinder>
      
      {/* Grid lines */}
      {Array.from({ length: 8 }, (_, i) => {
        const angle = (i / 8) * Math.PI * 2;
        const start = new Vector3(Math.cos(angle) * 2, 0, Math.sin(angle) * 2);
        const end = new Vector3(Math.cos(angle) * 8, 0, Math.sin(angle) * 8);
        
        return (
          <group key={i}>
            <Cylinder
              position={start.clone().lerp(end, 0.5)}
              args={[0.02, 0.02, start.distanceTo(end), 8]}
              rotation={[0, 0, Math.PI / 2]}
            >
              <meshBasicMaterial color="#333" transparent opacity={0.3} />
            </Cylinder>
          </group>
        );
      })}
      
      {/* Instructions */}
      <Text
        position={[0, -3, 0]}
        fontSize={0.25}
        color="#888"
        anchorX="center"
      >
        Click bars to drill down • Hover for details
      </Text>
    </group>
  );
};

export default DiversityScore3DVisualization;