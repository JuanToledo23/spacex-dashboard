import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import viteCompression from 'vite-plugin-compression'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    viteCompression({ algorithm: 'gzip', threshold: 1024 }),
    viteCompression({ algorithm: 'brotliCompress', threshold: 1024 }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-d3': ['d3-selection', 'd3-scale', 'd3-axis', 'd3-shape', 'd3-array', 'd3-geo', 'd3-transition', 'd3-interpolate', 'd3-format', 'd3-time-format', 'd3-path', 'd3-color', 'd3-ease', 'd3-timer'],
          'vendor-axios': ['axios'],
        },
      },
    },
    chunkSizeWarningLimit: 250,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
  },
})
