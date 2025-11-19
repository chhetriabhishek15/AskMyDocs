import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        // Use environment variable or default to localhost for local dev
        // In Docker, this should be 'http://backend:8000'
        // For local development, use 'http://localhost:8000'
        target: process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
        changeOrigin: true,
        // No rewrite needed - client.ts already uses '/api/v1' as baseURL
      },
    },
  },
})


