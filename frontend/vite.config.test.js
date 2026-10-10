import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(rootDir, '..')

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5174,
    fs: {
      allow: [rootDir, repoRoot],
    },
    proxy: {
      '/analyze': 'http://localhost:8001',
      '/search': 'http://localhost:8001',
      '/admin': 'http://localhost:8001',
      '/health': 'http://localhost:8001',
      '/pubmed': 'http://localhost:8001',
      '/methods': 'http://localhost:8001',
      '/documents': 'http://localhost:8001',
    },
  },
})
