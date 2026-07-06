import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BakeLab AI",
  description: "An AI baking assistant for home bakers.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

