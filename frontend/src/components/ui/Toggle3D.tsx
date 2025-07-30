import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Toggle3DProps {
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
  variant?: 'primary' | 'secondary' | 'accent' | 'elegant'
  size?: 'sm' | 'md' | 'lg'
  label?: string
  description?: string
  showIcons?: boolean
  className?: string
  'aria-label'?: string
  'aria-describedby'?: string
}

const Toggle3D: React.FC<Toggle3DProps> = ({
  checked,
  onChange,
  disabled = false,
  variant = 'primary',
  size = 'md',
  label,
  description,
  showIcons = true,
  className = '',
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isFocused, setIsFocused] = useState(false);

  const sizeStyles = {
    sm: {
      track: 'w-10 h-5',
      thumb: 'w-4 h-4',
      translate: 'translate-x-5',
      icon: 'w-3 h-3'
    },
    md: {
      track: 'w-12 h-6',
      thumb: 'w-5 h-5',
      translate: 'translate-x-6',
      icon: 'w-3.5 h-3.5'
    },
    lg: {
      track: 'w-14 h-7',
      thumb: 'w-6 h-6',
      translate: 'translate-x-7',
      icon: 'w-4 h-4'
    }
  };

  const variantStyles = {
    primary: {
      trackOn: 'var(--gradient-primary)',
      trackOff: 'bg-gray-300',
      thumb: 'bg-white',
      glow: 'var(--shadow-glow-primary)'
    },
    secondary: {
      trackOn: 'var(--gradient-secondary)',
      trackOff: 'bg-gray-300',
      thumb: 'bg-white',
      glow: 'var(--shadow-glow-secondary)'
    },
    accent: {
      trackOn: 'var(--gradient-accent)',
      trackOff: 'bg-gray-300',
      thumb: 'bg-white',
      glow: 'var(--shadow-glow-accent)'
    },
    elegant: {
      trackOn: 'linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9))',
      trackOff: 'linear-gradient(135deg, rgba(156, 163, 175, 0.8), rgba(107, 114, 128, 0.8))',
      thumb: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85))',
      glow: '0 0 20px rgba(102, 126, 234, 0.4)'
    }
  };

  const handleToggle = () => {
    if (!disabled) {
      onChange(!checked);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleToggle();
    }
  };

  const CheckIcon = () => (
    <svg className={sizeStyles[size].icon} fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
    </svg>
  );

  const XIcon = () => (
    <svg className={sizeStyles[size].icon} fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  );

  return (
    <div className={`flex items-start space-x-3 ${className}`}>
      {/* Toggle Switch */}
      <motion.button
        className={`
          relative inline-flex ${sizeStyles[size].track} rounded-full
          transition-all duration-300 ease-out transform-gpu
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
        style={{
          background: checked 
            ? (typeof variantStyles[variant].trackOn === 'string' && variantStyles[variant].trackOn.startsWith('var(') 
                ? variantStyles[variant].trackOn 
                : variantStyles[variant].trackOn)
            : variantStyles[variant].trackOff,
          boxShadow: `
            inset 0 2px 4px rgba(0,0,0,0.1),
            ${(isHovered || isFocused) && checked && !disabled ? variantStyles[variant].glow : '0 0 0 transparent'}
          `,
          transform: `
            translateZ(${isHovered ? 4 : 0}px)
            scale(${isHovered ? 1.05 : 1})
          `
        }}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        disabled={disabled}
        role="switch"
        aria-checked={checked}
        aria-label={ariaLabel || label}
        aria-describedby={ariaDescribedBy}
        whileHover={!disabled ? { scale: 1.05 } : {}}
        whileTap={!disabled ? { scale: 0.95 } : {}}
      >
        {/* Track Glow Effect */}
        <AnimatePresence>
          {(isHovered || isFocused) && checked && !disabled && (
            <motion.div
              className="absolute inset-0 rounded-full pointer-events-none"
              style={{
                background: `radial-gradient(circle, ${variantStyles[variant].trackOn}40, transparent 70%)`
              }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1.2 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.2 }}
            />
          )}
        </AnimatePresence>

        {/* Thumb */}
        <motion.div
          className={`
            absolute top-0.5 left-0.5 ${sizeStyles[size].thumb} rounded-full
            flex items-center justify-center
            transition-all duration-300 ease-out transform-gpu
            border border-gray-200
          `}
          style={{
            background: variantStyles[variant].thumb,
            boxShadow: `
              var(--shadow-3d-sm),
              ${(isHovered || isFocused) && !disabled ? '0 0 10px rgba(0,0,0,0.2)' : ''}
            `,
            transform: `
              ${checked ? sizeStyles[size].translate : 'translate-x-0'}
              translateZ(${isHovered ? 2 : 0}px)
            `
          }}
          animate={{
            x: checked ? (size === 'sm' ? 20 : size === 'md' ? 24 : 28) : 0
          }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        >
          {/* Icons */}
          <AnimatePresence mode="wait">
            {showIcons && (
              <motion.div
                key={checked ? 'check' : 'x'}
                className={`
                  flex items-center justify-center
                  ${checked ? 'text-green-600' : 'text-gray-400'}
                `}
                initial={{ opacity: 0, scale: 0.5, rotate: -90 }}
                animate={{ opacity: 1, scale: 1, rotate: 0 }}
                exit={{ opacity: 0, scale: 0.5, rotate: 90 }}
                transition={{ duration: 0.2 }}
              >
                {checked ? <CheckIcon /> : <XIcon />}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Thumb Highlight */}
          <motion.div
            className="absolute inset-0 rounded-full pointer-events-none"
            style={{
              background: 'linear-gradient(135deg, rgba(255,255,255,0.3) 0%, transparent 50%)'
            }}
            animate={{
              opacity: isHovered ? 1 : 0.7
            }}
            transition={{ duration: 0.2 }}
          />
        </motion.div>

        {/* Track Icons */}
        {showIcons && (
          <>
            {/* Off Icon */}
            <motion.div
              className={`
                absolute left-1 top-1/2 transform -translate-y-1/2
                ${sizeStyles[size].icon} text-gray-500
                pointer-events-none
              `}
              animate={{
                opacity: checked ? 0 : 0.7,
                scale: checked ? 0.8 : 1
              }}
              transition={{ duration: 0.2 }}
            >
              <XIcon />
            </motion.div>

            {/* On Icon */}
            <motion.div
              className={`
                absolute right-1 top-1/2 transform -translate-y-1/2
                ${sizeStyles[size].icon} text-white
                pointer-events-none
              `}
              animate={{
                opacity: checked ? 0.7 : 0,
                scale: checked ? 1 : 0.8
              }}
              transition={{ duration: 0.2 }}
            >
              <CheckIcon />
            </motion.div>
          </>
        )}
      </motion.button>

      {/* Label and Description */}
      {(label || description) && (
        <div className="flex-1">
          {label && (
            <motion.label
              className={`
                block text-sm font-medium cursor-pointer
                ${disabled ? 'text-gray-400' : 'text-gray-900'}
              `}
              onClick={handleToggle}
              whileHover={!disabled ? { x: 2 } : {}}
              transition={{ type: "spring", stiffness: 400, damping: 25 }}
            >
              {label}
            </motion.label>
          )}
          {description && (
            <p className={`text-xs mt-1 ${disabled ? 'text-gray-300' : 'text-gray-500'}`}>
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Toggle3D