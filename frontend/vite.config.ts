import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/run-task': 'http://localhost:5000',
      '/send-edited-email': 'http://localhost:5000',
      '/save-learning': 'http://localhost:5000',
    }
  }
})
