import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ManimGen - AI-Powered Animation Generator",
  description: "Transform text prompts into stunning mathematical animations using AI and Manim",
  keywords: ["manim", "animation", "ai", "math", "video generator", "3blue1brown"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' }}>
        {children}
      </body>
    </html>
  );
}

