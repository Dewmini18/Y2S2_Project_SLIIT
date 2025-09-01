import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

import tailwindcss from '@tailwindcss/vite'


// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#ff5722',
        secondary: '#ffc107',
      },
    },
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '2rem',
      },
    },
  },
})
