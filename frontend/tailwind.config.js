/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0EA5E9',
        'primary-hover': '#0284C7',
        secondary: '#38BDF8',
        cta: '#FBBF24',
        'cta-hover': '#F59E0B',
        background: '#F0F9FF',
        card: '#FFFFFF',
        text: '#0C4A6E',
        'text-muted': '#64748B',
        border: '#BAE6FD',
        'hover-bg': '#E0F2FE',
      },
      fontFamily: {
        heading: ['Poppins', 'sans-serif'],
        body: ['Open Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
