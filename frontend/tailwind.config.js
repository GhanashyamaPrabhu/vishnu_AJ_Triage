/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // AJ Institute Brand Colors
        primary: {
          50: '#f0f4ff',
          100: '#e0e9ff',
          200: '#c7d6ff',
          300: '#a5b8ff',
          400: '#8191ff',
          500: '#5d6aff',
          600: '#4c51f7',
          700: '#3d3ee3',
          800: '#3133b8',
          900: '#1a2f5e', // Deep navy blue - main brand color
          950: '#0f1729',
        },
        medical: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#2e7d32', // Medical green - accent color
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        // Triage Category Colors
        triage: {
          red: '#dc2626',      // RED - Immediate
          orange: '#ea580c',   // ORANGE - Very urgent
          yellow: '#ca8a04',   // YELLOW - Urgent
          green: '#16a34a',    // GREEN - Routine
        },
        // Status Colors
        success: '#059669',
        warning: '#d97706',
        error: '#dc2626',
        info: '#0284c7',
        // GCS Interpretation Colors
        gcs: {
          normal: '#16a34a',
          minor: '#0284c7',
          moderate: '#d97706',
          severe: '#dc2626',
          critical: '#991b1b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],
        'base': ['1rem', { lineHeight: '1.5rem' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'strong': '0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 4px 25px -5px rgba(0, 0, 0, 0.1)',
        'triage-red': '0 4px 20px -2px rgba(220, 38, 38, 0.25)',
        'triage-orange': '0 4px 20px -2px rgba(234, 88, 12, 0.25)',
        'triage-yellow': '0 4px 20px -2px rgba(202, 138, 4, 0.25)',
        'triage-green': '0 4px 20px -2px rgba(22, 163, 74, 0.25)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounceGentle 2s infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(93, 106, 255, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(93, 106, 255, 0.8)' },
        },
      },
      screens: {
        'xs': '475px',
        'tablet': '768px',
        'laptop': '1024px',
        'desktop': '1280px',
      },
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      backdropBlur: {
        'xs': '2px',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    require('@tailwindcss/typography'),
    // Custom plugin for medical form styles
    function({ addComponents, theme }) {
      addComponents({
        '.medical-input': {
          '@apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm': {},
        },
        '.medical-select': {
          '@apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm': {},
        },
        '.medical-textarea': {
          '@apply block w-full rounded-lg border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm resize-none': {},
        },
        '.btn-primary': {
          '@apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed': {},
        },
        '.btn-secondary': {
          '@apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-lg shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500': {},
        },
        '.btn-medical': {
          '@apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-medical-600 hover:bg-medical-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-medical-500': {},
        },
        '.triage-badge': {
          '@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': {},
        },
        '.triage-badge-red': {
          '@apply triage-badge bg-red-100 text-red-800 border border-red-200': {},
        },
        '.triage-badge-orange': {
          '@apply triage-badge bg-orange-100 text-orange-800 border border-orange-200': {},
        },
        '.triage-badge-yellow': {
          '@apply triage-badge bg-yellow-100 text-yellow-800 border border-yellow-200': {},
        },
        '.triage-badge-green': {
          '@apply triage-badge bg-green-100 text-green-800 border border-green-200': {},
        },
        '.gcs-badge': {
          '@apply inline-flex items-center px-3 py-1 rounded-full text-sm font-medium': {},
        },
        '.gcs-badge-normal': {
          '@apply gcs-badge bg-green-100 text-green-800': {},
        },
        '.gcs-badge-minor': {
          '@apply gcs-badge bg-blue-100 text-blue-800': {},
        },
        '.gcs-badge-moderate': {
          '@apply gcs-badge bg-yellow-100 text-yellow-800': {},
        },
        '.gcs-badge-severe': {
          '@apply gcs-badge bg-red-100 text-red-800': {},
        },
        '.gcs-badge-critical': {
          '@apply gcs-badge bg-red-200 text-red-900 animate-pulse': {},
        },
        '.card': {
          '@apply bg-white rounded-xl shadow-soft border border-gray-200': {},
        },
        '.card-header': {
          '@apply px-6 py-4 border-b border-gray-200': {},
        },
        '.card-body': {
          '@apply px-6 py-4': {},
        },
        '.card-footer': {
          '@apply px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl': {},
        },
        '.vital-input': {
          '@apply medical-input text-center font-mono text-lg': {},
        },
        '.vital-label': {
          '@apply block text-sm font-medium text-gray-700 mb-1': {},
        },
        '.vital-unit': {
          '@apply text-sm text-gray-500 ml-2': {},
        },
        '.vital-range': {
          '@apply text-xs text-gray-400 mt-1': {},
        },
        '.alert': {
          '@apply rounded-lg p-4 border': {},
        },
        '.alert-info': {
          '@apply alert bg-blue-50 border-blue-200 text-blue-800': {},
        },
        '.alert-success': {
          '@apply alert bg-green-50 border-green-200 text-green-800': {},
        },
        '.alert-warning': {
          '@apply alert bg-yellow-50 border-yellow-200 text-yellow-800': {},
        },
        '.alert-error': {
          '@apply alert bg-red-50 border-red-200 text-red-800': {},
        },
      })
    }
  ],
}