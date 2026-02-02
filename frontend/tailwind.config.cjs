/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#065f46',
          light: '#047857',
          dark: '#134e4a',
        },
        secondary: '#10b981',
        success: '#4ade80',
        warning: '#fbbf24',
        error: '#ef4444',
        info: '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
