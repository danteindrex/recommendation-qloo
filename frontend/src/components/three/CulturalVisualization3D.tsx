import React, { useState, useRef, useCallback, useMemo } from 'react';
import { Vector3 } from 'three';
import Scene3D from './Scene3D';
import CulturalEvolutionTimeline3D from './CulturalEvolutionTimeline3D';
import InfluenceNetwork3D from './InfluenceNetwork3D';
import DiversityScore3DVisualization from './DiversityScore3D';
import TrendPrediction3DChart from './TrendPrediction3D';
import ParticleSystem, { FireworksParticles, InteractionParticles } from './ParticleSystem';
import useGestures from '../../hooks/useGestures';
import {
  CulturalMilestone3D,
  InfluenceNode3D,
  InfluenceConnection3D,
  DiversityScore3D,
  TrendPrediction3D,
  TimelineControls,
  InteractionState3D,
  GestureEvent3D,
  CulturalCategory,
  SocialPlatform
} from '../../types/cultural3d.types';

interface CulturalVisualization3DProps {
  data: {
    milestones: CulturalMilestone3D[];
    influenceNodes: InfluenceNode3D[];
    influenceConnections: InfluenceConnection3D[];
    diversityScores: DiversityScore3D[];
    trendPredictions: TrendPrediction3D[];
  };
  mode: 'timeline' | 'network' | 'diversity' | 'trends' | 'overview';
  onModeChange: (mode: string) => void;
  onDataPointSelect: (dataPoint: any) => void;
  className?: string;
}

export const CulturalVisualization3D: React.FC<CulturalVisualization3DProps> = ({
  data,
  mode,
  onModeChange,
  onDataPointSelect,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [interactionState, setInteractionState] = useState<InteractionState3D>({
    hoveredObject: null,
    selectedObject: null,
    isDragging: false,
    dragStart: null,
    cameraPosition: new Vector3(10, 10, 10),
    cameraTarget: new Vector3(0, 0, 0),
    zoom: 1
  });

  const [timelineControls, setTimelineControls] = useState<TimelineControls>({
    currentTime: new Date(),
    startTime: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000), // 1 year ago
    endTime: new Date(),
    isPlaying: false,
    playbackSpeed: 1,
    scrubbing: false
  });

  const [particleEffects, setParticleEffects] = useState<{
    fireworks: { position: Vector3; active: boolean }[];
    interactions: { position: Vector3; intensity: number; color: string }[];
  }>({
    fireworks: [],
    interactions: []
  });

  // Gesture handling
  const gestureCallbacks = useMemo(() => ({
    onPinch: (scale: number, center: Vector3) => {
      setInteractionState(prev => ({
        ...prev,
        zoom: Math.max(0.1, Math.min(5, prev.zoom * scale))
      }));
    },
    onRotate: (rotation: number, center: Vector3) => {
      setInteractionState(prev => ({
        ...prev,
        cameraPosition: prev.cameraPosition.clone().applyAxisAngle(new Vector3(0, 1, 0), rotation * 0.01)
      }));
    },
    onSwipe: (direction: Vector3, velocity: number) => {
      if (velocity > 100) {
        // Switch visualization modes based on swipe direction
        const modes = ['timeline', 'network', 'diversity', 'trends', 'overview'];
        const currentIndex = modes.indexOf(mode);
        
        if (direction.x > 0.5) {
          // Swipe right - next mode
          const nextIndex = (currentIndex + 1) % modes.length;
          onModeChange(modes[nextIndex]);
        } else if (direction.x < -0.5) {
          // Swipe left - previous mode
          const prevIndex = (currentIndex - 1 + modes.length) % modes.length;
          onModeChange(modes[prevIndex]);
        }
      }
    },
    onTap: (position: Vector3) => {
      // Add interaction particle effect
      setParticleEffects(prev => ({
        ...prev,
        interactions: [
          ...prev.interactions,
          { position: position.clone(), intensity: 0.5, color: '#667eea' }
        ]
      }));
      
      // Clear after animation
      setTimeout(() => {
        setParticleEffects(prev => ({
          ...prev,
          interactions: prev.interactions.slice(1)
        }));
      }, 1000);
    },
    onDoubleTap: (position: Vector3) => {
      // Add fireworks effect
      setParticleEffects(prev => ({
        ...prev,
        fireworks: [
          ...prev.fireworks,
          { position: position.clone(), active: true }
        ]
      }));
      
      // Clear after animation
      setTimeout(() => {
        setParticleEffects(prev => ({
          ...prev,
          fireworks: prev.fireworks.slice(1)
        }));
      }, 3000);
    },
    onLongPress: (position: Vector3) => {
      // Show context menu or detailed view
      console.log('Long press at:', position);
    },
    onDrag: (delta: Vector3, position: Vector3) => {
      setInteractionState(prev => ({
        ...prev,
        isDragging: true,
        cameraTarget: prev.cameraTarget.clone().sub(delta.multiplyScalar(0.01))
      }));
    },
    onGestureEnd: () => {
      setInteractionState(prev => ({
        ...prev,
        isDragging: false,
        dragStart: null
      }));
    }
  }), [mode, onModeChange]);

  useGestures(containerRef, gestureCallbacks, {
    enablePinch: true,
    enableRotation: true,
    enableSwipe: true,
    enableTap: true,
    enableDoubleTap: true,
    enableLongPress: true,
    enableDrag: true
  });

  // Data interaction handlers
  const handleMilestoneClick = useCallback((milestone: CulturalMilestone3D) => {
    setInteractionState(prev => ({ ...prev, selectedObject: milestone.id }));
    onDataPointSelect(milestone);
    
    // Add celebration effect
    setParticleEffects(prev => ({
      ...prev,
      fireworks: [
        ...prev.fireworks,
        { position: milestone.position.clone(), active: true }
      ]
    }));
  }, [onDataPointSelect]);

  const handleMilestoneHover = useCallback((milestone: CulturalMilestone3D | null) => {
    setInteractionState(prev => ({ ...prev, hoveredObject: milestone?.id || null }));
  }, []);

  const handleNodeClick = useCallback((node: InfluenceNode3D) => {
    setInteractionState(prev => ({ ...prev, selectedObject: node.id }));
    onDataPointSelect(node);
  }, [onDataPointSelect]);

  const handleNodeHover = useCallback((node: InfluenceNode3D | null) => {
    setInteractionState(prev => ({ ...prev, hoveredObject: node?.id || null }));
  }, []);

  const handleConnectionClick = useCallback((connection: InfluenceConnection3D) => {
    onDataPointSelect(connection);
  }, [onDataPointSelect]);

  const handleScoreClick = useCallback((score: DiversityScore3D) => {
    setInteractionState(prev => ({ ...prev, selectedObject: score.id }));
    onDataPointSelect(score);
  }, [onDataPointSelect]);

  const handleScoreHover = useCallback((score: DiversityScore3D | null) => {
    setInteractionState(prev => ({ ...prev, hoveredObject: score?.id || null }));
  }, []);

  const handleBreakdownClick = useCallback((breakdown: any, score: DiversityScore3D) => {
    onDataPointSelect({ breakdown, score });
  }, [onDataPointSelect]);

  const handlePredictionClick = useCallback((prediction: TrendPrediction3D) => {
    setInteractionState(prev => ({ ...prev, selectedObject: prediction.id }));
    onDataPointSelect(prediction);
  }, [onDataPointSelect]);

  const handlePredictionHover = useCallback((prediction: TrendPrediction3D | null) => {
    setInteractionState(prev => ({ ...prev, hoveredObject: prediction?.id || null }));
  }, []);

  const handleTimelineScroll = useCallback((time: Date) => {
    setTimelineControls(prev => ({ ...prev, currentTime: time }));
  }, []);

  const handleTimeControlChange = useCallback((controls: Partial<TimelineControls>) => {
    setTimelineControls(prev => ({ ...prev, ...controls }));
  }, []);

  const handleCameraChange = useCallback((camera: any) => {
    setInteractionState(prev => ({
      ...prev,
      cameraPosition: camera.position.clone(),
      cameraTarget: new Vector3(0, 0, 0) // Assuming looking at origin
    }));
  }, []);

  // Render appropriate visualization based on mode
  const renderVisualization = () => {
    switch (mode) {
      case 'timeline':
        return (
          <CulturalEvolutionTimeline3D
            milestones={data.milestones}
            timelineControls={timelineControls}
            onMilestoneClick={handleMilestoneClick}
            onMilestoneHover={handleMilestoneHover}
            onTimelineScroll={handleTimelineScroll}
            interactionState={interactionState}
          />
        );

      case 'network':
        return (
          <InfluenceNetwork3D
            nodes={data.influenceNodes}
            connections={data.influenceConnections}
            onNodeClick={handleNodeClick}
            onNodeHover={handleNodeHover}
            onConnectionClick={handleConnectionClick}
            interactionState={interactionState}
            showLabels={true}
            animateConnections={true}
          />
        );

      case 'diversity':
        return (
          <DiversityScore3DVisualization
            diversityScores={data.diversityScores}
            onScoreClick={handleScoreClick}
            onScoreHover={handleScoreHover}
            onBreakdownClick={handleBreakdownClick}
            interactionState={interactionState}
            showBreakdown={true}
            animateTransitions={true}
          />
        );

      case 'trends':
        return (
          <TrendPrediction3DChart
            predictions={data.trendPredictions}
            timelineControls={timelineControls}
            onPredictionClick={handlePredictionClick}
            onPredictionHover={handlePredictionHover}
            onTimeControlChange={handleTimeControlChange}
            interactionState={interactionState}
            showConfidenceRegions={true}
            animateChart={true}
          />
        );

      case 'overview':
        return (
          <group>
            {/* Smaller versions of all visualizations */}
            <group position={[-10, 0, 0]} scale={[0.5, 0.5, 0.5]}>
              <CulturalEvolutionTimeline3D
                milestones={data.milestones.slice(0, 10)} // Limit for performance
                timelineControls={timelineControls}
                onMilestoneClick={handleMilestoneClick}
                onMilestoneHover={handleMilestoneHover}
                onTimelineScroll={handleTimelineScroll}
                interactionState={interactionState}
              />
            </group>
            
            <group position={[10, 0, 0]} scale={[0.5, 0.5, 0.5]}>
              <InfluenceNetwork3D
                nodes={data.influenceNodes.slice(0, 20)} // Limit for performance
                connections={data.influenceConnections.slice(0, 30)}
                onNodeClick={handleNodeClick}
                onNodeHover={handleNodeHover}
                onConnectionClick={handleConnectionClick}
                interactionState={interactionState}
                showLabels={false}
                animateConnections={false}
              />
            </group>
            
            <group position={[0, 10, 0]} scale={[0.5, 0.5, 0.5]}>
              <DiversityScore3DVisualization
                diversityScores={data.diversityScores}
                onScoreClick={handleScoreClick}
                onScoreHover={handleScoreHover}
                onBreakdownClick={handleBreakdownClick}
                interactionState={interactionState}
                showBreakdown={false}
                animateTransitions={false}
              />
            </group>
            
            <group position={[0, -10, 0]} scale={[0.5, 0.5, 0.5]}>
              <TrendPrediction3DChart
                predictions={data.trendPredictions.slice(0, 50)} // Limit for performance
                timelineControls={timelineControls}
                onPredictionClick={handlePredictionClick}
                onPredictionHover={handlePredictionHover}
                onTimeControlChange={handleTimeControlChange}
                interactionState={interactionState}
                showConfidenceRegions={false}
                animateChart={false}
              />
            </group>
          </group>
        );

      default:
        return null;
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`w-full h-full relative ${className}`}
      style={{ touchAction: 'none' }} // Prevent default touch behaviors
    >
      <Scene3D
        cameraPosition={[
          interactionState.cameraPosition.x,
          interactionState.cameraPosition.y,
          interactionState.cameraPosition.z
        ]}
        enableControls={!interactionState.isDragging}
        enableGrid={mode !== 'overview'}
        backgroundColor="#0a0a0a"
        onCameraChange={handleCameraChange}
      >
        {/* Main visualization */}
        {renderVisualization()}
        
        {/* Ambient particles */}
        <ParticleSystem
          particleCount={200}
          position={new Vector3(0, 0, 0)}
          spread={20}
          speed={0.1}
          life={10}
          size={0.02}
          color="#ffffff"
          emissionRate={20}
          gravity={new Vector3(0, 0, 0)}
          turbulence={0.02}
          fadeIn={true}
          fadeOut={true}
          shape="box"
        />
        
        {/* Interaction particle effects */}
        {particleEffects.interactions.map((effect, index) => (
          <InteractionParticles
            key={index}
            position={effect.position}
            intensity={effect.intensity}
            color={effect.color}
          />
        ))}
        
        {/* Fireworks effects */}
        {particleEffects.fireworks.map((firework, index) => (
          <FireworksParticles
            key={index}
            position={firework.position}
            trigger={firework.active}
          />
        ))}
      </Scene3D>
      
      {/* Mode indicator */}
      <div className="absolute top-4 left-4 bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg">
        <div className="text-sm font-medium capitalize">{mode} View</div>
        <div className="text-xs opacity-75">
          Swipe to change • Pinch to zoom • Tap to interact
        </div>
      </div>
      
      {/* Performance indicator */}
      <div className="absolute top-4 right-4 bg-black bg-opacity-50 text-white px-3 py-2 rounded-lg">
        <div className="text-xs">
          Objects: {
            data.milestones.length + 
            data.influenceNodes.length + 
            data.diversityScores.length + 
            data.trendPredictions.length
          }
        </div>
        <div className="text-xs opacity-75">
          Zoom: {(interactionState.zoom * 100).toFixed(0)}%
        </div>
      </div>
    </div>
  );
};

export default CulturalVisualization3D;