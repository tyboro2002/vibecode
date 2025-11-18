// vite.config.ts
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    server: {
        host: '0.0.0.0', // allow external network requests
        allowedHosts: ['gayming-naptop'],
        proxy: {
            '/backend': {
                target: 'http://backend:8000',
                changeOrigin: true,
                rewrite: (path) => path.replace(/^\/backend/, ''),
            }
        },
    },
})
