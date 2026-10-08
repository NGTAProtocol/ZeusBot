import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// outDir e site vengono passati da scripts/generate.mjs
export default defineConfig({
  srcDir: process.env.ATELIER_SRC || './src',
  outDir: process.env.ATELIER_OUT || './dist',
  site: process.env.ATELIER_SITE || 'https://example.com',
  base: process.env.ATELIER_BASE || '/',
  trailingSlash: 'ignore',
  build: { inlineStylesheets: 'always', assets: '_assets' },
  compressHTML: true,
  devToolbar: { enabled: false },
  vite: {
    plugins: [tailwindcss()],
    build: { assetsInlineLimit: 2048, chunkSizeWarningLimit: 900 }
  }
});
