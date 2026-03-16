import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Kobra",
  description: "AI-powered cyber threat defense platform",
};

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/urls", label: "URLs" },
  { href: "/prompt", label: "Prompt Guard" },
  { href: "/email", label: "Email" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-border/70 bg-base/80 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
              <div>
                <div className="text-xs uppercase tracking-[0.28em] text-accent">Cyber Threat Defense</div>
                <h1 className="text-2xl font-semibold">Kobra</h1>
              </div>
              <nav className="flex flex-wrap gap-3 text-sm text-white/65">
                {links.map((link) => (
                  <Link key={link.href} href={link.href} className="rounded-full border border-border px-4 py-2 hover:border-accent/40 hover:bg-panelAlt">
                    {link.label}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}

