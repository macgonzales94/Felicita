import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // Configuración del servidor de desarrollo
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    hmr: {
      port: 3001,
    },
    proxy: {
      // Proxy para API durante desarrollo
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy para archivos media
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy para archivos estáticos
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  // Configuración de preview
  preview: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
  },
  
  // Resolución de módulos
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
  
  // Variables de entorno
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
  
  // Configuración de build
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
          // Separar vendors principales
          'react-vendor': ['react', 'react-dom'],
          'router-vendor': ['react-router-dom'],
          'form-vendor': ['react-hook-form'],
          'query-vendor': ['react-query'],
          'chart-vendor': ['recharts'],
          'ui-vendor': ['@headlessui/react', '@heroicons/react'],
          'utils-vendor': ['axios', 'date-fns', 'clsx', 'tailwind-merge'],
        },
      },
    },
    // Configuración de chunks
    chunkSizeWarningLimit: 1000,
  },
  
  // Configuración de CSS
  css: {
    postcss: './postcss.config.js',
    devSourcemap: true,
  },
  
  // Configuración de optimización de dependencias
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'react-hook-form',
      'react-query',
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
    exclude: [
      // Excluir módulos que pueden causar problemas
    ],
  },
  
  // Configuración de entorno
  envPrefix: 'VITE_',
  
  // Configuración de testing
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
  
  // Configuración de worker
  worker: {
    format: 'es',
  },
  
  // Configuración de JSON
  json: {
    namedExports: true,
    stringify: false,
  },
  
  // Configuración de assets estáticos
  assetsInclude: ['**/*.woff', '**/*.woff2', '**/*.eot', '**/*.ttf', '**/*.otf'],
  
  // Base pública para producción
  base: process.env.NODE_ENV === 'production' ? '/felicita/' : '/',
  
  // Configuración para PWA (opcional)
  publicDir: 'public',
})