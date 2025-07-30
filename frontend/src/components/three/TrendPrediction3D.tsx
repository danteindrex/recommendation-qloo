import React, { useRef, useState, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text, Line, Sphere, Cylinder, Box } from '@react-three/drei';
import { Vector3, Color, CatmullRomCurve3 } from 'three';
import * as THREE from 'three';
import { TrendPrediction3D, ConfidenceRegion3D, InteractionState3D, TimelineControls } from '../../types/cultural3d.types';

interface TrendPrediction3DProps {
  predictions: TrendPrediction3D[];
  timelineControls: TimelineControls;
  onPredictionClick: (prediction: TrendPrediction3D) => void;
  onPredictionHover: (prediction: TrendPrediction3D | null) => void;
  onTimeControlChange: (controls: Partial<TimelineControls>) => void;
  interactionState: InteractionState3D;
  showConfidenceRegions?: boolean;
  animateChart?: boolean;
}

// Individual prediction point component
const PredictionPoint3D: React.FC<{
  prediction: TrendPrediction3D;
  isHovered: boolean;
  isSelected: boolean;
  showConfidence: boolean;
  onClick: () => void;
  onHover: (hovered: boolean) => void;
}> = ({ prediction, isHovered, isSelected, showConfidence, onClick, onHover }) => {
  const pointRef = useRef<THREE.Mesh>(null);
  const confidenceRef = useRef<THREE.Mesh>(null);
  const textRef = useRef<any>(null);
  
  useFrame((state) => {
    if (pointRef.current) {
      // Pulsing animation based on confidence
      const pulseScale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1 * prediction.confidence;
      const baseScale = isHovered ? 1.5 : isSelected ? 1.3 : 1;
      pointRef.current.scale.setScalar(baseScale * pulseScale);
      
      // Color intensity based on prediction value
      const material = pointRef.current.material as THREE.MeshStandardMaterial;
      material.emissiveIntensity = 0.2 + prediction.prediction * 0.3;
    }
    
    if (confidenceRef.current && showConfidence) {
      // Animate confidence region
      confidenceRef.current.rotation.y += 0.01;
      const material = confidenceRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = prediction.confidenceRegion.opacity * (isHovered ? 1.5 : 1);
    }
    
    if (textRef.current && (isHovered || isSelected)) {
      textRef.current.lookAt(state.camera.position);
    }
  });

  const predictionColor = new Color().setHSL(
    (1 - prediction.prediction) * 0.3, // Red to green based on prediction
    0.8,
    0.6
  );

  return (
    <group position={prediction.position}>
      {/* Confidence region */}
      {showConfidence && (
        <Sphere
          ref={confidenceRef}
          args={[prediction.confidenceRegion.radius, 16, 16]}
          position={prediction.confidenceRegion.center}
        >
          <meshBasicMaterial
            color={prediction.confidenceRegion.color}
            transparent
            opacity={prediction.confidenceRegion.opacity}
            wireframe
          />
        </Sphere>
      )}
      
      {/* Main prediction point */}
      <Sphere
        ref={pointRef}
        args={[0.3, 16, 16]}
        onClick={onClick}
        onPointerOver={() => onHover(true)}
        onPointerOut={() => onHover(false)}
      >
        <meshStandardMaterial
          color={predictionColor}
          emissive={predictionColor}
          emissiveIntensity={0.2}
          metalness={0.1}
          roughness={0.3}
        />
      </Sphere>
      
      {/* Prediction value indicator */}
      <Cylinder
        position={[0, prediction.prediction * 2, 0]}
        args={[0.05, 0.05, prediction.prediction * 4, 8]}
      >
        <meshStandardMaterial
          color={predictionColor}
          transparent
          opacity={0.6}
        />
      </Cylinder>
      
      {/* Prediction details */}
      {(isHovered || isSelected) && (
        <group>
          <Text
            ref={textRef}
            position={[0, 1, 0]}
            fontSize={0.3}
            color={predictionColor.getHexString()}
            anchorX="center"
            anchorY="bottom"
          >
            {prediction.category.replace('_', ' ').toUpperCase()}
          </Text>
          
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.25}
            color="#888"
            anchorX="center"
          >
            {(prediction.prediction * 100).toFixed(1)}%
          </Text>
          
          <Text
            position={[0, 0.2, 0]}
            fontSize={0.2}
            color="#666"
            anchorX="center"
          >
            Confidence: {(prediction.confidence * 100).toFixed(0)}%
          </Text>
          
          <Text
            position={[0, -0.1, 0]}
            fontSize={0.2}
            color="#666"
            anchorX="center"
          >
            {prediction.timeframe.toLocaleDateString()}
          </Text>
        </group>
      )}
    </group>
  );
};

// Trend line component
const TrendLine3D: React.FC<{
  predictions: TrendPrediction3D[];
  category: string;
  color: string;
  animated: boolean;
}> = ({ predictions, category, color, animated }) => {
  const lineRef = useRef<any>(null);
  const [animationProgress, setAnimationProgress] = useState(0);
  
  useFrame((state) => {
    if (animated && lineRef.current) {
      setAnimationProgress((state.clock.elapsedTime * 0.5) % 1);
    }
  });

  const sortedPredictions = useMemo(() => {
    return predictions
      .filter(p => p.category === category)
      .sort((a, b) => a.timeframe.getTime() - b.timeframe.getTime());
  }, [predictions, category]);

  const trendPoints = useMemo(() => {
    return sortedPredictions.map(p => p.position);
  }, [sortedPredictions]);

  if (trendPoints.length < 2) return null;

  // Create smooth curve
  const curve = new CatmullRomCurve3(trendPoints);
  const curvePoints = curve.getPoints(50);

  // Animate line drawing
  const visiblePoints = animated 
    ? curvePoints.slice(0, Math.floor(curvePoints.length * animationProgress))
    : curvePoints;

  return (
    <Line
      ref={lineRef}
      points={visiblePoints}
      color={color}
      lineWidth={3}
      transparent
      opacity={0.8}
    />
  );
};

// Time control interface
const TimeControls3D: React.FC<{
  timelineControls: TimelineControls;
  onControlChange: (controls: Partial<TimelineControls>) => void;
  predictions: TrendPrediction3D[];
}> = ({ timelineControls, onControlChange, predictions }) => {
  const controlsRef = useRef<THREE.Group>(null);
  
  const timeRange = useMemo(() => {
    const times = predictions.map(p => p.timeframe.getTime());
    return {
      min: Math.min(...times),
      max: Math.max(...times)
    };
  }, [predictions]);

  const currentProgress = useMemo(() => {
    const total = timeRange.max - timeRange.min;
    const current = timelineControls.currentTime.getTime() - timeRange.min;
    return Math.max(0, Math.min(1, current / total));
  }, [timelineControls.currentTime, timeRange]);

  useFrame(() => {
    if (controlsRef.current) {
      controlsRef.current.lookAt(0, 0, 0);
    }
  });

  return (
    <group ref={controlsRef} position={[0, -8, 0]}>
      {/* Time slider track */}
      <Box
        position={[0, 0, 0]}
        args={[10, 0.1, 0.1]}
      >
        <meshStandardMaterial color="#333" />
      </Box>
      
      {/* Progress indicator */}
      <Box
        position={[-5 + currentProgress * 10, 0, 0]}
        args={[0.2, 0.3, 0.2]}
      >
        <meshStandardMaterial
          color="#667eea"
          emissive="#667eea"
          emissiveIntensity={0.3}
        />
      </Box>
      
      {/* Play/pause button */}
      <Sphere
        position={[-6, 0, 0]}
        args={[0.3, 16, 16]}
        onClick={() => onControlChange({ isPlaying: !timelineControls.isPlaying })}
      >
        <meshStandardMaterial
          color={timelineControls.isPlaying ? "#ef4444" : "#4ade80"}
          emissive={timelineControls.isPlaying ? "#ef4444" : "#4ade80"}
          emissiveIntensity={0.3}
        />
      </Sphere>
      
      {/* Speed controls */}
      <Text
        position={[-6, -1, 0]}
        fontSize={0.2}
        color="#888"
        anchorX="center"
      >
        {timelineControls.isPlaying ? "⏸" : "▶"} {timelineControls.playbackSpeed}x
      </Text>
      
      {/* Time labels */}
      <Text
        position={[-5, -0.8, 0]}
        fontSize={0.2}
        color="#666"
        anchorX="left"
      >
        {new Date(timeRange.min).toLocaleDateString()}
      </Text>
      
      <Text
        position={[5, -0.8, 0]}
        fontSize={0.2}
        color="#666"
        anchorX="right"
      >
        {new Date(timeRange.max).toLocaleDateString()}
      </Text>
      
      <Text
        position={[0, -0.8, 0]}
        fontSize={0.25}
        color="#667eea"
        anchorX="center"
      >
        {timelineControls.currentTime.toLocaleDateString()}
      </Text>
    </group>
  );
};

// Prediction accuracy indicator
const AccuracyIndicator3D: React.FC<{
  predictions: TrendPrediction3D[];
  currentTime: Date;
}> = ({ predictions, currentTime }) => {
  const accuracyRef = useRef<THREE.Group>(null);
  
  const accuracy = useMemo(() => {
    const pastPredictions = predictions.filter(p => p.timeframe <= currentTime);
    if (pastPredictions.length === 0) return 0;
    
    const totalAccuracy = pastPredictions.reduce((sum, p) => sum + p.confidence, 0);
    return totalAccuracy / pastPredictions.length;
  }, [predictions, currentTime]);

  useFrame(() => {
    if (accuracyRef.current) {
      accuracyRef.current.rotation.z += 0.01;
    }
  });

  const accuracyColor = accuracy > 0.7 ? '#4ade80' : accuracy > 0.4 ? '#fbbf24' : '#ef4444';

  return (
    <group ref={accuracyRef} position={[8, 5, 0]}>
      {/* Accuracy ring */}
      <Cylinder
        args={[1.2, 1.2, 0.1, 32]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <meshBasicMaterial color="#333" transparent opacity={0.3} />
      </Cylinder>
      
      <Cylinder
        args={[1, 1, 0.15, 32, 1, false, 0, accuracy * Math.PI * 2]}
        rotation={[Math.PI / 2, 0, 0]}
      >
        <meshStandardMaterial
          color={accuracyColor}
          emissive={accuracyColor}
          emissiveIntensity={0.3}
        />
      </Cylinder>
      
      {/* Accuracy text */}
      <Text
        fontSize={0.4}
        color={accuracyColor}
        anchorX="center"
        anchorY="center"
      >
        {(accuracy * 100).toFixed(0)}%
      </Text>
      
      <Text
        position={[0, -0.8, 0]}
        fontSize={0.2}
        color="#888"
        anchorX="center"
      >
        Accuracy
      </Text>
    </group>
  );
};

export const TrendPrediction3DChart: React.FC<TrendPrediction3DProps> = ({
  predictions,
  timelineControls,
  onPredictionClick,
  onPredictionHover,
  onTimeControlChange,
  interactionState,
  showConfidenceRegions = true,
  animateChart = true
}) => {
  const chartRef = useRef<THREE.Group>(null);
  const [hoveredPrediction, setHoveredPrediction] = useState<string | null>(null);
  
  // Group predictions by category for trend lines
  const categorizedPredictions = useMemo(() => {
    const categories = new Map<string, TrendPrediction3D[]>();
    predictions.forEach(p => {
      if (!categories.has(p.category)) {
        categories.set(p.category, []);
      }
      categories.get(p.category)!.push(p);
    });
    return categories;
  }, [predictions]);

  // Filter predictions based on current time
  const visiblePredictions = useMemo(() => {
    return predictions.filter(p => p.timeframe <= timelineControls.currentTime);
  }, [predictions, timelineControls.currentTime]);

  // Auto-rotation
  useFrame(() => {
    if (chartRef.current && !interactionState.isDragging) {
      chartRef.current.rotation.y += 0.002;
    }
  });

  const handlePredictionHover = (prediction: TrendPrediction3D | null) => {
    setHoveredPrediction(prediction?.id || null);
    onPredictionHover(prediction);
  };

  const categoryColors = [
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
    '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43'
  ];

  return (
    <group ref={chartRef}>
      {/* Chart title */}
      <Text
        position={[0, 10, 0]}
        fontSize={0.8}
        color="#667eea"
        anchorX="center"
      >
        Cultural Trend Predictions
      </Text>
      
      {/* Trend lines */}
      {Array.from(categorizedPredictions.entries()).map(([category, categoryPredictions], index) => (
        <TrendLine3D
          key={category}
          predictions={categoryPredictions}
          category={category}
          color={categoryColors[index % categoryColors.length]}
          animated={animateChart}
        />
      ))}
      
      {/* Prediction points */}
      {visiblePredictions.map((prediction) => (
        <PredictionPoint3D
          key={prediction.id}
          prediction={prediction}
          isHovered={hoveredPrediction === prediction.id}
          isSelected={interactionState.selectedObject === prediction.id}
          showConfidence={showConfidenceRegions}
          onClick={() => onPredictionClick(prediction)}
          onHover={(hovered) => handlePredictionHover(hovered ? prediction : null)}
        />
      ))}
      
      {/* Time controls */}
      <TimeControls3D
        timelineControls={timelineControls}
        onControlChange={onTimeControlChange}
        predictions={predictions}
      />
      
      {/* Accuracy indicator */}
      <AccuracyIndicator3D
        predictions={predictions}
        currentTime={timelineControls.currentTime}
      />
      
      {/* Legend */}
      <group position={[-10, 5, 0]}>
        <Text
          fontSize={0.4}
          color="#888"
          anchorX="left"
        >
          Categories
        </Text>
        {Array.from(categorizedPredictions.keys()).map((category, index) => (
          <group key={category} position={[0, -0.8 * (index + 1), 0]}>
            <Sphere args={[0.1, 8, 8]}>
              <meshStandardMaterial color={categoryColors[index % categoryColors.length]} />
            </Sphere>
            <Text
              position={[0.3, 0, 0]}
              fontSize={0.25}
              color="#666"
              anchorX="left"
            >
              {category.replace('_', ' ').toUpperCase()}
            </Text>
          </group>
        ))}
      </group>
    </group>
  );
};

export default TrendPrediction3DChart;