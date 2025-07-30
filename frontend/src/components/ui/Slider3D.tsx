import React, { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Slider3DProps {
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'accent' | 'elegant'
  size?: 'sm' | 'md' | 'lg'
  showValue?: boolean
  showTicks?: boolean
  tickCount?: number
  label?: string
  className?: string
  'aria-label'?: string
  'aria-describedby'?: string
}

const Slider3D: React.FC<Slider3DProps> = ({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  disabled = false,
  variant = 'primary',
  size = 'md',
  showValue = true,
  showTicks = false,
  tickCount = 5,
  label,
  className = '',
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const sliderRef = useRef<HTMLDivElement>(null);
  const thumbRef = useRef<HTMLDivElement>(null);

  const sizeStyles = {
    sm: {
      track: 'h-2',
      thumb: 'w-4 h-4',
      container: 'py-2'
    },
    md: {
      track: 'h-3',
      thumb: 'w-6 h-6',
      container: 'py-3'
    },
    lg: {
      track: 'h-4',
      thumb: 'w-8 h-8',
      container: 'py-4'
    }
  };

  const variantStyles = {
    primary: {
      track: 'bg-gray-200',
      fill: 'var(--gradient-primary)',
      thumb: 'var(--gradient-primary)',
      glow: 'var(--shadow-glow-primary)'
    },
    secondary: {
      track: 'bg-gray-200',
      fill: 'var(--gradient-secondary)',
      thumb: 'var(--gradient-secondary)',
      glow: 'var(--shadow-glow-secondary)'
    },
    accent: {
      track: 'bg-gray-200',
      fill: 'var(--gradient-accent)',
      thumb: 'var(--gradient-accent)',
      glow: 'var(--shadow-glow-accent)'
    },
    elegant: {
      track: 'bg-gradient-to-r from-gray-100 to-gray-200',
      fill: 'linear-gradient(135deg, rgba(102, 126, 234, 0.8), rgba(118, 75, 162, 0.8))',
      thumb: 'linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.7))',
      glow: '0 0 20px rgba(102, 126, 234, 0.4)'
    }
  };

  // Calculate percentage and position
  const percentage = ((value - min) / (max - min)) * 100;

  // Handle mouse/touch events
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (disabled) return;
    
    setIsDragging(true);
    e.currentTarget.setPointerCapture(e.pointerId);
    
    const updateValue = (clientX: number) => {
      if (!sliderRef.current) return;
      
      const rect = sliderRef.current.getBoundingClientRect();
      const newPercentage = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100));
      const newValue = min + (newPercentage / 100) * (max - min);
      const steppedValue = Math.round(newValue / step) * step;
      
      onChange(Math.max(min, Math.min(max, steppedValue)));
    };
    
    updateValue(e.clientX);
  }, [disabled, min, max, step, onChange]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging || disabled) return;
    
    if (!sliderRef.current) return;
    
    const rect = sliderRef.current.getBoundingClientRect();
    const newPercentage = Math.max(0, Math.min(100, ((e.clientX - rect.left) / rect.width) * 100));
    const newValue = min + (newPercentage / 100) * (max - min);
    const steppedValue = Math.round(newValue / step) * step;
    
    onChange(Math.max(min, Math.min(max, steppedValue)));
  }, [isDragging, disabled, min, max, step, onChange]);

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Keyboard handling
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;
    
    let newValue = value;
    const largeStep = (max - min) / 10;
    
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowUp':
        newValue = Math.min(max, value + step);
        break;
      case 'ArrowLeft':
      case 'ArrowDown':
        newValue = Math.max(min, value - step);
        break;
      case 'PageUp':
        newValue = Math.min(max, value + largeStep);
        break;
      case 'PageDown':
        newValue = Math.max(min, value - largeStep);
        break;
      case 'Home':
        newValue = min;
        break;
      case 'End':
        newValue = max;
        break;
      default:
        return;
    }
    
    e.preventDefault();
    onChange(newValue);
  };

  // Generate tick marks
  const generateTicks = () => {
    if (!showTicks) return null;
    
    const ticks = [];
    for (let i = 0; i <= tickCount; i++) {
      const tickPercentage = (i / tickCount) * 100;
      ticks.push(
        <div
          key={i}
          className="absolute w-0.5 h-2 bg-gray-400 transform -translate-x-1/2"
          style={{ left: `${tickPercentage}%`, top: '100%' }}
        />
      );
    }
    return ticks;
  };

  return (
    <div className={`relative ${sizeStyles[size].container} ${className}`}>
      {/* Label */}
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
        </label>
      )}
      
      {/* Slider Container */}
      <div className="relative">
        {/* Track */}
        <div
          ref={sliderRef}
          className={`
            relative ${sizeStyles[size].track} rounded-full cursor-pointer
            transition-all duration-200 transform-gpu
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
          style={{
            background: variantStyles[variant].track,
            boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
          }}
          onPointerDown={handlePointerDown}
          onPointerMove={handlePointerMove}
          onPointerUp={handlePointerUp}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {/* Fill */}
          <motion.div
            className={`absolute top-0 left-0 ${sizeStyles[size].track} rounded-full`}
            style={{
              width: `${percentage}%`,
              background: variantStyles[variant].fill,
              boxShadow: isHovered ? variantStyles[variant].glow : undefined
            }}
            initial={{ width: 0 }}
            animate={{ width: `${percentage}%` }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          />
          
          {/* Thumb */}
          <motion.div
            ref={thumbRef}
            className={`
              absolute top-1/2 ${sizeStyles[size].thumb} rounded-full cursor-grab
              transform -translate-x-1/2 -translate-y-1/2 border-2 border-white
              transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
              ${disabled ? 'cursor-not-allowed' : isDragging ? 'cursor-grabbing' : ''}
              ${isFocused ? 'ring-2 ring-blue-500' : ''}
            `}
            style={{
              left: `${percentage}%`,
              background: variantStyles[variant].thumb,
              boxShadow: `
                var(--shadow-3d-md),
                ${(isHovered || isDragging) ? variantStyles[variant].glow : '0 0 0 transparent'}
              `,
              transform: `
                translateX(-50%) translateY(-50%) 
                translateZ(${isDragging ? 8 : isHovered ? 4 : 0}px)
                scale(${isDragging ? 1.1 : isHovered ? 1.05 : 1})
              `
            }}
            tabIndex={disabled ? -1 : 0}
            role="slider"
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={value}
            aria-label={ariaLabel || label}
            aria-describedby={ariaDescribedBy}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            whileHover={!disabled ? { scale: 1.05 } : {}}
            whileTap={!disabled ? { scale: 1.1 } : {}}
          >
            {/* Thumb Glow Effect */}
            <AnimatePresence>
              {(isHovered || isDragging) && !disabled && (
                <motion.div
                  className="absolute inset-0 rounded-full pointer-events-none"
                  style={{
                    background: `radial-gradient(circle, ${variantStyles[variant].fill}40, transparent 70%)`
                  }}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1.2 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ duration: 0.2 }}
                />
              )}
            </AnimatePresence>
          </motion.div>
          
          {/* Tick marks */}
          {generateTicks()}
        </div>
        
        {/* Value Display */}
        <AnimatePresence>
          {showValue && (isHovered || isDragging || isFocused) && (
            <motion.div
              className="absolute -top-12 left-0 transform -translate-x-1/2"
              style={{ left: `${percentage}%` }}
              initial={{ opacity: 0, y: 10, scale: 0.8 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.8 }}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              <div
                className="px-2 py-1 text-xs font-medium text-white rounded shadow-lg"
                style={{
                  background: variantStyles[variant].fill,
                  boxShadow: 'var(--shadow-3d-md)'
                }}
              >
                {value}
                <div
                  className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0"
                  style={{
                    borderLeft: '4px solid transparent',
                    borderRight: '4px solid transparent',
                    borderTop: `4px solid ${variantStyles[variant].fill}`
                  }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Slider3D