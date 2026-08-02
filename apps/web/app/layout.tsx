import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "./components/Sidebar";

export const metadata: Metadata = {
  title: "AI Copilot for PMs",
  description: "AI-powered product intelligence for product managers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-zinc-950 text-zinc-100 antialiased">
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute inset-0 bg-cover bg-center blur-[2px] scale-105 opacity-75"
            style={{ backgroundImage: "url('/bg-desk.jpg')" }}
          />
          <div className="absolute inset-0 bg-zinc-950/35" />
        </div>

        <div className="relative flex min-h-screen">
          <Sidebar />
          <main className="flex-1 ml-64 p-5">{children}</main>
        </div>
      </body>
    </html>
  );
}