"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  MessageSquare,
  FlaskConical,
  FileText,
  Target,
  Activity,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Command", icon: LayoutGrid },
  { href: "/feedback", label: "Feedback", icon: MessageSquare },
  { href: "/analyses", label: "Analyses", icon: FlaskConical },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/opportunities", label: "Opportunities", icon: Target },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r border-emerald-500/10 bg-emerald-950/40 backdrop-blur-2xl flex flex-col">
      <div className="flex items-center gap-2 px-6 py-6">
        <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
          <Activity className="w-4 h-4 text-emerald-400" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight text-white">
            AI PM Command
          </div>
          <div className="text-[10px] tracking-widest text-zinc-400 uppercase">
            Product Intelligence
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 space-y-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                active
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20"
                  : "text-zinc-300 hover:text-white hover:bg-white/5 border border-transparent"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4">
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 backdrop-blur-md px-4 py-3 space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-300">System</span>
            <span className="flex items-center gap-1.5 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Online
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-zinc-300">Sync</span>
            <span className="text-emerald-400">Active</span>
          </div>
        </div>
      </div>
    </aside>
  );
}