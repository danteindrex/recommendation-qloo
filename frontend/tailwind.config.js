/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366F1', // Indigo 500
          light: '#818CF8', // Indigo 400
          dark: '#4338CA',  // Indigo 700
        },
        secondary: {
          DEFAULT: '#10B981', // Emerald 500
          light: '#34D399', // Emerald 400
          dark: '#059669',  // Emerald 700
        },
        accent: {
          DEFAULT: '#F59E0B', // Amber 500
          light: '#FCD34D', // Amber 300
          dark: '#D97706',  // Amber 700
        },
        neutral: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563',
          700: '#374151',
          800: '#1F2937',
          900: '#111827',
        },
      },
    },
  },
  plugins: [],
}