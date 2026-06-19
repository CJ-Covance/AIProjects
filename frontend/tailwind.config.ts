import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        "atlas-navy": "#0c2340",
        "atlas-blue": "#1e4d8c",
        "atlas-teal": "#0d9488",
        "atlas-light": "#e8f4f8",
        "atlas-accent": "#38bdf8",
      },
    },
  },
  plugins: [],
};
export default config;
