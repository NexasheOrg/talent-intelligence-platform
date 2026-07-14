import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In `npm run dev`, calls to /api are proxied to the local API container.
// In Docker, nginx proxies /api instead (see nginx.conf).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { '/api': 'http://localhost:8000' },
  },
})
