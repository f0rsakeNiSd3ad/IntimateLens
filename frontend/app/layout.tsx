import "../globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "IntimacyLens - Relationship Health Analysis",
  description: "Privacy-focused relationship health analysis powered by AI",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
