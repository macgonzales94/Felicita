import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    hmr: {
      port: 3001,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/componentes': path.resolve(__dirname, './src/componentes'),
      '@/paginas': path.resolve(__dirname, './src/paginas'),
      '@/servicios': path.resolve(__dirname, './src/servicios'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/contextos': path.resolve(__dirname, './src/contextos'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/estilos': path.resolve(__dirname, './src/estilos'),
    },
  },

  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router-vendor': ['react-router-dom'],
          'form-vendor': ['react-hook-form'],
          'query-vendor': ['@tanstack/react-query'],
          'chart-vendor': ['recharts'],
          'ui-vendor': ['@headlessui/react', '@heroicons/react'],
          'utils-vendor': ['axios', 'date-fns', 'clsx', 'tailwind-merge'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },

  css: {
    postcss: './postcss.config.js',
    devSourcemap: true,
  },

  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'react-hook-form',
      '@tanstack/react-query',
      'axios',
      'date-fns',
      'clsx',
      'class-variance-authority',
      'tailwind-merge',
      'lucide-react',
      'recharts',
      '@headlessui/react',
      '@heroicons/react',
      'react-hot-toast',
    ],
    exclude: [],
  },

  envPrefix: 'VITE_',

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },

  worker: {
    format: 'es',
  },

  json: {
    namedExports: true,
    stringify: false,
  },

  assetsInclude: ['**/*.woff', '**/*.woff2', '**/*.eot', '**/*.ttf', '**/*.otf'],

  base: process.env.NODE_ENV === 'production' ? '/felicita/' : '/',

  publicDir: 'public',
})
