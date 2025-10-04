import path from "node:path"
import { viteStaticCopy } from "vite-plugin-static-copy"

import { defineConfig } from "vite"

export default defineConfig({
  build: {
    outDir: path.join(__dirname, "src", "assets", "dist"),
    manifest: "manifest.json",
    rollupOptions: {
      input: ["src/assets/main.scss", "src/assets/main.js"],
      external: [
        /assets\/fonts\/.*\.(woff|woff2)$/,
        /assets\/images\/.*\.svg$/,
      ],
    },
    emptyOutDir: true,
  },
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: [
          "mixed-decls",
          "global-builtin",
          "slash-div",
          "import",
        ],
      },
    },
  },
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: "node_modules/govuk-frontend/dist/govuk/assets/*",
          dest: "./assets",
        }
      ],
    }),
  ],
  clearScreen: false,
  appType: "custom"
})
