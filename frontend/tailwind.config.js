/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'navy': {
          950: '#050811', // Darkest (Main BG)
          900: '#0a0f1e', // Deep Navy (Background)
          800: '#111827', // Lighter Navy (Panels)
        },
        'emerald': {
          500: '#10b981', // Success
        },
        'electric-blue': '#3b82f6', // System/Highlight (Simplified)
        'crimson': {
          500: '#ef4444', // Error
        }
      },
      fontFamily: {
        sans: ['Inter', 'Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
