import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  envDir: '..',
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('/node_modules/mapbox-gl/')) return 'mapbox'
          if (id.includes('/node_modules/vue') || id.includes('/node_modules/@vue/')) return 'vue'
          if (id.includes('/node_modules/')) return 'vendor'
        }
      }
    }
  },
  server: {
    port: 5173,
    open: true
  }
})
