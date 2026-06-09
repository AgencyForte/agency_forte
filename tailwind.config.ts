import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17211f",
        field: "#f3f6f4",
        moss: "#425f4b",
        signal: "#c5563a"
      }
    }
  },
  plugins: []
};

export default config;
