import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // FORCE VITE TO LOAD V4 ONLY
      "lightweight-charts": path.resolve(
        __dirname,
        "node_modules/lightweight-charts/dist/lightweight-charts.esm.js"
      ),
    },
  },
});
