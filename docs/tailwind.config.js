/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './content/**/*.md',
    './layouts/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        mono: ["IBM Plex Mono", "monospace"],
      },
    },
  },
  plugins: [],
}
