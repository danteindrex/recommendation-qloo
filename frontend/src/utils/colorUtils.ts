// Color manipulation and palette generation utilities

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface GradientCollection {
  primary: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ColorTheme {
  name: string;
  palette: ColorPalette;
  gradients: GradientCollection;
  particles: ParticleColors;
  backgrounds: BackgroundColors;
  interactive: InteractiveColors;
}

export interface ParticleColors {
  primary: string;
  secondary: string;
  accent: string;
  success: string;
  warning: string;
  error: string;
}

export interface BackgroundColors {
  primary: string;
  secondary: string;
  glass: string;
  mesh: string;
}

export interface InteractiveColors {
  hover: string;
  active: string;
  focus: string;
  selection: string;
}

// HSL color manipulation
export const hslToHex = (h: number, s: number, l: number): string => {
  l /= 100;
  const a = s * Math.min(l, 1 - l) / 100;
  const f = (n: number) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color).toString(16).padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
};

export const hexToHsl = (hex: string): [number, number, number] => {
  const r = parseInt(hex.slice(1, 3), 16) / 255;
  const g = parseInt(hex.slice(3, 5), 16) / 255;
  const b = parseInt(hex.slice(5, 7), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h = 0, s = 0, l = (max + min) / 2;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case r: h = (g - b) / d + (g < b ? 6 : 0); break;
      case g: h = (b - r) / d + 2; break;
      case b: h = (r - g) / d + 4; break;
    }
    h /= 6;
  }

  return [h * 360, s * 100, l * 100];
};

// Generate complementary colors
export const generateComplementaryColor = (baseColor: string): string => {
  const [h, s, l] = hexToHsl(baseColor);
  const complementaryHue = (h + 180) % 360;
  return hslToHex(complementaryHue, s, l);
};

// Generate analogous colors
export const generateAnalogousColors = (baseColor: string, count: number = 3): string[] => {
  const [h, s, l] = hexToHsl(baseColor);
  const colors: string[] = [];
  const step = 30; // 30 degrees apart
  
  for (let i = 0; i < count; i++) {
    const newHue = (h + (i * step)) % 360;
    colors.push(hslToHex(newHue, s, l));
  }
  
  return colors;
};

// Generate triadic colors
export const generateTriadicColors = (baseColor: string): string[] => {
  const [h, s, l] = hexToHsl(baseColor);
  return [
    baseColor,
    hslToHex((h + 120) % 360, s, l),
    hslToHex((h + 240) % 360, s, l)
  ];
};

// Generate elegant gradient
export const generateElegantGradient = (color1: string, color2: string, angle: number = 135): string => {
  return `linear-gradient(${angle}deg, ${color1} 0%, ${color2} 100%)`;
};

// Generate cultural category colors
export const generateCulturalColors = (category: string): string => {
  const categoryColors: Record<string, string> = {
    music: 'linear-gradient(135deg, #ff6b6b 0%, #feca57 100%)',
    'visual-arts': 'linear-gradient(135deg, #48cae4 0%, #023e8a 100%)',
    cuisine: 'linear-gradient(135deg, #f72585 0%, #b5179e 100%)',
    literature: 'linear-gradient(135deg, #7209b7 0%, #480ca8 100%)',
    social: 'linear-gradient(135deg, #f77f00 0%, #fcbf49 100%)',
    technology: 'linear-gradient(135deg, #06ffa5 0%, #00d4aa 100%)',
  };
  
  return categoryColors[category] || categoryColors.social;
};

// Color accessibility utilities
export const getContrastRatio = (color1: string, color2: string): number => {
  const getLuminance = (color: string): number => {
    const [h, s, l] = hexToHsl(color);
    return l / 100;
  };
  
  const lum1 = getLuminance(color1);
  const lum2 = getLuminance(color2);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  
  return (brightest + 0.05) / (darkest + 0.05);
};

export const isAccessible = (foreground: string, background: string, level: 'AA' | 'AAA' = 'AA'): boolean => {
  const ratio = getContrastRatio(foreground, background);
  return level === 'AA' ? ratio >= 4.5 : ratio >= 7;
};

// Dynamic theme generation
export const generateDynamicTheme = (baseColor: string): ColorTheme => {
  const [h, s, l] = hexToHsl(baseColor);
  
  // Generate palette
  const palette: ColorPalette = {
    primary: baseColor,
    secondary: hslToHex((h + 60) % 360, s, l),
    accent: hslToHex((h + 120) % 360, s, l),
    success: hslToHex(120, 70, 50),
    warning: hslToHex(45, 90, 60),
    error: hslToHex(0, 80, 60),
    info: hslToHex(200, 80, 60)
  };
  
  // Generate gradients
  const gradients: GradientCollection = {
    primary: generateElegantGradient(baseColor, hslToHex(h, s, l - 10)),
    secondary: generateElegantGradient(palette.secondary, hslToHex((h + 60) % 360, s, l - 10)),
    accent: generateElegantGradient(palette.accent, hslToHex((h + 120) % 360, s, l - 10)),
    success: generateElegantGradient(palette.success, hslToHex(120, 70, 40)),
    warning: generateElegantGradient(palette.warning, hslToHex(45, 90, 50)),
    error: generateElegantGradient(palette.error, hslToHex(0, 80, 50)),
    info: generateElegantGradient(palette.info, hslToHex(200, 80, 50))
  };
  
  return {
    name: 'dynamic',
    palette,
    gradients,
    particles: {
      primary: baseColor,
      secondary: palette.secondary,
      accent: palette.accent,
      success: palette.success,
      warning: palette.warning,
      error: palette.error
    },
    backgrounds: {
      primary: `radial-gradient(circle at 50% 50%, ${baseColor}20 0%, transparent 70%)`,
      secondary: `radial-gradient(circle at 50% 50%, ${palette.secondary}20 0%, transparent 70%)`,
      glass: 'rgba(255, 255, 255, 0.1)',
      mesh: 'radial-gradient(at 40% 20%, hsla(28,100%,74%,1) 0px, transparent 50%)'
    },
    interactive: {
      hover: `${baseColor}30`,
      active: `${baseColor}50`,
      focus: `${palette.accent}40`,
      selection: `${palette.secondary}20`
    }
  };
};

// Color transition utilities
export const interpolateColor = (color1: string, color2: string, factor: number): string => {
  const [h1, s1, l1] = hexToHsl(color1);
  const [h2, s2, l2] = hexToHsl(color2);
  
  const h = h1 + factor * (h2 - h1);
  const s = s1 + factor * (s2 - s1);
  const l = l1 + factor * (l2 - l1);
  
  return hslToHex(h, s, l);
};

export const createColorTransition = (colors: string[], steps: number): string[] => {
  const result: string[] = [];
  const segmentSteps = Math.floor(steps / (colors.length - 1));
  
  for (let i = 0; i < colors.length - 1; i++) {
    for (let j = 0; j < segmentSteps; j++) {
      const factor = j / segmentSteps;
      result.push(interpolateColor(colors[i], colors[i + 1], factor));
    }
  }
  
  result.push(colors[colors.length - 1]);
  return result;
};

// Predefined elegant themes
export const elegantThemes: Record<string, ColorTheme> = {
  aurora: generateDynamicTheme('#667eea'),
  sunset: generateDynamicTheme('#f093fb'),
  ocean: generateDynamicTheme('#4facfe'),
  forest: generateDynamicTheme('#43e97b'),
  cosmic: generateDynamicTheme('#764ba2'),
  fire: generateDynamicTheme('#ff6b6b')
};

export default {
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
  createColorTransition,
  elegantThemes
};