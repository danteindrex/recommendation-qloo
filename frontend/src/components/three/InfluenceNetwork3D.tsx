import React, { useRef, useState, useEffect, useMemo } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { Text, Line, Sphere, Cylinder } from '@react-three/drei';
import { Vector3, Color, MathUtils } from 'three';
import * as THREE from 'three';
import { InfluenceNode3D, InfluenceConnection3D, InteractionState3D } from '../../types/cultural3d.types';

interface InfluenceNetwork3DProps {
  nodes: InfluenceNode3D[];
  connections: InfluenceConnection3D[];
  onNodeClick: (node: InfluenceNode3D) => void;
  onNodeHover: (node: InfluenceNode3D | null) => void;
  onConnectionClick: (connection: InfluenceConnection3D) => void;
  interactionState: InteractionState3D;
  showLabels?: boolean;
  animateConnections?: boolean;
}

// Individual network node component
const NetworkNode3D: React.FC<{
  node: InfluenceNode3D;
  isHovered: boolean;
  isSelected: boolean;
  isConnected: boolean;
  onClick: () => void;
  onHover: (hovered: boolean) => void;
}> = ({ node, isHovered, isSelected, isConnected, onClick, onHover }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);
  const textRef = useRef<any>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      // Pulsing animation based on influence
      const pulseScale = 1 + Math.sin(state.clock.elapsedTime * 3) * 0.1 * node.influence;
      const baseScale = isHovered ? 1.5 : isSelected ? 1.3 : isConnected ? 1.2 : 1;
      meshRef.current.scale.setScalar(baseScale * pulseScale);
      
      // Gentle rotation
      meshRef.current.rotation.y += 0.01 * node.influence;
    }
    
    if (glowRef.current) {
      // Glow intensity based on state
      const glowIntensity = isHovered ? 0.8 : isSelected ? 0.6 : isConnected ? 0.4 : 0.2;
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = glowIntensity;
    }
    
    if (textRef.current && (isHovered || isSelected)) {
      textRef.current.lookAt(state.camera.position);
    }
  });

  const nodeColor = new Color(node.color);
  const influenceHeight = node.influence * 2;

  return (
    <group position={node.position}>
      {/* Main node sphere */}
      <Sphere
        ref={meshRef}
        args={[node.size, 32, 32]}
        onClick={onClick}
        onPointerOver={() => onHover(true)}
        onPointerOut={() => onHover(false)}
      >
        <meshStandardMaterial
          color={nodeColor}
          emissive={nodeColor}
          emissiveIntensity={0.3}
          metalness={0.1}
          roughness={0.2}
        />
      </Sphere>
      
      {/* Glow effect */}
      <Sphere ref={glowRef} args={[node.size * 1.5, 16, 16]}>
        <meshBasicMaterial
          color={nodeColor}
          transparent
          opacity={0.2}
        />
      </Sphere>
      
      {/* Influence indicator (vertical bar) */}
      <Cylinder
        position={[0, influenceHeight / 2, 0]}
        args={[0.1, 0.1, influenceHeight, 8]}
      >
        <meshStandardMaterial
          color={nodeColor}
          transparent
          opacity={0.6}
        />
      </Cylinder>
      
      {/* Node label */}
      {(isHovered || isSelected) && (
        <Text
          ref={textRef}
          position={[0, node.size + 1, 0]}
          fontSize={0.4}
          color={node.color}
          anchorX="center"
          anchorY="bottom"
        >
          {node.source}
        </Text>
      )}
      
      {/* Influence value */}
      {(isHovered || isSelected) && (
        <Text
          position={[0, -node.size - 0.5, 0]}
          fontSize={0.3}
          color="#888"
          anchorX="center"
          anchorY="top"
        >
          {(node.influence * 100).toFixed(1)}%
        </Text>
      )}
    </group>
  );
};

// Network connection component
const NetworkConnection3D: React.FC<{
  connection: InfluenceConnection3D;
  fromNode: InfluenceNode3D;
  toNode: InfluenceNode3D;
  isHighlighted: boolean;
  onClick: () => void;
}> = ({ connection, fromNode, toNode, isHighlighted, onClick }) => {
  const lineRef = useRef<any>(null);
  const [animationOffset, setAnimationOffset] = useState(0);
  
  useFrame((state) => {
    if (connection.animated && lineRef.current) {
      setAnimationOffset(state.clock.elapsedTime * 2);
    }
  });

  const connectionPoints = useMemo(() => {
    const start = fromNode.position.clone();
    const end = toNode.position.clone();
    const mid = start.clone().lerp(end, 0.5);
    mid.y += 1; // Arc the connection
    return [start, mid, end];
  }, [fromNode.position, toNode.position]);

  const connectionColor = isHighlighted ? '#4ade80' : connection.color;
  const lineWidth = isHighlighted ? 4 : 2 * connection.strength;

  return (
    <group>
      {/* Main connection line */}
      <Line
        ref={lineRef}
        points={connectionPoints}
        color={connectionColor}
        lineWidth={lineWidth}
        transparent
        opacity={0.7}
        onClick={onClick}
      />
      
      {/* Animated flow particles */}
      {connection.animated && (
        <Sphere
          position={connectionPoints[1].clone().add(
            new Vector3(
              Math.sin(animationOffset) * 0.5,
              Math.cos(animationOffset) * 0.3,
              0
            )
          )}
          args={[0.1, 8, 8]}
        >
          <meshBasicMaterial color={connectionColor} />
        </Sphere>
      )}
      
      {/* Connection strength indicator */}
      {isHighlighted && (
        <Text
          position={connectionPoints[1]}
          fontSize={0.2}
          color={connectionColor}
          anchorX="center"
          anchorY="center"
        >
          {(connection.strength * 100).toFixed(0)}%
        </Text>
      )}
    </group>
  );
};

// Force-directed layout simulation
const useForceLayout = (nodes: InfluenceNode3D[], connections: InfluenceConnection3D[]) => {
  const [positions, setPositions] = useState<Map<string, Vector3>>(new Map());
  
  useEffect(() => {
    const nodeMap = new Map(nodes.map(n => [n.id, n]));
    const newPositions = new Map<string, Vector3>();
    
    // Initialize positions if not set
    nodes.forEach(node => {
      if (!positions.has(node.id)) {
        newPositions.set(node.id, new Vector3(
          (Math.random() - 0.5) * 20,
          (Math.random() - 0.5) * 10,
          (Math.random() - 0.5) * 20
        ));
      } else {
        newPositions.set(node.id, positions.get(node.id)!.clone());
      }
    });
    
    // Simple force simulation
    for (let i = 0; i < 50; i++) {
      nodes.forEach(node => {
        const pos = newPositions.get(node.id)!;
        const force = new Vector3();
        
        // Repulsion from other nodes
        nodes.forEach(other => {
          if (other.id !== node.id) {
            const otherPos = newPositions.get(other.id)!;
            const diff = pos.clone().sub(otherPos);
            const distance = Math.max(diff.length(), 0.1);
            force.add(diff.normalize().multiplyScalar(10 / (distance * distance)));
          }
        });
        
        // Attraction to connected nodes
        connections.forEach(conn => {
          if (conn.from === node.id) {
            const targetPos = newPositions.get(conn.to)!;
            const diff = targetPos.clone().sub(pos);
            force.add(diff.multiplyScalar(0.1 * conn.strength));
          } else if (conn.to === node.id) {
            const targetPos = newPositions.get(conn.from)!;
            const diff = targetPos.clone().sub(pos);
            force.add(diff.multiplyScalar(0.1 * conn.strength));
          }
        });
        
        // Apply force
        pos.add(force.multiplyScalar(0.01));
        
        // Damping
        pos.multiplyScalar(0.99);
      });
    }
    
    setPositions(newPositions);
  }, [nodes, connections]);
  
  return positions;
};

export const InfluenceNetwork3D: React.FC<InfluenceNetwork3DProps> = ({
  nodes,
  connections,
  onNodeClick,
  onNodeHover,
  onConnectionClick,
  interactionState,
  showLabels = true,
  animateConnections = true
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [selectedConnections, setSelectedConnections] = useState<Set<string>>(new Set());
  
  // Use force-directed layout for positioning
  const layoutPositions = useForceLayout(nodes, connections);
  
  // Update node positions from layout
  const layoutNodes = useMemo(() => {
    return nodes.map(node => ({
      ...node,
      position: layoutPositions.get(node.id) || node.position
    }));
  }, [nodes, layoutPositions]);

  // Get connected nodes for highlighting
  const getConnectedNodes = (nodeId: string): Set<string> => {
    const connected = new Set<string>();
    connections.forEach(conn => {
      if (conn.from === nodeId) connected.add(conn.to);
      if (conn.to === nodeId) connected.add(conn.from);
    });
    return connected;
  };

  const connectedNodes = useMemo(() => {
    return hoveredNode ? getConnectedNodes(hoveredNode) : new Set<string>();
  }, [hoveredNode, connections]);

  // Auto-rotation
  useFrame(() => {
    if (groupRef.current && !interactionState.isDragging) {
      groupRef.current.rotation.y += 0.002;
    }
  });

  const handleNodeHover = (node: InfluenceNode3D | null) => {
    setHoveredNode(node?.id || null);
    onNodeHover(node);
    
    if (node) {
      // Highlight connected nodes and connections
      const connected = getConnectedNodes(node.id);
      const connectedConnectionIds = connections
        .filter(conn => conn.from === node.id || conn.to === node.id)
        .map(conn => conn.id);
      setSelectedConnections(new Set(connectedConnectionIds));
    } else {
      setSelectedConnections(new Set());
    }
  };

  const handleNodeClick = (node: InfluenceNode3D) => {
    onNodeClick(node);
    // Focus camera on selected node
    if (groupRef.current) {
      const targetPosition = node.position.clone().add(new Vector3(5, 5, 5));
      // Camera animation would be handled by parent component
    }
  };

  return (
    <group ref={groupRef}>
      {/* Network nodes */}
      {layoutNodes.map((node) => (
        <NetworkNode3D
          key={node.id}
          node={node}
          isHovered={hoveredNode === node.id}
          isSelected={interactionState.selectedObject === node.id}
          isConnected={connectedNodes.has(node.id)}
          onClick={() => handleNodeClick(node)}
          onHover={(hovered) => handleNodeHover(hovered ? node : null)}
        />
      ))}
      
      {/* Network connections */}
      {connections.map((connection) => {
        const fromNode = layoutNodes.find(n => n.id === connection.from);
        const toNode = layoutNodes.find(n => n.id === connection.to);
        
        if (!fromNode || !toNode) return null;
        
        return (
          <NetworkConnection3D
            key={connection.id}
            connection={{
              ...connection,
              animated: animateConnections && connection.animated
            }}
            fromNode={fromNode}
            toNode={toNode}
            isHighlighted={selectedConnections.has(connection.id)}
            onClick={() => onConnectionClick(connection)}
          />
        );
      })}
      
      {/* Network statistics */}
      {showLabels && (
        <group position={[0, 10, 0]}>
          <Text
            fontSize={0.6}
            color="#667eea"
            anchorX="center"
          >
            Influence Network
          </Text>
          <Text
            position={[0, -1, 0]}
            fontSize={0.3}
            color="#888"
            anchorX="center"
          >
            {nodes.length} nodes • {connections.length} connections
          </Text>
        </group>
      )}
    </group>
  );
};

export default InfluenceNetwork3D;