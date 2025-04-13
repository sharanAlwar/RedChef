/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        redbull: {
          DEFAULT: '#FF0000',
          dark: '#CC0000',
          light: '#FF3333',
        },
      },
    },
  },
  plugins: [],
} 