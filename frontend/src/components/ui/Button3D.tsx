import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  color: string;
}

interface Button3DProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'glass' | 'gradient'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  loading?: boolean
  className?: string
  type?: 'button' | 'submit' | 'reset'
  fullWidth?: boolean
  icon?: React.ReactNode
  iconPosition?: 'left' | 'right'
  depth?: number
  glowIntensity?: number
  particleEffect?: boolean
  rippleAnimation?: boolean
  hoverTransform?: boolean
  'aria-label'?: string
  'aria-describedby'?: string
}

const Button3D: React.FC<Button3DProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  type = 'button',
  fullWidth = false,
  icon,
  iconPosition = 'left',
  depth = 8,
  glowIntensity = 0.3,
  particleEffect = true,
  rippleAnimation = true,
  hoverTransform = true,
  'aria-label': ariaLabel,
  'aria-describedby': ariaDescribedBy
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [particles, setParticles] = useState<Particle[]>([]);
  const [ripples, setRipples] = useState<Array<{ id: number; x: number; y: number }>>([]);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const particleIdRef = useRef(0);
  const rippleIdRef = useRef(0);

  const baseStyles = `
    relative inline-flex items-center justify-center font-medium 
    transition-all duration-300 ease-out focus:outline-none 
    transform-gpu perspective-1000 preserve-3d overflow-hidden
    border-0 cursor-pointer select-none
  `;
  
  const variantStyles = {
    primary: `
      background: var(--gradient-primary);
      color: white;
      box-shadow: var(--shadow-3d-lg), var(--shadow-glow-primary);
      border-radius: var(--radius-elegant);
    `,
    secondary: `
      background: var(--gradient-secondary);
      color: white;
      box-shadow: var(--shadow-3d-lg), var(--shadow-glow-secondary);
      border-radius: var(--radius-elegant);
    `,
    accent: `
      background: var(--gradient-accent);
      color: white;
      box-shadow: var(--shadow-3d-lg), var(--shadow-glow-accent);
      border-radius: var(--radius-elegant);
    `,
    outline: `
      background: transparent;
      color: var(--particle-primary);
      border: 2px solid var(--particle-primary);
      box-shadow: var(--shadow-3d-md);
      border-radius: var(--radius-elegant);
    `,
    glass: `
      background: var(--glass-background);
      backdrop-filter: var(--glass-backdrop);
      border: 1px solid var(--glass-border);
      color: white;
      box-shadow: var(--glass-shadow);
      border-radius: var(--radius-elegant);
    `,
    gradient: `
      background: linear-gradient(135deg, var(--particle-primary), var(--particle-secondary), var(--particle-accent));
      background-size: 200% 200%;
      animation: gradient-shift 4s ease infinite;
      color: white;
      box-shadow: var(--shadow-3d-xl);
      border-radius: var(--radius-elegant);
    `
  };
  
  const sizeStyles = {
    sm: 'px-4 py-2 text-sm min-h-[36px]',
    md: 'px-6 py-3 text-base min-h-[44px]',
    lg: 'px-8 py-4 text-lg min-h-[52px]',
    xl: 'px-10 py-5 text-xl min-h-[60px]'
  };

  const isDisabled = disabled || loading;

  // Particle system
  const createParticles = (x: number, y: number) => {
    if (!particleEffect || isDisabled) return;
    
    const newParticles: Particle[] = [];
    const particleCount = 8;
    
    for (let i = 0; i < particleCount; i++) {
      newParticles.push({
        id: particleIdRef.current++,
        x,
        y,
        vx: (Math.random() - 0.5) * 4,
        vy: (Math.random() - 0.5) * 4,
        life: 1,
        maxLife: 1,
        color: variant === 'primary' ? 'var(--particle-primary)' : 
               variant === 'secondary' ? 'var(--particle-secondary)' : 
               'var(--particle-accent)'
      });
    }
    
    setParticles(prev => [...prev, ...newParticles]);
  };

  // Ripple effect
  const createRipple = (e: React.MouseEvent) => {
    if (!rippleAnimation || isDisabled) return;
    
    const rect = buttonRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const newRipple = {
      id: rippleIdRef.current++,
      x,
      y
    };
    
    setRipples(prev => [...prev, newRipple]);
    
    // Remove ripple after animation
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== newRipple.id));
    }, 600);
  };

  // Handle click with effects
  const handleClick = (e: React.MouseEvent) => {
    if (isDisabled) return;
    
    createRipple(e);
    
    if (particleEffect) {
      const rect = buttonRef.current?.getBoundingClientRect();
      if (rect) {
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        createParticles(x, y);
      }
    }
    
    onClick?.();
  };

  // Animate particles
  useEffect(() => {
    if (particles.length === 0) return;
    
    const interval = setInterval(() => {
      setParticles(prev => 
        prev.map(particle => ({
          ...particle,
          x: particle.x + particle.vx,
          y: particle.y + particle.vy,
          life: particle.life - 0.02,
          vy: particle.vy + 0.1 // gravity
        })).filter(particle => particle.life > 0)
      );
    }, 16);
    
    return () => clearInterval(interval);
  }, [particles.length]);

  // Dynamic styles based on state
  const dynamicStyles = {
    transform: `
      translateZ(${isPressed ? depth / 2 : depth}px)
      ${hoverTransform && isHovered ? 'rotateX(-5deg) rotateY(5deg)' : ''}
      ${isPressed ? 'scale(0.98)' : isHovered ? 'scale(1.02)' : 'scale(1)'}
    `,
    filter: `
      brightness(${isHovered ? 1.1 : 1})
      ${isFocused ? `drop-shadow(0 0 ${glowIntensity * 20}px var(--color-focus-ring))` : ''}
    `,
    boxShadow: `
      ${variantStyles[variant].includes('box-shadow') ? '' : 'var(--shadow-3d-lg)'}
      ${isHovered ? ', var(--shadow-3d-xl)' : ''}
      ${isFocused ? ', 0 0 0 3px var(--color-focus-ring)' : ''}
    `
  };

  return (
    <motion.button
      ref={buttonRef}
      type={type}
      onClick={handleClick}
      disabled={isDisabled}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedBy}
      className={`
        ${baseStyles}
        ${sizeStyles[size]}
        ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      style={{
        ...dynamicStyles,
        ...Object.fromEntries(
          variantStyles[variant]
            .split(';')
            .map(rule => rule.trim())
            .filter(rule => rule)
            .map(rule => {
              const [property, value] = rule.split(':').map(s => s.trim());
              return [property.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase()), value];
            })
        )
      }}
      initial={{ scale: 1 }}
      whileHover={!isDisabled && hoverTransform ? { scale: 1.02 } : {}}
      whileTap={!isDisabled ? { scale: 0.98 } : {}}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      {/* Ripple Effects */}
      <AnimatePresence>
        {ripples.map(ripple => (
          <motion.div
            key={ripple.id}
            className="absolute rounded-full bg-white/30 pointer-events-none"
            style={{
              left: ripple.x,
              top: ripple.y,
              transform: 'translate(-50%, -50%)'
            }}
            initial={{ width: 0, height: 0, opacity: 0.8 }}
            animate={{ width: 200, height: 200, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          />
        ))}
      </AnimatePresence>

      {/* Particle Effects */}
      <AnimatePresence>
        {particles.map(particle => (
          <motion.div
            key={particle.id}
            className="absolute w-1 h-1 rounded-full pointer-events-none"
            style={{
              left: particle.x,
              top: particle.y,
              backgroundColor: particle.color,
              opacity: particle.life
            }}
            initial={{ scale: 1 }}
            animate={{ scale: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          />
        ))}
      </AnimatePresence>

      {/* Button Content */}
      <span className="relative z-10 flex items-center justify-center">
        {loading ? (
          <span className="flex items-center">
            <motion.div
              className="w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-2"
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            />
            Loading...
          </span>
        ) : (
          <>
            {icon && iconPosition === 'left' && (
              <span className="mr-2 flex items-center">{icon}</span>
            )}
            {children}
            {icon && iconPosition === 'right' && (
              <span className="ml-2 flex items-center">{icon}</span>
            )}
          </>
        )}
      </span>

      {/* Hover Glow Effect */}
      {isHovered && !isDisabled && (
        <motion.div
          className="absolute inset-0 rounded-[inherit] opacity-20 pointer-events-none"
          style={{
            background: `radial-gradient(circle at center, ${
              variant === 'primary' ? 'var(--particle-primary)' :
              variant === 'secondary' ? 'var(--particle-secondary)' :
              'var(--particle-accent)'
            }, transparent 70%)`
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.2 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        />
      )}
    </motion.button>
  );
};

export default Button3D