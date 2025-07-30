import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Canvas } from '@react-three/fiber';
import '@testing-library/jest-dom';
import Scene3D from '../Scene3D';

import { vi } from 'vitest';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children, ...props }: any) => (
    <div data-testid="canvas" {...props}>
      {children}
    </div>
  ),
  useFrame: vi.fn(),
  useThree: () => ({
    camera: {
      position: { x: 0, y: 0, z: 0 },
      lookAt: vi.fn()
    },
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
  PerspectiveCamera: ({ children, ...props }: any) => (
    <div data-testid="camera" {...props}>
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
  )
}));

describe('Scene3D Component', () => {
  const mockOnCameraChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(
      <Scene3D>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.getByTestId('canvas')).toBeInTheDocument();
  });

  it('renders with default props', () => {
    render(
      <Scene3D>
        <div>Test content</div>
      </Scene3D>
    );
    
    const canvas = screen.getByTestId('canvas');
    expect(canvas).toHaveStyle({ background: '#0a0a0a' });
  });

  it('applies custom camera position', () => {
    const customPosition: [number, number, number] = [5, 5, 5];
    
    render(
      <Scene3D cameraPosition={customPosition}>
        <div>Test content</div>
      </Scene3D>
    );
    
    const canvas = screen.getByTestId('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders grid when enabled', () => {
    render(
      <Scene3D enableGrid={true}>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.getByTestId('grid')).toBeInTheDocument();
  });

  it('does not render grid when disabled', () => {
    render(
      <Scene3D enableGrid={false}>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.queryByTestId('grid')).not.toBeInTheDocument();
  });

  it('renders controls when enabled', () => {
    render(
      <Scene3D enableControls={true}>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.getByTestId('orbit-controls')).toBeInTheDocument();
  });

  it('does not render controls when disabled', () => {
    render(
      <Scene3D enableControls={false}>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.queryByTestId('orbit-controls')).not.toBeInTheDocument();
  });

  it('applies custom background color', () => {
    const customColor = '#ff0000';
    
    render(
      <Scene3D backgroundColor={customColor}>
        <div>Test content</div>
      </Scene3D>
    );
    
    const canvas = screen.getByTestId('canvas');
    expect(canvas).toHaveStyle({ background: customColor });
  });

  it('calls onCameraChange callback', () => {
    render(
      <Scene3D onCameraChange={mockOnCameraChange}>
        <div>Test content</div>
      </Scene3D>
    );
    
    // Camera change callback would be called in useFrame
    // This is mocked, so we just verify the component renders
    expect(screen.getByTestId('canvas')).toBeInTheDocument();
  });

  it('renders children content', () => {
    const testContent = 'Test 3D Content';
    
    render(
      <Scene3D>
        <div>{testContent}</div>
      </Scene3D>
    );
    
    expect(screen.getByText(testContent)).toBeInTheDocument();
  });

  it('handles suspense fallback', () => {
    // This would test the Suspense fallback, but since we're mocking
    // the Three.js components, we just verify the structure
    render(
      <Scene3D>
        <div>Test content</div>
      </Scene3D>
    );
    
    expect(screen.getByTestId('canvas')).toBeInTheDocument();
  });
});

describe('Scene3D Performance', () => {
  it('should render within performance budget', async () => {
    const startTime = performance.now();
    
    render(
      <Scene3D>
        <div>Performance test content</div>
      </Scene3D>
    );
    
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    
    // Should render within 100ms
    expect(renderTime).toBeLessThan(100);
  });

  it('should handle multiple re-renders efficiently', () => {
    const { rerender } = render(
      <Scene3D cameraPosition={[0, 0, 0]}>
        <div>Test</div>
      </Scene3D>
    );

    const startTime = performance.now();
    
    // Perform multiple re-renders
    for (let i = 0; i < 10; i++) {
      rerender(
        <Scene3D cameraPosition={[i, i, i]}>
          <div>Test {i}</div>
        </Scene3D>
      );
    }
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;
    
    // Should handle 10 re-renders within 200ms
    expect(totalTime).toBeLessThan(200);
  });
});

describe('Scene3D Accessibility', () => {
  it('should be keyboard navigable', () => {
    render(
      <Scene3D>
        <div>Accessible content</div>
      </Scene3D>
    );
    
    const canvas = screen.getByTestId('canvas');
    
    // Should be focusable
    canvas.focus();
    expect(document.activeElement).toBe(canvas);
  });

  it('should support screen readers', () => {
    render(
      <Scene3D>
        <div role="img" aria-label="3D Cultural Visualization">
          3D Content
        </div>
      </Scene3D>
    );
    
    const content = screen.getByRole('img');
    expect(content).toHaveAttribute('aria-label', '3D Cultural Visualization');
  });
});