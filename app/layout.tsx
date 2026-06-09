import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Insuretra",
  description: "Pipeline-first market intelligence for Texas insurance agencies."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
