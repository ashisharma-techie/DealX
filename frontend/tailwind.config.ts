import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: "#F3EDE4",
        surface: "#FBF8F3",
        lavender: "#A9C9E3",
        sage: "#A9DBC5",
        blush: "#F0B8C9",
        ink: "#3B362F",
        muted: "#8A8072",
        "lavender-deep": "#8FB4D6",
        "sage-deep": "#82C2A4",
        "blush-deep": "#E29BB4",
      },
      fontFamily: {
        display: ["var(--font-sora)", "sans-serif"],
        body: ["var(--font-inter)", "sans-serif"],
      },
      borderRadius: {
        search: "28px",
        tile: "20px",
        card: "16px",
        modal: "30px",
      },
      boxShadow: {
        lifted: "0 12px 32px -12px rgba(59, 54, 47, 0.18)",
      },
    },
  },
  plugins: [],
};
export default config;