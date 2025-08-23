import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    svgr({
      svgrOptions: {
        exportType: "default",
      },
    }),
  ],
  server: {
    host: "0.0.0.0",
  },
  build: {
    sourcemap: mode === "development",
  },
  base: "./",
}));
