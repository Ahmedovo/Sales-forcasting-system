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
    proxy: (() => {
      const inDocker = process.env.DOCKER === "true";
      const targets = inDocker
        ? {
            auth: "http://auth-service:8001",
            products: "http://products-service:8002",
            sales: "http://sales-service:8003",
            forecast: "http://forecast-service:8004",
          }
        : {
            auth: "http://localhost:8001",
            products: "http://localhost:8002",
            sales: "http://localhost:8003",
            forecast: "http://localhost:8004",
          };
      return {
        "/api/auth": { target: targets.auth, changeOrigin: true },
        "/api/products": { target: targets.products, changeOrigin: true },
        "/api/sales": { target: targets.sales, changeOrigin: true },
        "/api": { target: targets.forecast, changeOrigin: true },
      };
    })(),
  },
});


