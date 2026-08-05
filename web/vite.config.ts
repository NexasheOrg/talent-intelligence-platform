/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In `npm run dev`, calls to /api are proxied to the local API on port 8000.
// In Docker, nginx proxies /api instead (see nginx.conf). The app itself always uses
// relative /api paths so the same build works in both places.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Order matters: the more specific rule has to come first, or /api would swallow it.
      '/api/assistant': 'http://localhost:8100',
      '/api': 'http://localhost:8000',
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    css: false,
  },
})
