import React, { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Modal3DProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  variant?: 'default' | 'glass' | 'elegant' | 'gradient'
  closeOnOverlayClick?: boolean
  closeOnEscape?: boolean
  showCloseButton?: boolean
  depth?: number
  blurIntensity?: number
  'aria-labelledby'?: string
  'aria-describedby'?: string
}

const Modal3D: React.FC<Modal3DProps> = ({
  isOpen,
  onClose,
  children,
  title,
  size = 'md',
  variant = 'elegant',
  closeOnOverlayClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  depth = 20,
  blurIntensity = 12,
  'aria-labelledby': ariaLabelledBy,
  'aria-describedby': ariaDescribedBy
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-[95vw] max-h-[95vh]'
  };

  const variantStyles = {
    default: `
      background: white;
      border: 1px solid rgba(229, 231, 235, 1);
      box-shadow: var(--shadow-3d-xl);
    `,
    glass: `
      background: var(--glass-background);
      backdrop-filter: var(--glass-backdrop-strong);
      border: 1px solid var(--glass-border);
      box-shadow: var(--glass-shadow);
    `,
    elegant: `
      background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
      backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.3);
      box-shadow: var(--shadow-3d-xl), 0 0 60px rgba(102, 126, 234, 0.2);
    `,
    gradient: `
      background: var(--gradient-primary);
      color: white;
      box-shadow: var(--shadow-3d-xl), var(--shadow-glow-primary);
    `
  };

  // Handle escape key
  useEffect(() => {
    if (!closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose, closeOnEscape]);

  // Focus management
  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && closeOnOverlayClick) {
      onClose();
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!modalRef.current) return;
    
    const rect = modalRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    setMousePosition({ x, y });
  };

  const backdropVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { duration: 0.3 }
    },
    exit: { 
      opacity: 0,
      transition: { duration: 0.2 }
    }
  };

  const modalVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8, 
      y: 50,
      rotateX: -15
    },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      rotateX: 0,
      transition: { 
        type: 'spring', 
        damping: 25, 
        stiffness: 300,
        duration: 0.4
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.8, 
      y: 50,
      rotateX: -15,
      transition: { duration: 0.2 }
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          variants={backdropVariants}
          initial="hidden"
          animate="visible"
          exit="exit"
          onClick={handleOverlayClick}
          role="dialog"
          aria-modal="true"
          aria-labelledby={ariaLabelledBy || (title ? 'modal-title' : undefined)}
          aria-describedby={ariaDescribedBy}
        >
          {/* Enhanced Backdrop */}
          <motion.div
            className="absolute inset-0"
            style={{
              background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(102, 126, 234, 0.1), rgba(0, 0, 0, 0.6))`,
              backdropFilter: `blur(${blurIntensity}px)`
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />
          
          {/* Modal Container */}
          <motion.div
            ref={modalRef}
            className={`
              relative w-full ${sizeClasses[size]} max-h-[90vh] 
              transform-gpu perspective-1000 preserve-3d
              focus:outline-none
            `}
            style={{
              transform: `translateZ(${depth}px)`,
              borderRadius: 'var(--radius-elegant-lg)',
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
            variants={modalVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            onMouseMove={handleMouseMove}
            tabIndex={-1}
          >
            {/* Glow Effect */}
            <motion.div
              className="absolute inset-0 rounded-[inherit] opacity-10 pointer-events-none"
              style={{
                background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, var(--particle-primary), transparent 70%)`
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.1 }}
              transition={{ duration: 0.3 }}
            />

            {/* Header */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between p-6 border-b border-white/20">
                {title && (
                  <h2 
                    id="modal-title"
                    className={`text-xl font-semibold ${
                      variant === 'gradient' ? 'text-white' : 'text-gray-900'
                    }`}
                  >
                    {title}
                  </h2>
                )}
                {showCloseButton && (
                  <motion.button
                    onClick={onClose}
                    className={`
                      p-2 rounded-lg transition-all duration-200
                      ${variant === 'gradient' 
                        ? 'text-white/70 hover:text-white hover:bg-white/10' 
                        : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                      }
                    `}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    aria-label="Close modal"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </motion.button>
                )}
              </div>
            )}
            
            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)] relative z-10">
              {children}
            </div>

            {/* Shimmer Effect for elegant variant */}
            {variant === 'elegant' && (
              <motion.div
                className="absolute inset-0 rounded-[inherit] pointer-events-none overflow-hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                  initial={{ x: '-100%' }}
                  animate={{ x: '100%' }}
                  transition={{ 
                    duration: 2, 
                    ease: "easeInOut",
                    repeat: Infinity,
                    repeatDelay: 3
                  }}
                />
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default Modal3D