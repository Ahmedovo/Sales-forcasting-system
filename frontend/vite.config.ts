import { defineConfig } from "vite";
import { fileURLToPath, URL } from "node:url";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  preview: {
    port: 8080,
    strictPort: true,
  },
  server: {
    port: 8080,
    strictPort: true,
    host: true,
    origin: "http://0.0.0.0:8080",
    proxy: {
      // Route frontend /api/auth/* to auth-service
      "/api/auth": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      // Route /api/products/* to products-service
      "/api/products": {
        target: "http://localhost:8002",
        changeOrigin: true,
      },
      // Route /api/sales/* to sales-service
      "/api/sales": {
        target: "http://localhost:8003",
        changeOrigin: true,
      },
      // Route /api (forecast endpoints live directly under /api)
      "/api": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
    },
  },
});


