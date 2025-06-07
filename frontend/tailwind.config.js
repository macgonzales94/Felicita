/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  
  theme: {
    extend: {
      // Configuración de colores personalizados para FELICITA
      colors: {
        // Colores principales de la marca
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',  // Color principal
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        
        // Colores secundarios
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
        },
        
        // Colores de estado para facturación
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',  // Verde para estados exitosos
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',  // Amarillo para advertencias
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',  // Rojo para errores
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        
        // Colores específicos para módulos
        facturacion: {
          light: '#dbeafe',
          DEFAULT: '#3b82f6',
          dark: '#1d4ed8',
        },
        
        inventario: {
          light: '#d1fae5',
          DEFAULT: '#10b981',
          dark: '#047857',
        },
        
        contabilidad: {
          light: '#e0e7ff',
          DEFAULT: '#6366f1',
          dark: '#4338ca',
        },
        
        pos: {
          light: '#fef3c7',
          DEFAULT: '#f59e0b',
          dark: '#d97706',
        },
        
        // Colores de estado SUNAT
        sunat: {
          enviado: '#3b82f6',
          aceptado: '#22c55e',
          rechazado: '#ef4444',
          pendiente: '#f59e0b',
        },
      },
      
      // Configuración de tipografía
      fontFamily: {
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'Courier New',
          'monospace',
        ],
      },
      
      // Configuración de espaciado
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      
      // Configuración de breakpoints
      screens: {
        'xs': '475px',
        '3xl': '1920px',
      },
      
      // Configuración de animaciones
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'fade-out': {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'slide-out': {
          '0%': { transform: 'translateX(0)' },
          '100%': { transform: 'translateX(-100%)' },
        },
        'bounce-gentle': {
          '0%, 100%': { transform: 'translateY(-5%)' },
          '50%': { transform: 'translateY(0)' },
        },
        'pulse-slow': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'fade-out': 'fade-out 0.3s ease-out',
        'slide-in': 'slide-in 0.3s ease-out',
        'slide-out': 'slide-out 0.3s ease-out',
        'bounce-gentle': 'bounce-gentle 2s infinite',
        'pulse-slow': 'pulse-slow 3s infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      
      // Configuración de sombras
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.07), 0 10px 20px -2px rgba(0, 0, 0, 0.04)',
        'medium': '0 4px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'strong': '0 10px 40px -10px rgba(0, 0, 0, 0.15), 0 4px 25px -5px rgba(0, 0, 0, 0.1)',
        'inner-soft': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.3)',
      },
      
      // Configuración de bordes redondeados
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '2rem',
      },
      
      // Configuración de transiciones
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
      },
      
      // Configuración de z-index
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
      
      // Configuración de backdrop blur
      backdropBlur: {
        xs: '2px',
      },
      
      // Configuración de gradientes
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'shimmer-gradient': 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
      },
    },
  },
  
  plugins: [
    // Plugin para formularios
    require('@tailwindcss/forms')({
      strategy: 'class',
    }),
    
    // Plugin para tipografía
    require('@tailwindcss/typography'),
    
    // Plugin para aspect ratio
    require('@tailwindcss/aspect-ratio'),
    
    // Plugin personalizado para utilidades de FELICITA
    function({ addUtilities, addComponents, theme }) {
      // Utilidades personalizadas
      addUtilities({
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
        
        '.scrollbar-thin': {
          'scrollbar-width': 'thin',
          '&::-webkit-scrollbar': {
            width: '6px',
            height: '6px',
          },
          '&::-webkit-scrollbar-track': {
            background: theme('colors.gray.100'),
          },
          '&::-webkit-scrollbar-thumb': {
            background: theme('colors.gray.300'),
            'border-radius': '3px',
          },
          '&::-webkit-scrollbar-thumb:hover': {
            background: theme('colors.gray.400'),
          },
        },
        
        '.text-balance': {
          'text-wrap': 'balance',
        },
      })
      
      // Componentes personalizados
      addComponents({
        '.btn-primary': {
          '@apply bg-primary-500 hover:bg-primary-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2': {},
        },
        
        '.btn-secondary': {
          '@apply bg-secondary-500 hover:bg-secondary-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-secondary-500 focus:ring-offset-2': {},
        },
        
        '.btn-outline': {
          '@apply border border-primary-500 text-primary-500 hover:bg-primary-500 hover:text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2': {},
        },
        
        '.card': {
          '@apply bg-white rounded-xl shadow-soft border border-gray-200 p-6': {},
        },
        
        '.card-hover': {
          '@apply card hover:shadow-medium transition-shadow duration-200': {},
        },
        
        '.input-field': {
          '@apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-colors duration-200': {},
        },
        
        '.label': {
          '@apply block text-sm font-medium text-gray-700 mb-1': {},
        },
        
        '.badge': {
          '@apply inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium': {},
        },
        
        '.badge-success': {
          '@apply badge bg-success-100 text-success-800': {},
        },
        
        '.badge-warning': {
          '@apply badge bg-warning-100 text-warning-800': {},
        },
        
        '.badge-error': {
          '@apply badge bg-error-100 text-error-800': {},
        },
      })
    },
  ],
  
  // Configuración de dark mode
  darkMode: 'class',
  
  // Configuración de variantes
  future: {
    hoverOnlyWhenSupported: true,
  },
  
  // Configuración de preflight
  corePlugins: {
    preflight: true,
  },
}