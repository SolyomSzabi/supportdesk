import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// In development the Vite server forwards /api to Django, so the browser sees
// one origin and we need no CORS setup.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
});
