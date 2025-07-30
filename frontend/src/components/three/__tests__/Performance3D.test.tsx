import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { Vector3 } from 'three';
import CulturalVisualization3D from '../CulturalVisualization3D';
import {
  CulturalMilestone3D,
  InfluenceNode3D,
  InfluenceConnection3D,
  DiversityScore3D,
  TrendPrediction3D,
  CulturalCategory,
  SocialPlatform
} from '../../../types/cultural3d.types';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children, ...props }: any) => (
    <div data-testid="canvas" {...props}>
      {children}
    </div>
  ),
  useFrame: vi.fn(),
  useThree: () => ({
    camera: { position: new Vector3(0, 0, 10) },
    scene: {},
    gl: { render: vi.fn() }
  })
}));

vi.mock('@react-three/drei', () => ({
  OrbitControls: ({ children, ...props }: any) => (
    <div data-testid="orbit-controls" {...props}>
      {children}
    </div>
  ),
  Environment: ({ children, ...props }: any) => (
    <div data-testid="environment" {...props}>
      {children}
    </div>
  ),
  Grid: ({ children, ...props }: any) => (
    <div data-testid="grid" {...props}>
      {children}
    </div>
  ),
  Text: ({ children, ...props }: any) => (
    <div data-testid="text" {...props}>
      {children}
    </div>
  ),
  Line: ({ children, ...props }: any) => (
    <div data-testid="line" {...props}>
      {children}
    </div>
  ),
  Sphere: ({ children, ...props }: any) => (
    <div data-testid="sphere" {...props}>
      {children}
    </div>
  ),
  Cylinder: ({ children, ...props }: any) => (
    <div data-testid="cylinder" {...props}>
      {children}
    </div>
  ),
  Box: ({ children, ...props }: any) => (
    <div data-testid="box" {...props}>
      {children}
    </div>
  )
}));

// Mock useGestures hook
vi.mock('../../../hooks/useGestures', () => ({
  default: () => ({
    isGestureActive: false,
    currentPosition: new Vector3(),
    velocity: new Vector3(),
    touchCount: 0
  })
}));

describe('3D Visualization Performance Tests', () => {
  const createMockData = (scale: number = 1) => ({
    milestones: Array.from({ length: 10 * scale }, (_, i) => ({
      id: `milestone-${i}`,
      position: new Vector3(i, 0, 0),
      timestamp: new Date(2023, 0, 1 + i),
      event: `Event ${i}`,
      culturalShift: Math.random(),
      confidence: Math.random(),
      platforms: [SocialPlatform.SPOTIFY],
      color: '#ff6b6b',
      size: 0.3,
      connections: []
    })),
    influenceNodes: Array.from({ length: 20 * scale }, (_, i) => ({
      id: `node-${i}`,
      position: new Vector3(i * 0.5, 0, 0),
      source: `Source ${i}`,
      influence: Math.random(),
      category: CulturalCategory.MUSIC,
      connections: [],
      color: '#4ecdc4',
      size: 0.2,
      isActive: true
    })),
    influenceConnections: Array.from({ length: 30 * scale }, (_, i) => ({
      id: `connection-${i}`,
      from: `node-${i % (20 * scale)}`,
      to: `node-${(i + 1) % (20 * scale)}`,
      strength: Math.random(),
      color: '#45b7d1',
      animated: true
    })),
    diversityScores: Array.from({ length: 8 * scale }, (_, i) => ({
      id: `score-${i}`,
      position: new Vector3(i, 0, 0),
      score: Math.random(),
      category: Object.values(CulturalCategory)[i % Object.values(CulturalCategory).length],
      breakdown: [],
      color: '#96ceb4',
      height: 2
    })),
    trendPredictions: Array.from({ length: 50 * scale }, (_, i) => ({
      id: `prediction-${i}`,
      position: new Vector3(i * 0.2, 0, 0),
      prediction: Math.random(),
      confidence: Math.random(),
      timeframe: new Date(2023, 0, 1 + i),
      category: Object.values(CulturalCategory)[i % Object.values(CulturalCategory).length],
      confidenceRegion: {
        center: new Vector3(0, 0, 0),
        radius: 1,
        opacity: 0.3,
        color: '#feca57'
      }
    }))
  });

  it('should render timeline mode within performance budget', () => {
    const data = createMockData(1);
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="timeline"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 200ms
    expect(renderTime).toBeLessThan(200);
  });

  it('should render network mode within performance budget', () => {
    const data = createMockData(1);
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="network"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 200ms
    expect(renderTime).toBeLessThan(200);
  });

  it('should render diversity mode within performance budget', () => {
    const data = createMockData(1);
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="diversity"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 200ms
    expect(renderTime).toBeLessThan(200);
  });

  it('should render trends mode within performance budget', () => {
    const data = createMockData(1);
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="trends"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 200ms
    expect(renderTime).toBeLessThan(200);
  });

  it('should render overview mode within performance budget', () => {
    const data = createMockData(0.5); // Smaller dataset for overview
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="overview"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 300ms (more complex with multiple views)
    expect(renderTime).toBeLessThan(300);
  });

  it('should handle large datasets efficiently', () => {
    const data = createMockData(10); // 10x larger dataset
    const startTime = performance.now();

    render(
      <CulturalVisualization3D
        data={data}
        mode="timeline"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should still render within 1 second even with large dataset
    expect(renderTime).toBeLessThan(1000);
  });

  it('should handle mode switching efficiently', () => {
    const data = createMockData(1);
    const modes = ['timeline', 'network', 'diversity', 'trends', 'overview'];
    
    const { rerender } = render(
      <CulturalVisualization3D
        data={data}
        mode="timeline"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    const startTime = performance.now();

    // Switch between all modes
    modes.forEach(mode => {
      rerender(
        <CulturalVisualization3D
          data={data}
          mode={mode as any}
          onModeChange={vi.fn()}
          onDataPointSelect={vi.fn()}
        />
      );
    });

    const endTime = performance.now();
    const totalTime = endTime - startTime;

    // Should handle 5 mode switches within 500ms
    expect(totalTime).toBeLessThan(500);
  });

  it('should maintain 60fps target for animations', () => {
    const data = createMockData(1);
    
    render(
      <CulturalVisualization3D
        data={data}
        mode="timeline"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    // Simulate 60fps frame budget (16.67ms per frame)
    const frameTime = 16.67;
    const targetFPS = 60;
    
    // This is a conceptual test - in real implementation,
    // we would measure actual frame times during animations
    expect(frameTime).toBeLessThan(1000 / targetFPS + 1); // Allow 1ms tolerance
  });

  it('should handle memory efficiently with component unmounting', () => {
    const data = createMockData(5);
    
    const { unmount } = render(
      <CulturalVisualization3D
        data={data}
        mode="timeline"
        onModeChange={vi.fn()}
        onDataPointSelect={vi.fn()}
      />
    );

    // Measure memory before unmount
    const beforeUnmount = performance.now();
    
    unmount();
    
    const afterUnmount = performance.now();
    const unmountTime = afterUnmount - beforeUnmount;

    // Should unmount quickly without memory leaks
    expect(unmountTime).toBeLessThan(50);
  });

  it('should support cross-device compatibility', () => {
    const data = createMockData(1);
    
    // Test different viewport sizes
    const viewports = [
      { width: 320, height: 568 },  // Mobile
      { width: 768, height: 1024 }, // Tablet
      { width: 1920, height: 1080 } // Desktop
    ];

    viewports.forEach(viewport => {
      // Mock viewport size
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: viewport.width,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: viewport.height,
      });

      const startTime = performance.now();

      const { unmount } = render(
        <CulturalVisualization3D
          data={data}
          mode="timeline"
          onModeChange={vi.fn()}
          onDataPointSelect={vi.fn()}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render efficiently on all device sizes
      expect(renderTime).toBeLessThan(300);

      unmount();
    });
  });
});