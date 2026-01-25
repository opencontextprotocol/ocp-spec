/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './**/*.md',
    './**/*.html',
    '../**/*.j2',
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
