# PRD v2 — AI Copilot for Product Managers

**Owner:** Shreyasi
**Status:** Draft v2.0 — reflects current build
**Last updated:** September 7, 2026
**Supersedes:** PRD v0.1 (July 20, 2026)

---

## 0. Why a v2

The original PRD described the intended product. This version describes the product as it is actually being built, and adds the sections a PRD needs once an LLM pipeline is a core dependency rather than a nice-to-have: how we know the model is good enough, what happens when it's wrong, and what it costs to run. Standard PM PRDs assume deterministic features. This one doesn't have that luxury — everything downstream of extraction depends on a model's output being *usually* right, and the product has to be designed around that assumption, not in spite of it.

---

## 1. Problem Statement

Product managers make "what to build next" decisions using scattered, unstructured inputs — customer interview transcripts, support/feedback threads, and product analytics. Synthesizing these into a prioritized, defensible feature list is manual, slow, and biased toward whoever shouts loudest in the room.

## 2. Goal

Ingest customer feedback (starting with text; interviews and analytics in v2+), extract and cluster recurring themes, score them against a transparent rubric, and surface a ranked, evidence-backed feature list — with every ranking traceable back to source text.

## 3. Target User

- Primary: PMs at seed–Series B startups without a dedicated insights/ops function.
- Secondary: Founders acting as de facto PMs.
- **Portfolio context:** this is also a demo-able artifact for AI PM interviews. That constraint shapes some decisions below (e.g., favoring explainable scoring over a black-box ranking model) as much as the end-user need does.

## 4. Non-Goals (current scope)

- Not a Jira/roadmapping replacement.
- Not a live analytics pipeline — batch upload, not streaming.
- Not multi-user/workspace — single-user for now.
- Not a fine-tuned or custom-trained model — this is a pipeline built entirely on off-the-shelf LLM and embedding APIs, orchestrated with deterministic logic. No training data collection, no model fine-tuning is in scope.

---

## 5. What's Actually Built (as of this version)

| Layer | Choice | Status |
|---|---|---|
| Theme extraction | Groq (`openai/gpt-oss-20b`) | ✅ Live |
| Embeddings | Gemini (`gemini-embedding-001`) | ✅ Live |
| Clustering | Greedy, cosine similarity, 0.80 threshold | ✅ Live |
| Scoring | RICE-style: frequency × source diversity × sentiment weight | ✅ Live |
| Persistence | Supabase Postgres, 5 tables, Alembic-migrated | ✅ Live |
| API | FastAPI, `/analyze` (write path), `/dashboard/stats` (read path) | ✅ Live |
| Frontend | Next.js, sidebar shell, Feedback page wired to `/analyze` | 🔶 Partial |
| Command Center, Opportunities, Analyses, Documents pages | — | 🔲 Not built |

---

## 6. AI/ML Approach

### 6.1 Why two different model providers

Extraction runs once per *document*; embeddings run once per *theme* (a smaller, later-stage call volume). Extraction was the first thing to hit rate limits under Gemini's free tier, so it moved to Groq, which offers a genuinely free (no-card) developer tier at 30 req/min. Embeddings stayed on Gemini because Groq does not serve embedding models at all — this wasn't a preference, it was a hard constraint discovered mid-build. This kind of provider-splitting is a normal reality in AI product work: you don't get to pick one vendor and be done, you pick per-capability and accept the operational complexity of two API keys, two rate-limit regimes, two failure modes.

### 6.2 Why greedy clustering instead of k-means or a vector DB

K-means requires knowing the number of clusters in advance, which we don't. At MVP scale (dozens of themes per run, not millions), a greedy single-pass approach is fast enough, and — this matters for an AI PM specifically — it's *auditable*. Every clustering decision reduces to one comparable number: cosine similarity against the 0.80 threshold. That threshold is a real product lever, not an implementation detail — raising it produces more, smaller, higher-precision clusters (safer, less impressive-looking); lowering it produces broader clusters (better recall, higher risk of merging distinct requests). No offline tuning of this threshold has been done yet — it's a placeholder based on general embedding-similarity conventions, not validated against labeled data. That's a real gap, tracked in §9.

### 6.3 Why the scoring rubric is fixed, not learned

`sentiment_weight` uses fixed values (negative=1.0, neutral=0.6, positive=0.4) rather than a learned or user-configurable weighting. This is a deliberate MVP choice: a rubric a PM can recite and defend beats a marginally more accurate one they can't explain. If real usage later shows the fixed weights misrank obviously-important features, that's a signal to revisit — not something to solve preemptively.

### 6.4 The hallucination guardrail

Every extracted theme must include an `evidence_quote`. Before a theme is accepted, the pipeline verifies that quote is a real substring of the source text (whitespace-normalized). If it isn't, the theme is discarded and logged, not silently kept. This is the single most important AI-specific safeguard in the system — it's what makes "evidence-backed" in the product's core value prop actually true rather than aspirational. It does not catch every failure mode (see §7), but it does catch outright fabrication.

---

## 7. Failure Modes & Mitigations

This is the section a standard PM PRD doesn't have, and an AI PM PRD can't skip.

| Failure mode | Impact | Current mitigation | Gap |
|---|---|---|---|
| LLM fabricates a theme not in the source | Undermines "evidence-backed" claim | Substring-verification guardrail discards unverifiable quotes | Guardrail can't catch a *paraphrased* fabrication that happens to match a real substring out of context |
| Over-clustering (distinct asks merged) | PM sees a diluted, less actionable feature | 0.80 similarity threshold | Threshold untuned against labeled data; no current way to detect this happening except manual inspection |
| Under-clustering (same ask splits into multiple clusters) | Feature appears lower-priority than it is (lower `mention_count`) | None currently | Real gap — no dedup pass after clustering |
| Sentiment misclassification | Skews `sentiment_weight`, distorts ranking | None beyond the LLM's own judgment | No human-labeled eval set to measure this against |
| Provider rate limits / outage (Groq or Gemini) | `/analyze` fails entirely mid-run | Free-tier limits are generous relative to current volume | No retry/backoff logic, no fallback provider |
| Empty extraction on ambiguous/short text | Cluster/score tables silently get nothing for that source | `extract_themes` returns `{"themes": []}` gracefully | No user-facing signal when a source yields zero themes |

None of these are currently instrumented or measured — there's no eval harness yet. That's the single highest-leverage next investment from an AI-PM-rigor standpoint (see §9).

---

## 8. Data & Cost Considerations

- **Storage:** raw feedback text is stored unredacted in `feedback_sources.raw_text`. No PII detection/redaction exists. Acceptable for a personal portfolio project with synthetic/test data; would be a hard blocker before any real user data touches this system.
- **Cost:** Groq's free tier requires no card and cannot incur charges. Gemini embeddings are billed per the standard API rate once past free quota. At current test volume, cost is effectively zero. This will need real modeling before any claim about unit economics at scale.
- **Latency:** each `/analyze` call is synchronous and blocks on sequential LLM calls (one extraction call per document, one embedding call per theme). This is fine at demo scale (single digits of documents) and will not scale to the PRD's original "under 3 minutes for ~50 docs" target without batching or async processing — currently unverified against that target.

---

## 9. Evaluation Strategy (currently a gap, stated explicitly)

There is no offline evaluation set today — no labeled data to measure extraction precision/recall, clustering correctness, or sentiment accuracy against. This PRD names it rather than glossing over it, because "how do you know it's working" is the first question any AI PM should expect in an interview about this project, and the honest current answer is "manual spot-checking of pipeline output," not a rigorous eval.

**Next step, not yet started:** hand-label a small set (10–20 documents) with expected themes/clusters/sentiment, and measure the pipeline against it. This becomes the basis for the PRD's original product metric ("≥60% of surfaced features rated non-obvious but correct") — currently that number is aspirational, not measured.

---

## 10. Success Metrics (unchanged targets, honest status)

| Metric | Target | Current status |
|---|---|---|
| % of surfaced features rated "non-obvious but correct" | ≥60% | Not measured — no eval set |
| % of rankings traceable to source in <2 clicks | 100% | Structurally true (evidence stored per theme) but not yet exposed in any UI |
| Time from upload to ranked output, ~50 docs | <3 min | Not tested at that volume |
| Portfolio metric | Demoable, explainable product | On track — backend pipeline and persistence layer both verified working end-to-end |

## 11. Risks

| Risk | Status |
|---|---|
| LLM hallucination | Partially mitigated (guardrail); not eliminated |
| Scope creep into full analytics suite | Actively managed — Command Center scoped to PRD-derived metrics only, not generic dashboard filler |
| Untuned clustering threshold | Open, tracked in §6.2 |
| No eval harness | Open, tracked in §9 |
| Two-provider dependency (Groq + Gemini) | Accepted trade-off; no fallback currently |

## 12. Open Questions

- Should the similarity threshold be tunable per-run, or does that reintroduce the "premature configurability" problem the fixed sentiment rubric was designed to avoid?
- At what document volume does synchronous, sequential API calling become a real latency problem — and is background job processing worth the complexity before real users exist?
- Does a genuine eval set get built before or after the remaining frontend pages? (Current lean: after Command Center, before claiming any accuracy number publicly.)

---

## 13. Milestones (updated)

1. ~~Repo, architecture skeleton, auth stub~~ — done
2. ~~Ingestion pipeline: extraction, embeddings, clustering~~ — done
3. ~~RICE-style scoring~~ — done
4. ~~Persistence layer (Supabase, 5-table schema, Alembic)~~ — done
5. ~~`/analyze` writes real data end-to-end~~ — done, verified
6. **Current:** `/dashboard/stats` endpoint — done; Command Center frontend — in progress
7. Opportunities page (ranked feature list with evidence trace-back) — next
8. Analyses, Documents pages
9. Minimal eval set + measured accuracy numbers
10. CI/CD, deployment, demo polish
