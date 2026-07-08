/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        idbi: {
          primary: '#00857C',    // IDBI Teal/Green
          secondary: '#006B64',  // Darker teal
          accent: '#E87722',     // IDBI Orange
          gold: '#F5A623',       // Gold/amber
          light: '#E6F5F3',      // Light teal background
          orange: '#E87722',     // Primary orange
          'orange-light': '#FEF3E8', // Light orange bg
          'orange-dark': '#C4621A',  // Dark orange
          'teal-light': '#E6F5F3',   // Light teal bg
          'teal-dark': '#004D47',    // Very dark teal
        },
      },
      animation: {
        'pulse-ring': 'pulse-ring 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'avatar-breathe': 'breathe 3s ease-in-out infinite',
      },
      keyframes: {
        'pulse-ring': {
          '0%': { transform: 'scale(0.8)', opacity: '1' },
          '100%': { transform: 'scale(1.4)', opacity: '0' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.02)' },
        },
      },
    },
  },
  plugins: [],
}
