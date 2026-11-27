import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const rootDir = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(rootDir, '..')

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    fs: {
      // Allow importing shared markdown from ../docs (e.g. glossary_*.md)
      allow: [rootDir, repoRoot],
    },
    proxy: {
      '/analyze': 'http://localhost:8000',
      '/search': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/pubmed': 'http://localhost:8000',
      '/methods': 'http://localhost:8000',
      '/documents': 'http://localhost:8000',
    },
  },
})
