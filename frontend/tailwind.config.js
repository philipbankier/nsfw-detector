/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./src/**/*.{js,jsx,ts,tsx}",
      "./public/index.html"
    ],
    theme: {
      extend: {
        colors: {
          // Custom colors if needed
        },
        animation: {
          'spin-slow': 'spin 2s linear infinite',
        }
      },
    },
    plugins: [],
  }