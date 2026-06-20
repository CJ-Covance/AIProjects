"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Ask" },
  { href: "/browse", label: "Browse" },
  { href: "/manage", label: "Manage" },
  { href: "/logs", label: "Logs" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-atlas-navy text-sm font-bold text-white">
            A
          </div>
          <div>
            <div className="text-lg font-semibold text-atlas-navy">Atlas</div>
            <div className="text-xs text-slate-500">Unified Knowledge Platform</div>
          </div>
        </Link>
        <nav className="flex items-center gap-1">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                pathname === link.href
                  ? "bg-atlas-light text-atlas-navy"
                  : "text-slate-600 hover:bg-slate-50 hover:text-atlas-navy"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
