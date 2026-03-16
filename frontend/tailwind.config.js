/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        base: "#08111f",
        panel: "#0d1728",
        panelAlt: "#13213a",
        border: "#1f3155",
        safe: "#16a34a",
        suspicious: "#f59e0b",
        malicious: "#f97316",
        critical: "#dc2626",
        accent: "#29c7ac"
      },
      boxShadow: {
        glow: "0 20px 50px rgba(41, 199, 172, 0.12)"
      }
    }
  },
  plugins: []
};

