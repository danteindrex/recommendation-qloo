import React, { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Card3DProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'glass' | 'gradient' | 'elegant' | 'mesh'
  padding?: 'sm' | 'md' | 'lg' | 'xl'
  hover?: boolean
  depth?: number
  glowEffect?: boolean
  tiltEffect?: boolean
  borderGradient?: boolean
  interactive?: boolean
  animated?: boolean
  'aria-label'?: string
  onClick?: () => void
}

const Card3D: React.FC<Card3DProps> = ({
  children,
  className = '',
  variant = 'default',
  padding = 'md',
  hover = true,
  depth = 6,
  glowEffect = true,
  tiltEffect = true,
  borderGradient = false,
  interactive = false,
  animated = true,
  'aria-label': ariaLabel,
  onClick
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const baseStyles = `
    relative transition-all duration-300 ease-out transform-gpu
    ${interactive || onClick ? 'cursor-pointer' : ''}
    ${borderGradient ? 'p-[2px]' : ''}
  `;
  
  const variantStyles = {
    default: `
      background: white;
      border: 1px solid rgba(229, 231, 235, 1);
      box-shadow: var(--shadow-3d-lg);
      border-radius: var(--radius-elegant);
    `,
    glass: `
      background: var(--glass-background);
      backdrop-filter: var(--glass-backdrop);
      border: 1px solid var(--glass-border);
      box-shadow: var(--glass-shadow);
      border-radius: var(--radius-elegant);
    `,
    gradient: `
      background: var(--gradient-primary);
      color: white;
      box-shadow: var(--shadow-3d-xl), var(--shadow-glow-primary);
      border-radius: var(--radius-elegant);
    `,
    elegant: `
      background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.3);
      box-shadow: var(--shadow-3d-lg), 0 0 40px rgba(102, 126, 234, 0.1);
      border-radius: var(--radius-elegant-lg);
    `,
    mesh: `
      background: radial-gradient(at 40% 20%, hsla(28,100%,74%,0.1) 0%, transparent 50%),
                  radial-gradient(at 80% 0%, hsla(189,100%,56%,0.1) 0%, transparent 50%),
                  radial-gradient(at 0% 50%, hsla(355,100%,93%,0.1) 0%, transparent 50%);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255,255,255,0.2);
      box-shadow: var(--shadow-3d-lg);
      border-radius: var(--radius-elegant-lg);
    `
  };
  
  const paddingStyles = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10'
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!tiltEffect || !cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setMousePosition({ x, y });
  };

  const getTiltTransform = () => {
    if (!tiltEffect || !isHovered || !cardRef.current) return '';
    
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (mousePosition.y - centerY) / centerY * -10;
    const rotateY = (mousePosition.x - centerX) / centerX * 10;
    
    return `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(${depth}px)`;
  };

  const dynamicStyles = {
    transform: getTiltTransform() || `translateZ(${isHovered ? depth : 0}px)`,
    filter: `brightness(${isHovered ? 1.05 : 1})`,
    boxShadow: isHovered && hover ? 'var(--shadow-3d-xl)' : undefined
  };

  const Component = animated ? motion.div : 'div';
  const animationProps = animated
    ? {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.3 },
        whileHover: hover ? { scale: 1.02 } : {},
        whileTap: interactive || onClick ? { scale: 0.98 } : {}
      }
    : {};

  const cardContent = (
    <Component
      ref={cardRef}
      className={`
        ${baseStyles}
        ${paddingStyles[padding]}
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
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
      onClick={onClick}
      aria-label={ariaLabel}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      {...animationProps}
    >
      {/* Glow Effect */}
      <AnimatePresence>
        {isHovered && glowEffect && (
          <motion.div
            className="absolute inset-0 rounded-[inherit] opacity-20 pointer-events-none"
            style={{
              background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, var(--particle-primary), transparent 70%)`
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.2 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </AnimatePresence>

      {/* Shimmer Effect */}
      {isHovered && variant === 'elegant' && (
        <motion.div
          className="absolute inset-0 rounded-[inherit] pointer-events-none overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
            initial={{ x: '-100%' }}
            animate={{ x: '100%' }}
            transition={{ duration: 1.5, ease: "easeInOut" }}
          />
        </motion.div>
      )}

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>

      {/* Interactive Highlight */}
      {(interactive || onClick) && isHovered && (
        <motion.div
          className="absolute inset-0 rounded-[inherit] border-2 border-transparent pointer-events-none"
          style={{
            background: `linear-gradient(135deg, var(--particle-primary), var(--particle-accent)) border-box`,
            WebkitMask: 'linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'exclude'
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.6 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
        />
      )}
    </Component>
  );

  // Wrap with gradient border if enabled
  if (borderGradient) {
    return (
      <div
        className="rounded-[inherit] p-[2px]"
        style={{
          background: 'var(--gradient-primary)',
          borderRadius: 'var(--radius-elegant-lg)'
        }}
      >
        <div
          className="rounded-[inherit] bg-white"
          style={{
            borderRadius: 'calc(var(--radius-elegant-lg) - 2px)'
          }}
        >
          {cardContent}
        </div>
      </div>
    );
  }

  return cardContent;
};

export default Card3D