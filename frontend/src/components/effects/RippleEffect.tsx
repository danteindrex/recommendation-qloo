import React, { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface Ripple {
  id: number
  x: number
  y: number
  color: string
  size: number
}

interface RippleEffectProps {
  color?: string
  duration?: number
  maxSize?: number
  className?: string
  disabled?: boolean
  children?: React.ReactNode
}

const RippleEffect: React.FC<RippleEffectProps> = ({
  color = 'rgba(255, 255, 255, 0.6)',
  duration = 600,
  maxSize = 200,
  className = '',
  disabled = false,
  children
}) => {
  const [ripples, setRipples] = useState<Ripple[]>([])
  const rippleIdRef = React.useRef(0)

  const createRipple = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    if (disabled) return

    const element = event.currentTarget
    const rect = element.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    
    const newRipple: Ripple = {
      id: rippleIdRef.current++,
      x,
      y,
      color,
      size: maxSize
    }

    setRipples(prev => [...prev, newRipple])

    // Remove ripple after animation
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== newRipple.id))
    }, duration)
  }, [color, maxSize, duration, disabled])

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      onMouseDown={createRipple}
    >
      {children}
      
      <AnimatePresence>
        {ripples.map(ripple => (
          <motion.div
            key={ripple.id}
            className="absolute rounded-full pointer-events-none"
            style={{
              left: ripple.x,
              top: ripple.y,
              backgroundColor: ripple.color,
              transform: 'translate(-50%, -50%)'
            }}
            initial={{ width: 0, height: 0, opacity: 0.8 }}
            animate={{ 
              width: ripple.size, 
              height: ripple.size, 
              opacity: 0 
            }}
            exit={{ opacity: 0 }}
            transition={{ 
              duration: duration / 1000, 
              ease: "easeOut" 
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}

export default RippleEffect