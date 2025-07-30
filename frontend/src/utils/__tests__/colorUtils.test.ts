import { describe, it, expect } from 'vitest'
import {
  hslToHex,
  hexToHsl,
  generateComplementaryColor,
  generateAnalogousColors,
  generateTriadicColors,
  generateElegantGradient,
  generateCulturalColors,
  getContrastRatio,
  isAccessible,
  generateDynamicTheme,
  interpolateColor,
  createColorTransition
} from '../colorUtils'

describe('colorUtils', () => {
  describe('hslToHex', () => {
    it('converts HSL to hex correctly', () => {
      expect(hslToHex(0, 100, 50)).toBe('#ff0000') // Red
      expect(hslToHex(120, 100, 50)).toBe('#00ff00') // Green
      expect(hslToHex(240, 100, 50)).toBe('#0000ff') // Blue
      expect(hslToHex(0, 0, 0)).toBe('#000000') // Black
      expect(hslToHex(0, 0, 100)).toBe('#ffffff') // White
    })
  })

  describe('hexToHsl', () => {
    it('converts hex to HSL correctly', () => {
      const [h, s, l] = hexToHsl('#ff0000')
      expect(h).toBeCloseTo(0, 1)
      expect(s).toBeCloseTo(100, 1)
      expect(l).toBeCloseTo(50, 1)
    })

    it('handles different hex formats', () => {
      const [h1, s1, l1] = hexToHsl('#FF0000')
      const [h2, s2, l2] = hexToHsl('#ff0000')
      
      expect(h1).toBeCloseTo(h2, 1)
      expect(s1).toBeCloseTo(s2, 1)
      expect(l1).toBeCloseTo(l2, 1)
    })
  })

  describe('generateComplementaryColor', () => {
    it('generates complementary color correctly', () => {
      const red = '#ff0000'
      const complementary = generateComplementaryColor(red)
      const [h] = hexToHsl(complementary)
      
      // Complementary of red (0°) should be cyan (180°)
      expect(h).toBeCloseTo(180, 1)
    })
  })

  describe('generateAnalogousColors', () => {
    it('generates analogous colors', () => {
      const baseColor = '#ff0000'
      const analogous = generateAnalogousColors(baseColor, 3)
      
      expect(analogous).toHaveLength(3)
      expect(analogous[0]).toBe(baseColor)
    })
  })

  describe('generateTriadicColors', () => {
    it('generates triadic colors', () => {
      const baseColor = '#ff0000'
      const triadic = generateTriadicColors(baseColor)
      
      expect(triadic).toHaveLength(3)
      expect(triadic[0]).toBe(baseColor)
      
      // Check that the colors are 120° apart
      const [h1] = hexToHsl(triadic[1])
      const [h2] = hexToHsl(triadic[2])
      
      expect(h1).toBeCloseTo(120, 1)
      expect(h2).toBeCloseTo(240, 1)
    })
  })

  describe('generateElegantGradient', () => {
    it('generates CSS gradient string', () => {
      const gradient = generateElegantGradient('#ff0000', '#00ff00', 45)
      
      expect(gradient).toBe('linear-gradient(45deg, #ff0000 0%, #00ff00 100%)')
    })

    it('uses default angle when not provided', () => {
      const gradient = generateElegantGradient('#ff0000', '#00ff00')
      
      expect(gradient).toBe('linear-gradient(135deg, #ff0000 0%, #00ff00 100%)')
    })
  })

  describe('generateCulturalColors', () => {
    it('returns correct gradient for known categories', () => {
      expect(generateCulturalColors('music')).toBe('linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)')
      expect(generateCulturalColors('technology')).toBe('linear-gradient(135deg, #06ffa5 0%, #00d4aa 100%)')
    })

    it('returns default gradient for unknown categories', () => {
      const defaultGradient = 'linear-gradient(135deg, #f77f00 0%, #fcbf49 100%)'
      expect(generateCulturalColors('unknown')).toBe(defaultGradient)
    })
  })

  describe('getContrastRatio', () => {
    it('calculates contrast ratio correctly', () => {
      const ratio = getContrastRatio('#000000', '#ffffff')
      expect(ratio).toBeGreaterThan(1)
      
      const sameColorRatio = getContrastRatio('#ff0000', '#ff0000')
      expect(sameColorRatio).toBe(1)
    })
  })

  describe('isAccessible', () => {
    it('checks accessibility correctly for AA level', () => {
      expect(isAccessible('#000000', '#ffffff', 'AA')).toBe(true)
      expect(isAccessible('#ffffff', '#ffffff', 'AA')).toBe(false)
    })

    it('checks accessibility correctly for AAA level', () => {
      expect(isAccessible('#000000', '#ffffff', 'AAA')).toBe(true)
    })
  })

  describe('generateDynamicTheme', () => {
    it('generates a complete theme object', () => {
      const theme = generateDynamicTheme('#667eea')
      
      expect(theme).toHaveProperty('name', 'dynamic')
      expect(theme).toHaveProperty('palette')
      expect(theme).toHaveProperty('gradients')
      expect(theme).toHaveProperty('particles')
      expect(theme).toHaveProperty('backgrounds')
      expect(theme).toHaveProperty('interactive')
      
      expect(theme.palette.primary).toBe('#667eea')
    })
  })

  describe('interpolateColor', () => {
    it('interpolates between two colors', () => {
      const color1 = '#ff0000'
      const color2 = '#00ff00'
      
      const midpoint = interpolateColor(color1, color2, 0.5)
      expect(midpoint).toBeDefined()
      
      const start = interpolateColor(color1, color2, 0)
      expect(start).toBe(color1)
      
      const end = interpolateColor(color1, color2, 1)
      expect(end).toBe(color2)
    })
  })

  describe('createColorTransition', () => {
    it('creates color transition array', () => {
      const colors = ['#ff0000', '#00ff00', '#0000ff']
      const transition = createColorTransition(colors, 6)
      
      expect(transition.length).toBeGreaterThanOrEqual(6)
      expect(transition[0]).toBe('#ff0000')
      expect(transition[transition.length - 1]).toBe('#0000ff')
    })
  })
})