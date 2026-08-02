import Link from "next/link";

type QuickStartAction = {
  href: string;
  title: string;
  description: string;
  icon: React.ReactNode;
};

const actions: QuickStartAction[] = [
  {
    href: "/feedback",
    title: "Import Feedback",
    description: "Paste customer signal from support tickets, reviews, or calls",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-5 h-5">
        <path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5c-1.35 0-2.62-.32-3.75-.9L3 21l1.9-5.75A8.5 8.5 0 1 1 21 11.5Z" />
      </svg>
    ),
  },
  {
    href: "/documents",
    title: "Add a Document",
    description: "Upload a PRD, spec, or research doc for the copilot to reference",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-5 h-5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
        <path d="M14 2v6h6" />
      </svg>
    ),
  },
  {
    href: "/analyses",
    title: "Run an Analysis",
    description: "Cluster and prioritize the feedback you've already imported",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-5 h-5">
        <path d="M9 3v18M9 3 4 6v14l5-3M9 3l6 3M15 6v14l5-3V3l-5 3Z" />
      </svg>
    ),
  },
  {
    href: "/opportunities",
    title: "Log an Opportunity",
    description: "Capture a problem or bet worth tracking against the roadmap",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" className="w-5 h-5">
        <circle cx="12" cy="12" r="9" />
        <circle cx="12" cy="12" r="5" />
        <circle cx="12" cy="12" r="1" />
      </svg>
    ),
  },
];

export default function QuickStart() {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/8 backdrop-blur-md p-6 shadow-xl shadow-black/20">
      <div className="mb-5">
        <h2 className="text-xs font-medium tracking-widest text-zinc-200 uppercase">Quick Start</h2>
        <p className="text-zinc-300 text-sm mt-1">Where do you want to start today?</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {actions.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="group rounded-xl border border-white/10 bg-black/20 hover:bg-emerald-500/10 hover:border-emerald-400/30 p-4 transition-colors"
          >
            <div className="w-9 h-9 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center mb-3 group-hover:bg-emerald-500/25 transition-colors">
              {action.icon}
            </div>
            <h3 className="text-sm font-medium text-white mb-1">{action.title}</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">{action.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}