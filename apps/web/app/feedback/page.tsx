"use client";

import { useState } from "react";

type FeedbackItem = {
  id: string;
  text: string;
  sentiment: "positive" | "negative" | "neutral";
  theme: string | null;
};

export default function FeedbackPage() {
  const [source, setSource] = useState("");
  const [data, setData] = useState("");
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleImport() {
    setError(null);
    const lines = data.split("\n").map((l) => l.trim()).filter((l) => l.length > 0);

    if (lines.length === 0) {
      setError("Paste at least one line of feedback before importing.");
      return;
    }

    const documents = lines.map((text, i) => ({
      id: `${source || "feedback"}_${i + 1}`,
      text,
    }));

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documents }),
      });

      if (!res.ok) throw new Error(`Server responded with ${res.status}`);

      const result = await res.json();

      const themesBySource = new Map<string, { theme: string; sentiment: string }>();
      for (const cluster of result.ranked_features) {
        for (const evidence of cluster.evidence) {
          themesBySource.set(evidence.source_id, {
            theme: cluster.cluster_theme,
            sentiment: evidence.sentiment,
          });
        }
      }

      const displayed: FeedbackItem[] = documents.map((doc) => {
        const match = themesBySource.get(doc.id);
        return {
          id: doc.id,
          text: doc.text,
          sentiment: (match?.sentiment as FeedbackItem["sentiment"]) || "neutral",
          theme: match?.theme || null,
        };
      });

      setItems((prev) => [...displayed, ...prev]);
      setData("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  const sentimentColor: Record<FeedbackItem["sentiment"], string> = {
    positive: "text-emerald-400 border-emerald-400/30 bg-emerald-400/10",
    negative: "text-rose-400 border-rose-400/30 bg-rose-400/10",
    neutral: "text-zinc-400 border-zinc-400/30 bg-zinc-400/10",
  };

  return (
    <div className="w-full space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-white">Feedback</h1>
        <p className="text-zinc-300 text-sm mt-1">Capture and organize customer signal</p>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/8 backdrop-blur-md p-6 space-y-4 shadow-xl shadow-black/20">
        <h2 className="text-xs font-medium tracking-widest text-zinc-200 uppercase">Bulk Import</h2>

        <div>
          <label className="text-sm text-zinc-200 block mb-1.5">Source</label>
          <input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="e.g., zendesk-export"
            className="w-full rounded-lg bg-black/30 border border-white/10 px-3 py-2.5 text-sm placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50"
          />
        </div>

        <div>
          <label className="text-sm text-zinc-200 block mb-1.5">Data</label>
          <textarea
            value={data}
            onChange={(e) => setData(e.target.value)}
            placeholder="Paste your feedback data here, one item per line..."
            rows={6}
            className="w-full rounded-lg bg-black/30 border border-white/10 px-3 py-2.5 text-sm placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 resize-none"
          />
        </div>

        {error && <p className="text-rose-400 text-sm">{error}</p>}

        <button
          onClick={handleImport}
          disabled={loading}
          className="rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 text-sm font-medium text-white transition-colors"
        >
          {loading ? "Analyzing..." : "Import & Analyze"}
        </button>
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/8 backdrop-blur-md p-6 shadow-xl shadow-black/20">
        <h2 className="text-xs font-medium tracking-widest text-zinc-200 uppercase mb-4">
          Feedback ({items.length})
        </h2>

        {items.length === 0 ? (
          <p className="text-zinc-400 text-sm">No feedback imported yet.</p>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.id} className="rounded-xl border border-white/10 bg-black/20 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${sentimentColor[item.sentiment]}`}>
                    {item.sentiment}
                  </span>
                  {item.theme && (
                    <span className="text-xs px-2 py-0.5 rounded-full border border-white/10 text-zinc-400">
                      {item.theme}
                    </span>
                  )}
                </div>
                <p className="text-sm text-zinc-300">{item.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}