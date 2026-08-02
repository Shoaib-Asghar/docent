import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    //for output clean file names for embedding
    rollupOptions: {
      output: {
        entryFileNames: 'docent-widget.js',
        assetFileNames: 'docent-widget.[ext]',
      },
    },
  },
})
