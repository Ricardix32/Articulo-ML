/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: '#f2f5f8',
          100: '#e1e7f0',
          200: '#c5d2e3',
          300: '#9cb5d1',
          400: '#6d91bb',
          500: '#4a70a0',
          600: '#385682',
          700: '#2e456a',
          800: '#1f304c',
          900: '#152136',
          950: '#0e1525',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
