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
      const target = inDocker ? "http://backend:8000" : "http://localhost:8000";
      return {
        "/api": { target, changeOrigin: true },
      };
    })(),
  },
});


