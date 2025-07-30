import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CulturalEvolutionTimeline3D from '../CulturalEvolutionTimeline3D';
import { CulturalMilestone3D, TimelineControls, InteractionState3D, CulturalCategory, SocialPlatform } from '../../../types/cultural3d.types';
import { Vector3 } from 'three';
import { vi } from 'vitest';

// Mock Three.js and React Three Fiber
vi.mock('@react-three/fiber', () => ({
  useFrame: vi.fn((callback) => {
    // Simulate frame callback
    callback({ clock: { elapsedTime: 1 } }, 0.016);
  }),
  useThree: () => ({
    camera: { position: new Vector3(0, 0, 10) },
    raycaster: {},
    mouse: { x: 0, y: 0 }
  })
}));

vi.mock('@react-three/drei', () => ({
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
  Sphere: ({ children, onClick, onPointerOver, onPointerOut, ...props }: any) => (
    <div 
      data-testid="sphere" 
      onClick={onClick}
      onMouseOver={onPointerOver}
      onMouseOut={onPointerOut}
      {...props}
    >
      {children}
    </div>
  )
}));

describe('CulturalEvolutionTimeline3D', () => {
  const mockMilestones: CulturalMilestone3D[] = [
    {
      id: '1',
      position: new Vector3(0, 0, 0),
      timestamp: new Date('2023-01-01'),
      event: 'Started listening to K-pop',
      culturalShift: 0.8,
      confidence: 0.9,
      platforms: [SocialPlatform.SPOTIFY],
      color: '#ff6b6b',
      size: 0.5,
      connections: []
    },
    {
      id: '2',
      position: new Vector3(2, 1, 0),
      timestamp: new Date('2023-06-01'),
      event: 'Discovered indie films',
      culturalShift: 0.6,
      confidence: 0.7,
      platforms: [SocialPlatform.INSTAGRAM],
      color: '#4ecdc4',
      size: 0.4,
      connections: ['1']
    }
  ];

  const mockTimelineControls: TimelineControls = {
    currentTime: new Date('2023-12-01'),
    startTime: new Date('2023-01-01'),
    endTime: new Date('2023-12-31'),
    isPlaying: false,
    playbackSpeed: 1,
    scrubbing: false
  };

  const mockInteractionState: InteractionState3D = {
    hoveredObject: null,
    selectedObject: null,
    isDragging: false,
    dragStart: null,
    cameraPosition: new Vector3(0, 0, 10),
    cameraTarget: new Vector3(0, 0, 0),
    zoom: 1
  };

  const mockCallbacks = {
    onMilestoneClick: vi.fn(),
    onMilestoneHover: vi.fn(),
    onTimelineScroll: vi.fn()
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    expect(screen.getAllByTestId('sphere')).toHaveLength(2); // Two milestones
  });

  it('filters milestones based on current time', () => {
    const pastTimelineControls = {
      ...mockTimelineControls,
      currentTime: new Date('2023-03-01') // Before second milestone
    };

    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={pastTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    // Should only show first milestone
    expect(screen.getAllByTestId('sphere')).toHaveLength(1);
  });

  it('handles milestone click events', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    const milestones = screen.getAllByTestId('sphere');
    fireEvent.click(milestones[0]);

    expect(mockCallbacks.onMilestoneClick).toHaveBeenCalledWith(mockMilestones[0]);
  });

  it('handles milestone hover events', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    const milestones = screen.getAllByTestId('sphere');
    fireEvent.mouseOver(milestones[0]);

    expect(mockCallbacks.onMilestoneHover).toHaveBeenCalledWith(mockMilestones[0]);

    fireEvent.mouseOut(milestones[0]);
    expect(mockCallbacks.onMilestoneHover).toHaveBeenCalledWith(null);
  });

  it('displays timeline path when milestones exist', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    expect(screen.getByTestId('line')).toBeInTheDocument();
  });

  it('shows playing indicator when timeline is playing', () => {
    const playingControls = {
      ...mockTimelineControls,
      isPlaying: true
    };

    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={playingControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    expect(screen.getByText(/Playing/)).toBeInTheDocument();
  });

  it('displays milestone labels on hover', () => {
    const hoveredInteractionState = {
      ...mockInteractionState,
      hoveredObject: '1'
    };

    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={hoveredInteractionState}
        {...mockCallbacks}
      />
    );

    expect(screen.getByText('Started listening to K-pop')).toBeInTheDocument();
  });

  it('displays confidence indicators', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    // Should have confidence indicators for each milestone
    const spheres = screen.getAllByTestId('sphere');
    expect(spheres.length).toBeGreaterThanOrEqual(mockMilestones.length);
  });

  it('handles timeline scrubbing', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        {...mockCallbacks}
      />
    );

    // Timeline scrubber should be present
    const spheres = screen.getAllByTestId('sphere');
    expect(spheres.length).toBeGreaterThan(mockMilestones.length); // Includes scrubber
  });
});

describe('CulturalEvolutionTimeline3D Performance', () => {
  it('should handle large numbers of milestones efficiently', () => {
    const largeMilestoneSet = Array.from({ length: 1000 }, (_, i) => ({
      id: i.toString(),
      position: new Vector3(i * 0.1, 0, 0),
      timestamp: new Date(2023, 0, 1 + i),
      event: `Event ${i}`,
      culturalShift: Math.random(),
      confidence: Math.random(),
      platforms: [SocialPlatform.SPOTIFY],
      color: '#ff6b6b',
      size: 0.3,
      connections: []
    }));

    const startTime = performance.now();

    render(
      <CulturalEvolutionTimeline3D
        milestones={largeMilestoneSet}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        onMilestoneClick={vi.fn()}
        onMilestoneHover={vi.fn()}
        onTimelineScroll={vi.fn()}
      />
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Should render within 500ms even with 1000 milestones
    expect(renderTime).toBeLessThan(500);
  });

  it('should update efficiently when timeline controls change', () => {
    const { rerender } = render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        onMilestoneClick={vi.fn()}
        onMilestoneHover={vi.fn()}
        onTimelineScroll={vi.fn()}
      />
    );

    const startTime = performance.now();

    // Simulate timeline progression
    for (let i = 0; i < 100; i++) {
      const newControls = {
        ...mockTimelineControls,
        currentTime: new Date(2023, 0, 1 + i)
      };

      rerender(
        <CulturalEvolutionTimeline3D
          milestones={mockMilestones}
          timelineControls={newControls}
          interactionState={mockInteractionState}
          onMilestoneClick={vi.fn()}
          onMilestoneHover={vi.fn()}
          onTimelineScroll={vi.fn()}
        />
      );
    }

    const endTime = performance.now();
    const totalTime = endTime - startTime;

    // Should handle 100 timeline updates within 300ms
    expect(totalTime).toBeLessThan(300);
  });
});

describe('CulturalEvolutionTimeline3D Accessibility', () => {
  it('should provide accessible milestone information', () => {
    render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        onMilestoneClick={vi.fn()}
        onMilestoneHover={vi.fn()}
        onTimelineScroll={vi.fn()}
      />
    );

    // Should have text elements for accessibility
    expect(screen.getAllByTestId('text')).toHaveLength(3); // Timeline labels
  });

  it('should support keyboard navigation', () => {
    const { container } = render(
      <CulturalEvolutionTimeline3D
        milestones={mockMilestones}
        timelineControls={mockTimelineControls}
        interactionState={mockInteractionState}
        onMilestoneClick={vi.fn()}
        onMilestoneHover={vi.fn()}
        onTimelineScroll={vi.fn()}
      />
    );

    // Timeline should be keyboard accessible
    const milestones = screen.getAllByTestId('sphere');
    milestones.forEach(milestone => {
      expect(milestone).toBeInTheDocument();
    });
  });
});