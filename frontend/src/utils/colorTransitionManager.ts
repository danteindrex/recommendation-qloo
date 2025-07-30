// Color Transition Manager for smooth theme changes and interaction feedback

import { interpolateColor, createColorTransition, ColorTheme } from './colorUtils'

export interface TransitionConfig {
  duration: number
  easing: string
  property: string
  fromValue: string
  toValue: string
}

export interface ColorTransitionState {
  isTransitioning: boolean
  progress: number
  currentColor: string
  targetColor: string
}

export class ColorTransitionManager {
  private transitions: Map<string, ColorTransitionState> = new Map()
  private animationFrames: Map<string, number> = new Map()
  private callbacks: Map<string, (color: string) => void> = new Map()

  // Start a color transition
  startTransition(
    id: string,
    fromColor: string,
    toColor: string,
    duration: number = 300,
    callback?: (color: string) => void
  ): void {
    // Cancel existing transition
    this.cancelTransition(id)

    // Set up new transition
    this.transitions.set(id, {
      isTransitioning: true,
      progress: 0,
      currentColor: fromColor,
      targetColor: toColor
    })

    if (callback) {
      this.callbacks.set(id, callback)
    }

    const startTime = Date.now()
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      const currentColor = interpolateColor(fromColor, toColor, this.easeInOutCubic(progress))
      
      // Update state
      const state = this.transitions.get(id)
      if (state) {
        state.progress = progress
        state.currentColor = currentColor
        this.transitions.set(id, state)
      }

      // Call callback
      const cb = this.callbacks.get(id)
      if (cb) {
        cb(currentColor)
      }

      if (progress < 1) {
        const frameId = requestAnimationFrame(animate)
        this.animationFrames.set(id, frameId)
      } else {
        this.completeTransition(id)
      }
    }

    const frameId = requestAnimationFrame(animate)
    this.animationFrames.set(id, frameId)
  }

  // Cancel a transition
  cancelTransition(id: string): void {
    const frameId = this.animationFrames.get(id)
    if (frameId) {
      cancelAnimationFrame(frameId)
      this.animationFrames.delete(id)
    }
    
    this.transitions.delete(id)
    this.callbacks.delete(id)
  }

  // Complete a transition
  private completeTransition(id: string): void {
    const state = this.transitions.get(id)
    if (state) {
      state.isTransitioning = false
      state.progress = 1
      state.currentColor = state.targetColor
      this.transitions.set(id, state)
    }

    this.animationFrames.delete(id)
    this.callbacks.delete(id)
  }

  // Get current transition state
  getTransitionState(id: string): ColorTransitionState | null {
    return this.transitions.get(id) || null
  }

  // Check if transition is active
  isTransitioning(id: string): boolean {
    const state = this.transitions.get(id)
    return state?.isTransitioning || false
  }

  // Get current color
  getCurrentColor(id: string): string | null {
    const state = this.transitions.get(id)
    return state?.currentColor || null
  }

  // Easing functions
  private easeInOutCubic(t: number): number {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
  }

  private easeOutQuart(t: number): number {
    return 1 - Math.pow(1 - t, 4)
  }

  private easeInOutQuart(t: number): number {
    return t < 0.5 ? 8 * t * t * t * t : 1 - Math.pow(-2 * t + 2, 4) / 2
  }

  // Batch transition multiple colors
  startBatchTransition(
    transitions: Array<{
      id: string
      fromColor: string
      toColor: string
      callback?: (color: string) => void
    }>,
    duration: number = 300
  ): void {
    transitions.forEach(({ id, fromColor, toColor, callback }) => {
      this.startTransition(id, fromColor, toColor, duration, callback)
    })
  }

  // Create smooth color sequence
  createColorSequence(
    id: string,
    colors: string[],
    stepDuration: number = 300,
    callback?: (color: string) => void
  ): void {
    if (colors.length < 2) return

    let currentIndex = 0
    
    const nextTransition = () => {
      if (currentIndex < colors.length - 1) {
        this.startTransition(
          id,
          colors[currentIndex],
          colors[currentIndex + 1],
          stepDuration,
          (color) => {
            if (callback) callback(color)
            
            // Check if this transition is complete
            const state = this.getTransitionState(id)
            if (state && !state.isTransitioning) {
              currentIndex++
              setTimeout(nextTransition, 50) // Small delay between transitions
            }
          }
        )
      }
    }

    nextTransition()
  }

  // Cleanup all transitions
  cleanup(): void {
    this.animationFrames.forEach(frameId => cancelAnimationFrame(frameId))
    this.transitions.clear()
    this.animationFrames.clear()
    this.callbacks.clear()
  }
}

// Theme transition manager for switching between themes
export class ThemeTransitionManager {
  private colorManager = new ColorTransitionManager()
  private currentTheme: ColorTheme | null = null

  // Transition to new theme
  transitionToTheme(
    newTheme: ColorTheme,
    duration: number = 500,
    onComplete?: () => void
  ): void {
    if (!this.currentTheme) {
      this.currentTheme = newTheme
      if (onComplete) onComplete()
      return
    }

    const transitions: Array<{
      id: string
      fromColor: string
      toColor: string
      callback: (color: string) => void
    }> = []

    // Transition primary colors
    Object.keys(newTheme.palette).forEach(key => {
      const fromColor = (this.currentTheme!.palette as any)[key]
      const toColor = (newTheme.palette as any)[key]
      
      if (fromColor !== toColor) {
        transitions.push({
          id: `palette-${key}`,
          fromColor,
          toColor,
          callback: (color) => {
            document.documentElement.style.setProperty(`--color-${key}`, color)
          }
        })
      }
    })

    // Transition gradients
    Object.keys(newTheme.gradients).forEach(key => {
      const fromGradient = (this.currentTheme!.gradients as any)[key]
      const toGradient = (newTheme.gradients as any)[key]
      
      if (fromGradient !== toGradient) {
        // For gradients, we'll transition the CSS custom property directly
        document.documentElement.style.setProperty(`--gradient-${key}`, toGradient)
      }
    })

    this.colorManager.startBatchTransition(transitions, duration)
    this.currentTheme = newTheme

    if (onComplete) {
      setTimeout(onComplete, duration)
    }
  }

  // Get current theme
  getCurrentTheme(): ColorTheme | null {
    return this.currentTheme
  }

  // Cleanup
  cleanup(): void {
    this.colorManager.cleanup()
  }
}

// Global instances
export const globalColorTransitionManager = new ColorTransitionManager()
export const globalThemeTransitionManager = new ThemeTransitionManager()

// React hook for color transitions
export const useColorTransition = () => {
  const [transitionStates, setTransitionStates] = React.useState<Map<string, ColorTransitionState>>(new Map())

  const startTransition = React.useCallback((
    id: string,
    fromColor: string,
    toColor: string,
    duration: number = 300
  ) => {
    globalColorTransitionManager.startTransition(
      id,
      fromColor,
      toColor,
      duration,
      (color) => {
        setTransitionStates(prev => {
          const newMap = new Map(prev)
          const state = globalColorTransitionManager.getTransitionState(id)
          if (state) {
            newMap.set(id, state)
          }
          return newMap
        })
      }
    )
  }, [])

  const cancelTransition = React.useCallback((id: string) => {
    globalColorTransitionManager.cancelTransition(id)
    setTransitionStates(prev => {
      const newMap = new Map(prev)
      newMap.delete(id)
      return newMap
    })
  }, [])

  const getCurrentColor = React.useCallback((id: string) => {
    return globalColorTransitionManager.getCurrentColor(id)
  }, [])

  const isTransitioning = React.useCallback((id: string) => {
    return globalColorTransitionManager.isTransitioning(id)
  }, [])

  return {
    startTransition,
    cancelTransition,
    getCurrentColor,
    isTransitioning,
    transitionStates
  }
}

// React hook for theme transitions
export const useThemeTransition = () => {
  const [currentTheme, setCurrentTheme] = React.useState<ColorTheme | null>(null)
  const [isTransitioning, setIsTransitioning] = React.useState(false)

  const transitionToTheme = React.useCallback((
    newTheme: ColorTheme,
    duration: number = 500
  ) => {
    setIsTransitioning(true)
    globalThemeTransitionManager.transitionToTheme(
      newTheme,
      duration,
      () => {
        setCurrentTheme(newTheme)
        setIsTransitioning(false)
      }
    )
  }, [])

  React.useEffect(() => {
    setCurrentTheme(globalThemeTransitionManager.getCurrentTheme())
  }, [])

  return {
    currentTheme,
    isTransitioning,
    transitionToTheme
  }
}

export default ColorTransitionManager