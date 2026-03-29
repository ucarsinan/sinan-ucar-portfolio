// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://sinanucar.com',
  integrations: [
    sitemap({
      filter: (page) =>
        !page.includes('/datenschutz') &&
        !page.includes('/impressum') &&
        !page.includes('/privacy') &&
        !page.includes('/imprint'),
      i18n: {
        defaultLocale: 'de',
        locales: { de: 'de-DE', en: 'en-US' }
      }
    })
  ],
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        '/health': 'http://localhost:8000',
        '/api': 'http://localhost:8000',
      }
    }
  },
  i18n: {
    defaultLocale: "de",
    locales: ["de", "en"],
    routing: {
      prefixDefaultLocale: false 
    }
  }
});
