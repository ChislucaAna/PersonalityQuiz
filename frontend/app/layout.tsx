import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Portrait Quiz",
  description: "Answer a short quiz and get an AI portrait that captures your vibe.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <main className="app">{children}</main>
      </body>
    </html>
  );
}
