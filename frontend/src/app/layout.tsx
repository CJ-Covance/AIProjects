import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Navbar from "@/components/Navbar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Atlas — Unified Knowledge Platform",
  description:
    "Ask once. Receive one clear, consolidated answer — summarized from every relevant page across your organization.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main className="min-h-[calc(100vh-73px)]">{children}</main>
      </body>
    </html>
  );
}
