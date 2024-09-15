import { viteStaticCopy } from 'vite-plugin-static-copy'

export default {
  server: {
    port: 3000,
    strictPort: true,
  },

  resolve: {
    alias: {
      '@': '/src',
    }
  },

  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'node_modules/govuk-frontend/dist/govuk/assets/*',
          dest: '../../src/govuk_flask_admin/static/govuk-frontend/assets/.'
        },
        {
          src: 'dist/assets/*',
          dest: '../../src/govuk_flask_admin/static/govuk-frontend/.'
        }
      ]
    })
  ]
};
