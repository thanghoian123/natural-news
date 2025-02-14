import { fileURLToPath, URL } from "node:url"

import { defineConfig, loadEnv } from "vite"
import vue from "@vitejs/plugin-vue"
import vueDevTools from "vite-plugin-vue-devtools"


// https://vite.dev/config/
export default ({mode}) => {
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};

  const baseURL = process.env.VITE_BASE_URL
  const allowedHost = baseURL ? baseURL : "vip.healthrangerstore.com";

  return defineConfig({
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url))
      },
    },
    server: {
      allowedHosts: [allowedHost],
    },
  });
};
