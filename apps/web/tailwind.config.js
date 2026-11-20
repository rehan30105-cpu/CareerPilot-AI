/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
      colors: {
        brand: {
          50: "#f8fafc",
          100: "#f1f5f9",
          200: "#e2e8f0",
          300: "#cbd5e1",
          400: "#94a3b8",
          500: "#64748b",
          600: "#475569",
          700: "#334155",
          800: "#1e293b",
          900: "#0f172a",
        },
        accent: {
          500: "#2563eb",
          600: "#1d4ed8",
        },
      },
      spacing: {
        "xs": "0.5rem",
        "sm": "1rem",
        "md": "1.5rem",
        "lg": "2rem",
        "xl": "3rem",
        "2xl": "4rem",
      },
      borderRadius: {
        sm: "0.375rem",
        DEFAULT: "0.5rem",
        md: "0.75rem",
      },
    },
  },
  plugins: [],
}
