import { renderHook, act } from '@testing-library/react';
import { useGestures } from '../useGestures';
import { Vector3 } from 'three';
import { vi } from 'vitest';

// Mock DOM element
const createMockElement = () => {
  const element = document.createElement('div');
  const listeners: { [key: string]: EventListener[] } = {};
  
  element.addEventListener = vi.fn((event: string, listener: EventListener) => {
    if (!listeners[event]) listeners[event] = [];
    listeners[event].push(listener);
  });
  
  element.removeEventListener = vi.fn((event: string, listener: EventListener) => {
    if (listeners[event]) {
      const index = listeners[event].indexOf(listener);
      if (index > -1) listeners[event].splice(index, 1);
    }
  });

  // Helper to trigger events
  (element as any).triggerEvent = (eventType: string, eventData: any) => {
    if (listeners[eventType]) {
      listeners[eventType].forEach(listener => listener(eventData));
    }
  };

  return element;
};

// Mock touch event
const createTouchEvent = (type: string, touches: Array<{ clientX: number; clientY: number }>) => {
  const touchList = touches.map(touch => ({ ...touch })) as any;
  touchList.length = touches.length;
  
  return {
    type,
    touches: touchList,
    preventDefault: vi.fn(),
    stopPropagation: vi.fn()
  };
};

// Mock mouse event
const createMouseEvent = (type: string, clientX: number, clientY: number) => ({
  type,
  clientX,
  clientY,
  preventDefault: vi.fn(),
  stopPropagation: vi.fn()
});

describe('useGestures Hook', () => {
  let mockElement: HTMLElement;
  let mockCallbacks: any;

  beforeEach(() => {
    mockElement = createMockElement();
    mockCallbacks = {
      onPinch: vi.fn(),
      onRotate: vi.fn(),
      onSwipe: vi.fn(),
      onTap: vi.fn(),
      onDoubleTap: vi.fn(),
      onLongPress: vi.fn(),
      onDrag: vi.fn(),
      onGestureStart: vi.fn(),
      onGestureEnd: vi.fn()
    };
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should initialize without errors', () => {
    const elementRef = { current: mockElement };
    
    const { result } = renderHook(() => 
      useGestures(elementRef, mockCallbacks)
    );

    expect(result.current.isGestureActive).toBe(false);
    expect(result.current.touchCount).toBe(0);
  });

  it('should detect tap gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    // Simulate tap
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    act(() => {
      vi.advanceTimersByTime(50);
    });

    act(() => {
      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    expect(mockCallbacks.onTap).toHaveBeenCalledWith(expect.any(Vector3));
  });

  it('should detect double tap gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    // First tap
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    act(() => {
      vi.advanceTimersByTime(50);
    });

    act(() => {
      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    // Second tap within double tap timeout
    act(() => {
      vi.advanceTimersByTime(100);
    });

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    act(() => {
      vi.advanceTimersByTime(50);
    });

    act(() => {
      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    expect(mockCallbacks.onDoubleTap).toHaveBeenCalledWith(expect.any(Vector3));
  });

  it('should detect long press gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    // Advance time to trigger long press
    act(() => {
      vi.advanceTimersByTime(600); // Default long press timeout is 500ms
    });

    expect(mockCallbacks.onLongPress).toHaveBeenCalledWith(expect.any(Vector3));
  });

  it('should detect pinch gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    // Start with two fingers
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 },
        { clientX: 200, clientY: 100 }
      ]));
    });

    // Move fingers closer together (pinch in)
    act(() => {
      (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
        { clientX: 120, clientY: 100 },
        { clientX: 180, clientY: 100 }
      ]));
    });

    expect(mockCallbacks.onPinch).toHaveBeenCalledWith(
      expect.any(Number),
      expect.any(Vector3)
    );
  });

  it('should detect rotation gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    // Start with two fingers
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 },
        { clientX: 200, clientY: 100 }
      ]));
    });

    // Rotate fingers
    act(() => {
      (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
        { clientX: 100, clientY: 120 },
        { clientX: 200, clientY: 80 }
      ]));
    });

    expect(mockCallbacks.onRotate).toHaveBeenCalledWith(
      expect.any(Number),
      expect.any(Vector3)
    );
  });

  it('should detect swipe gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    // Quick swipe movement
    act(() => {
      (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
        { clientX: 200, clientY: 100 }
      ]));
    });

    act(() => {
      vi.advanceTimersByTime(16); // One frame
    });

    act(() => {
      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    expect(mockCallbacks.onSwipe).toHaveBeenCalledWith(
      expect.any(Vector3),
      expect.any(Number)
    );
  });

  it('should detect drag gestures', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    act(() => {
      (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
        { clientX: 110, clientY: 110 }
      ]));
    });

    expect(mockCallbacks.onDrag).toHaveBeenCalledWith(
      expect.any(Vector3),
      expect.any(Vector3)
    );
  });

  it('should handle mouse events for desktop compatibility', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('mousedown', createMouseEvent('mousedown', 100, 100));
    });

    act(() => {
      (mockElement as any).triggerEvent('mousemove', createMouseEvent('mousemove', 110, 110));
    });

    expect(mockCallbacks.onDrag).toHaveBeenCalledWith(
      expect.any(Vector3),
      expect.any(Vector3)
    );

    act(() => {
      (mockElement as any).triggerEvent('mouseup', createMouseEvent('mouseup', 110, 110));
    });

    expect(mockCallbacks.onTap).toHaveBeenCalledWith(expect.any(Vector3));
  });

  it('should handle wheel events for zoom', () => {
    const elementRef = { current: mockElement };
    
    renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('wheel', {
        deltaY: -100,
        clientX: 100,
        clientY: 100,
        preventDefault: vi.fn()
      });
    });

    expect(mockCallbacks.onPinch).toHaveBeenCalledWith(
      1.1, // Scale up for negative deltaY
      expect.any(Vector3)
    );
  });

  it('should respect gesture options', () => {
    const elementRef = { current: mockElement };
    const options = {
      enablePinch: false,
      enableTap: false
    };
    
    renderHook(() => useGestures(elementRef, mockCallbacks, options));

    // Try pinch - should not trigger
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 },
        { clientX: 200, clientY: 100 }
      ]));
    });

    act(() => {
      (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
        { clientX: 120, clientY: 100 },
        { clientX: 180, clientY: 100 }
      ]));
    });

    expect(mockCallbacks.onPinch).not.toHaveBeenCalled();

    // Try tap - should not trigger
    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));
    });

    act(() => {
      vi.advanceTimersByTime(50);
    });

    act(() => {
      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    expect(mockCallbacks.onTap).not.toHaveBeenCalled();
  });

  it('should clean up event listeners on unmount', () => {
    const elementRef = { current: mockElement };
    
    const { unmount } = renderHook(() => 
      useGestures(elementRef, mockCallbacks)
    );

    expect(mockElement.addEventListener).toHaveBeenCalledTimes(7); // All event types

    unmount();

    expect(mockElement.removeEventListener).toHaveBeenCalledTimes(7);
  });
});

describe('useGestures Performance', () => {
  it('should handle rapid touch events efficiently', () => {
    const mockElement = createMockElement();
    const elementRef = { current: mockElement };
    const mockCallbacks = { onDrag: vi.fn() };

    renderHook(() => useGestures(elementRef, mockCallbacks));

    const startTime = performance.now();

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 100, clientY: 100 }
      ]));

      // Simulate 60 FPS touch move events
      for (let i = 0; i < 60; i++) {
        (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
          { clientX: 100 + i, clientY: 100 + i }
        ]));
      }

      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    const endTime = performance.now();
    const processingTime = endTime - startTime;

    // Should process 60 touch events within 100ms
    expect(processingTime).toBeLessThan(100);
    expect(mockCallbacks.onDrag).toHaveBeenCalledTimes(60);
  });

  it('should maintain velocity history efficiently', () => {
    const mockElement = createMockElement();
    const elementRef = { current: mockElement };
    const mockCallbacks = { onSwipe: vi.fn() };

    const { result } = renderHook(() => useGestures(elementRef, mockCallbacks));

    act(() => {
      (mockElement as any).triggerEvent('touchstart', createTouchEvent('touchstart', [
        { clientX: 0, clientY: 0 }
      ]));

      // Generate many velocity samples
      for (let i = 0; i < 1000; i++) {
        (mockElement as any).triggerEvent('touchmove', createTouchEvent('touchmove', [
          { clientX: i, clientY: 0 }
        ]));
      }

      (mockElement as any).triggerEvent('touchend', createTouchEvent('touchend', []));
    });

    // Velocity should be calculated efficiently
    expect(result.current.velocity).toBeInstanceOf(Vector3);
  });
});