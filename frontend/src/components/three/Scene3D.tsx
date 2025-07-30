import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Grid } from '@react-three/drei';
import { Vector3 } from 'three';
import * as THREE from 'three';

interface Scene3DProps {
  children: React.ReactNode;
  cameraPosition?: [number, number, number];
  enableControls?: boolean;
  enableGrid?: boolean;
  backgroundColor?: string;
  onCameraChange?: (camera: THREE.Camera) => void;
}

// Scene manager component
const SceneManager: React.FC<{ onCameraChange?: (camera: THREE.Camera) => void }> = ({ onCameraChange }) => {
  const { camera } = useThree();
  const controlsRef = useRef<any>();

  useFrame(() => {
    if (onCameraChange) {
      onCameraChange(camera);
    }
  });

  return (
    <OrbitControls
      ref={controlsRef}
      enablePan={true}
      enableZoom={true}
      enableRotate={true}
      minDistance={5}
      maxDistance={50}
      minPolarAngle={0}
      maxPolarAngle={Math.PI}
      dampingFactor={0.05}
      enableDamping={true}
    />
  );
};

// Loading fallback component
const Scene3DFallback: React.FC = () => (
  <mesh>
    <boxGeometry args={[1, 1, 1]} />
    <meshStandardMaterial color="#667eea" />
  </mesh>
);

export const Scene3D: React.FC<Scene3DProps> = ({
  children,
  cameraPosition = [10, 10, 10],
  enableControls = true,
  enableGrid = true,
  backgroundColor = '#0a0a0a',
  onCameraChange
}) => {
  return (
    <div className="w-full h-full">
      <Canvas
        shadows
        camera={{ position: cameraPosition, fov: 75 }}
        style={{ background: backgroundColor }}
        gl={{ 
          antialias: true, 
          alpha: true,
          powerPreference: "high-performance"
        }}
      >
        <Suspense fallback={<Scene3DFallback />}>
          {/* Lighting setup */}
          <ambientLight intensity={0.4} />
          <directionalLight
            position={[10, 10, 5]}
            intensity={1}
            castShadow
            shadow-mapSize-width={2048}
            shadow-mapSize-height={2048}
          />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          
          {/* Environment and atmosphere */}
          <Environment preset="city" />
          <fog attach="fog" args={[backgroundColor, 20, 100]} />
          
          {/* Grid helper */}
          {enableGrid && (
            <Grid
              args={[20, 20]}
              cellSize={1}
              cellThickness={0.5}
              cellColor="#333"
              sectionSize={5}
              sectionThickness={1}
              sectionColor="#555"
              fadeDistance={30}
              fadeStrength={1}
              followCamera={false}
              infiniteGrid={true}
            />
          )}
          
          {/* Camera controls */}
          {enableControls && <SceneManager onCameraChange={onCameraChange} />}
          
          {/* Scene content */}
          {children}
        </Suspense>
      </Canvas>
    </div>
  );
};

export default Scene3D;