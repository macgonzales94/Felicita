export default {
  plugins: {
    // Tailwind CSS
    tailwindcss: {},
    
    // Autoprefixer para compatibilidad con navegadores
    autoprefixer: {},
    
    // Plugin para optimización en producción
    ...(process.env.NODE_ENV === 'production' && {
      cssnano: {
        preset: [
          'default',
          {
            discardComments: {
              removeAll: true,
            },
            normalizeWhitespace: true,
            colormin: true,
            minifySelectors: true,
            minifyParams: true,
            minifyFontValues: true,
          },
        ],
      },
    }),
  },
}