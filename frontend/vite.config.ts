import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Permet l'accès depuis d'autres machines
    // Autoriser tous les hôtes AWS EC2 (compute.amazonaws.com)
    allowedHosts: [
      '.compute.amazonaws.com', // Autorise tous les sous-domaines *.compute.amazonaws.com
      'ec2-56-228-16-227.eu-north-1.compute.amazonaws.com', // Hôte spécifique
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path, // Garde le chemin /api tel quel
        // Logs pour le débogage
        configure: (proxy, _options) => {
          proxy.on('error', (err, req, res) => {
            console.error('❌ Proxy error:', err.message);
            console.error('❌ Backend non accessible sur http://localhost:8000');
            console.error('❌ Vérifiez que le backend est démarré avec: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000');
          });
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('📤 Proxy Request:', req.method, req.url, '-> http://localhost:8000' + req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('📥 Proxy Response:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
})

