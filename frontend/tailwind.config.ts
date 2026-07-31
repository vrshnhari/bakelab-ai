import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        dough: "#fff8ed",
        cocoa: "#3d2821",
        berry: "#9f244d",
        rosewater: "#fff1f4",
        pistachio: "#5d7c52",
        steel: "#34404a",
      },
      boxShadow: {
        soft: "0 18px 60px rgba(61, 40, 33, 0.14)",
      },
    },
  },
  plugins: [],
};

export default config;
