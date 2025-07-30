import { useRef, useEffect, useState, useCallback } from 'react';
import { Vector3 } from 'three';
import { GestureEvent3D } from '../types/cultural3d.types';

interface GestureState {
  isActive: boolean;
  startPosition: Vector3;
  currentPosition: Vector3;
  startDistance: number;
  currentDistance: number;
  startRotation: number;
  currentRotation: number;
  touchCount: number;
  velocity: Vector3;
  lastUpdateTime: number;
}

interface GestureCallbacks {
  onPinch?: (scale: number, center: Vector3) => void;
  onRotate?: (rotation: number, center: Vector3) => void;
  onSwipe?: (direction: Vector3, velocity: number) => void;
  onTap?: (position: Vector3) => void;
  onDoubleTap?: (position: Vector3) => void;
  onLongPress?: (position: Vector3) => void;
  onDrag?: (delta: Vector3, position: Vector3) => void;
  onGestureStart?: (event: GestureEvent3D) => void;
  onGestureEnd?: (event: GestureEvent3D) => void;
}

interface UseGesturesOptions {
  enablePinch?: boolean;
  enableRotation?: boolean;
  enableSwipe?: boolean;
  enableTap?: boolean;
  enableDoubleTap?: boolean;
  enableLongPress?: boolean;
  enableDrag?: boolean;
  pinchThreshold?: number;
  swipeThreshold?: number;
  tapTimeout?: number;
  doubleTapTimeout?: number;
  longPressTimeout?: number;
  rotationThreshold?: number;
}

const defaultOptions: UseGesturesOptions = {
  enablePinch: true,
  enableRotation: true,
  enableSwipe: true,
  enableTap: true,
  enableDoubleTap: true,
  enableLongPress: true,
  enableDrag: true,
  pinchThreshold: 10,
  swipeThreshold: 50,
  tapTimeout: 200,
  doubleTapTimeout: 300,
  longPressTimeout: 500,
  rotationThreshold: 0.1
};

export const useGestures = (
  elementRef: React.RefObject<HTMLElement>,
  callbacks: GestureCallbacks,
  options: UseGesturesOptions = {}
) => {
  const opts = { ...defaultOptions, ...options };
  const gestureState = useRef<GestureState>({
    isActive: false,
    startPosition: new Vector3(),
    currentPosition: new Vector3(),
    startDistance: 0,
    currentDistance: 0,
    startRotation: 0,
    currentRotation: 0,
    touchCount: 0,
    velocity: new Vector3(),
    lastUpdateTime: 0
  });

  const [lastTapTime, setLastTapTime] = useState(0);
  const [tapCount, setTapCount] = useState(0);
  const longPressTimer = useRef<NodeJS.Timeout | null>(null);
  const velocityHistory = useRef<Array<{ position: Vector3; time: number }>>([]);

  // Helper functions
  const getTouchCenter = (touches: TouchList): Vector3 => {
    if (touches.length === 0) return new Vector3();
    
    let x = 0, y = 0;
    for (let i = 0; i < touches.length; i++) {
      x += touches[i].clientX;
      y += touches[i].clientY;
    }
    return new Vector3(x / touches.length, y / touches.length, 0);
  };

  const getTouchDistance = (touches: TouchList): number => {
    if (touches.length < 2) return 0;
    
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  };

  const getTouchRotation = (touches: TouchList): number => {
    if (touches.length < 2) return 0;
    
    const dx = touches[1].clientX - touches[0].clientX;
    const dy = touches[1].clientY - touches[0].clientY;
    return Math.atan2(dy, dx);
  };

  const calculateVelocity = (position: Vector3, time: number): Vector3 => {
    velocityHistory.current.push({ position: position.clone(), time });
    
    // Keep only recent history (last 100ms)
    const cutoffTime = time - 100;
    velocityHistory.current = velocityHistory.current.filter(h => h.time > cutoffTime);
    
    if (velocityHistory.current.length < 2) return new Vector3();
    
    const oldest = velocityHistory.current[0];
    const newest = velocityHistory.current[velocityHistory.current.length - 1];
    const deltaTime = newest.time - oldest.time;
    
    if (deltaTime === 0) return new Vector3();
    
    return newest.position.clone().sub(oldest.position).divideScalar(deltaTime);
  };

  // Touch event handlers
  const handleTouchStart = useCallback((event: TouchEvent) => {
    event.preventDefault();
    
    const touches = event.touches;
    const center = getTouchCenter(touches);
    const distance = getTouchDistance(touches);
    const rotation = getTouchRotation(touches);
    const time = Date.now();

    gestureState.current = {
      isActive: true,
      startPosition: center.clone(),
      currentPosition: center.clone(),
      startDistance: distance,
      currentDistance: distance,
      startRotation: rotation,
      currentRotation: rotation,
      touchCount: touches.length,
      velocity: new Vector3(),
      lastUpdateTime: time
    };

    velocityHistory.current = [{ position: center.clone(), time }];

    // Long press detection
    if (opts.enableLongPress && touches.length === 1) {
      longPressTimer.current = setTimeout(() => {
        if (gestureState.current.isActive && callbacks.onLongPress) {
          callbacks.onLongPress(center);
        }
      }, opts.longPressTimeout);
    }

    // Gesture start callback
    if (callbacks.onGestureStart) {
      callbacks.onGestureStart({
        type: 'tap',
        position: center,
        delta: new Vector3(),
        touches: touches.length
      });
    }
  }, [callbacks, opts]);

  const handleTouchMove = useCallback((event: TouchEvent) => {
    event.preventDefault();
    
    if (!gestureState.current.isActive) return;
    
    const touches = event.touches;
    const center = getTouchCenter(touches);
    const distance = getTouchDistance(touches);
    const rotation = getTouchRotation(touches);
    const time = Date.now();

    const prevPosition = gestureState.current.currentPosition.clone();
    const delta = center.clone().sub(prevPosition);
    
    gestureState.current.currentPosition = center;
    gestureState.current.currentDistance = distance;
    gestureState.current.currentRotation = rotation;
    gestureState.current.velocity = calculateVelocity(center, time);
    gestureState.current.lastUpdateTime = time;

    // Clear long press timer on movement
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    // Pinch gesture
    if (opts.enablePinch && touches.length === 2 && gestureState.current.startDistance > 0) {
      const scale = gestureState.current.currentDistance / gestureState.current.startDistance;
      const scaleChange = Math.abs(scale - 1);
      
      if (scaleChange > opts.pinchThreshold! / 100 && callbacks.onPinch) {
        callbacks.onPinch(scale, center);
      }
    }

    // Rotation gesture
    if (opts.enableRotation && touches.length === 2) {
      const rotationDelta = gestureState.current.currentRotation - gestureState.current.startRotation;
      
      if (Math.abs(rotationDelta) > opts.rotationThreshold! && callbacks.onRotate) {
        callbacks.onRotate(rotationDelta, center);
      }
    }

    // Drag gesture
    if (opts.enableDrag && touches.length === 1 && callbacks.onDrag) {
      callbacks.onDrag(delta, center);
    }
  }, [callbacks, opts]);

  const handleTouchEnd = useCallback((event: TouchEvent) => {
    event.preventDefault();
    
    if (!gestureState.current.isActive) return;
    
    const touches = event.touches;
    const center = gestureState.current.currentPosition;
    const velocity = gestureState.current.velocity;
    const time = Date.now();

    // Clear long press timer
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    // Swipe gesture
    if (opts.enableSwipe && touches.length === 0) {
      const velocityMagnitude = velocity.length();
      
      if (velocityMagnitude > opts.swipeThreshold! && callbacks.onSwipe) {
        const direction = velocity.clone().normalize();
        callbacks.onSwipe(direction, velocityMagnitude);
      }
    }

    // Tap gesture
    if (opts.enableTap && touches.length === 0 && gestureState.current.touchCount === 1) {
      const startPos = gestureState.current.startPosition;
      const endPos = gestureState.current.currentPosition;
      const distance = startPos.distanceTo(endPos);
      const duration = time - gestureState.current.lastUpdateTime;

      if (distance < 10 && duration < opts.tapTimeout!) {
        // Double tap detection
        if (opts.enableDoubleTap && time - lastTapTime < opts.doubleTapTimeout!) {
          setTapCount(prev => prev + 1);
          
          if (tapCount === 0 && callbacks.onDoubleTap) {
            callbacks.onDoubleTap(center);
          }
        } else {
          setTapCount(0);
          if (callbacks.onTap) {
            callbacks.onTap(center);
          }
        }
        
        setLastTapTime(time);
      }
    }

    // Reset gesture state if no touches remain
    if (touches.length === 0) {
      gestureState.current.isActive = false;
      velocityHistory.current = [];
      
      // Gesture end callback
      if (callbacks.onGestureEnd) {
        callbacks.onGestureEnd({
          type: 'tap',
          position: center,
          delta: new Vector3(),
          touches: 0
        });
      }
    }
  }, [callbacks, opts, lastTapTime, tapCount]);

  // Mouse event handlers for desktop compatibility
  const handleMouseDown = useCallback((event: MouseEvent) => {
    const position = new Vector3(event.clientX, event.clientY, 0);
    const time = Date.now();

    gestureState.current = {
      isActive: true,
      startPosition: position.clone(),
      currentPosition: position.clone(),
      startDistance: 0,
      currentDistance: 0,
      startRotation: 0,
      currentRotation: 0,
      touchCount: 1,
      velocity: new Vector3(),
      lastUpdateTime: time
    };

    velocityHistory.current = [{ position: position.clone(), time }];

    // Long press detection
    if (opts.enableLongPress) {
      longPressTimer.current = setTimeout(() => {
        if (gestureState.current.isActive && callbacks.onLongPress) {
          callbacks.onLongPress(position);
        }
      }, opts.longPressTimeout);
    }
  }, [callbacks, opts]);

  const handleMouseMove = useCallback((event: MouseEvent) => {
    if (!gestureState.current.isActive) return;
    
    const position = new Vector3(event.clientX, event.clientY, 0);
    const time = Date.now();
    const delta = position.clone().sub(gestureState.current.currentPosition);

    gestureState.current.currentPosition = position;
    gestureState.current.velocity = calculateVelocity(position, time);
    gestureState.current.lastUpdateTime = time;

    // Clear long press timer on movement
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    // Drag gesture
    if (opts.enableDrag && callbacks.onDrag) {
      callbacks.onDrag(delta, position);
    }
  }, [callbacks, opts]);

  const handleMouseUp = useCallback((event: MouseEvent) => {
    if (!gestureState.current.isActive) return;
    
    const position = new Vector3(event.clientX, event.clientY, 0);
    const velocity = gestureState.current.velocity;
    const time = Date.now();

    // Clear long press timer
    if (longPressTimer.current) {
      clearTimeout(longPressTimer.current);
      longPressTimer.current = null;
    }

    // Swipe gesture
    if (opts.enableSwipe) {
      const velocityMagnitude = velocity.length();
      
      if (velocityMagnitude > opts.swipeThreshold! && callbacks.onSwipe) {
        const direction = velocity.clone().normalize();
        callbacks.onSwipe(direction, velocityMagnitude);
      }
    }

    // Tap gesture
    if (opts.enableTap) {
      const startPos = gestureState.current.startPosition;
      const distance = startPos.distanceTo(position);
      const duration = time - gestureState.current.lastUpdateTime;

      if (distance < 10 && duration < opts.tapTimeout!) {
        // Double tap detection
        if (opts.enableDoubleTap && time - lastTapTime < opts.doubleTapTimeout!) {
          setTapCount(prev => prev + 1);
          
          if (tapCount === 0 && callbacks.onDoubleTap) {
            callbacks.onDoubleTap(position);
          }
        } else {
          setTapCount(0);
          if (callbacks.onTap) {
            callbacks.onTap(position);
          }
        }
        
        setLastTapTime(time);
      }
    }

    gestureState.current.isActive = false;
    velocityHistory.current = [];
  }, [callbacks, opts, lastTapTime, tapCount]);

  // Wheel event for zoom
  const handleWheel = useCallback((event: WheelEvent) => {
    event.preventDefault();
    
    if (opts.enablePinch && callbacks.onPinch) {
      const scale = event.deltaY > 0 ? 0.9 : 1.1;
      const position = new Vector3(event.clientX, event.clientY, 0);
      callbacks.onPinch(scale, position);
    }
  }, [callbacks, opts]);

  // Setup event listeners
  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    // Touch events
    element.addEventListener('touchstart', handleTouchStart, { passive: false });
    element.addEventListener('touchmove', handleTouchMove, { passive: false });
    element.addEventListener('touchend', handleTouchEnd, { passive: false });

    // Mouse events
    element.addEventListener('mousedown', handleMouseDown);
    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('mouseup', handleMouseUp);
    element.addEventListener('wheel', handleWheel, { passive: false });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
      element.removeEventListener('mousedown', handleMouseDown);
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('mouseup', handleMouseUp);
      element.removeEventListener('wheel', handleWheel);
      
      if (longPressTimer.current) {
        clearTimeout(longPressTimer.current);
      }
    };
  }, [
    handleTouchStart,
    handleTouchMove,
    handleTouchEnd,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    handleWheel
  ]);

  return {
    isGestureActive: gestureState.current.isActive,
    currentPosition: gestureState.current.currentPosition,
    velocity: gestureState.current.velocity,
    touchCount: gestureState.current.touchCount
  };
};

export default useGestures;