# PRD — AI Copilot for Product Managers

**Owner:** Shreyasi
**Status:** Draft v0.1
**Last updated:** July 20, 2026

---

## 1. Problem Statement

Product managers make "what to build next" decisions using scattered, unstructured inputs — customer interview transcripts, support/feedback threads, and product analytics dashboards. Synthesizing these into a prioritized, defensible feature list is manual, slow, and biased toward whoever shouts loudest in the room. There's no single tool that ingests all three input types and surfaces the *actual* patterns.

## 2. Goal

Build an AI copilot that ingests customer interviews, user feedback, and product analytics, and outputs a ranked, evidence-backed list of features users actually want — reducing guesswork in roadmap prioritization.

## 3. Target User

- Primary: Product Managers at early-to-growth stage startups (Seed–Series B), where there's no dedicated PM-ops/insights team.
- Secondary: Founders acting as de facto PMs.

## 4. Non-Goals (v1)

- Not a full roadmapping/Jira-replacement tool.
- Not a real-time analytics platform (assumes exported/uploaded data, not live pipelines).
- Not multi-workspace / enterprise SSO in v1.

## 5. Core User Flow

1. PM uploads inputs: interview transcripts (txt/docx/audio), feedback exports (CSV/Notion/Zendesk), analytics exports (CSV/Mixpanel/Amplitude).
2. System parses and normalizes each source.
3. AI extracts feature signals: explicit asks, implicit pain points, frequency, sentiment, and usage-drop-off correlation.
4. System clusters signals into candidate features, dedupes, and scores each on a rubric (frequency × pain intensity × ease-of-build estimate — RICE-style).
5. PM sees a ranked feature list, each with: supporting quotes/evidence, source count, confidence score, and a "why this ranked here" explanation.
6. PM can chat with the copilot to interrogate a ranking ("show me every interview that mentions X").

## 6. MVP Scope (v1)

| Included | Excluded (v2+) |
|---|---|
| CSV/text upload for feedback + analytics | Audio transcription (Whisper) |
| Manual paste for interview transcripts | Live integrations (Zendesk/Intercom API) |
| LLM-based theme extraction + clustering | Multi-user workspaces |
| RICE-style scoring | Custom scoring model per team |
| Evidence trace-back per feature | Slack/email digest automation |
| Chat interface over ingested corpus (RAG) | Fine-tuned ranking model |

## 7. Success Metrics

- **Product:** % of surfaced features a test-user rates as "non-obvious but correct" (target ≥60%).
- **Trust:** % of rankings where user can trace back to source evidence in <2 clicks.
- **Efficiency:** Time from raw upload to first ranked output (<3 min for ~50 docs).
- **Portfolio metric (for you):** shippable, demo-able product with a clear before/after narrative for interviews.

## 8. Key Risks

| Risk | Mitigation |
|---|---|
| LLM hallucinating features not in source data | Every output feature must cite ≥1 retrievable source chunk; no citation = discarded |
| Small/noisy input sets give unreliable clusters | Set minimum input thresholds; show confidence scores, not false precision |
| Scope creep (this can balloon into a full analytics suite) | Hard MVP boundary above; v2 backlog kept separate |
| Cost of LLM calls at scale | Batch processing, caching embeddings, cheap model for extraction / stronger model only for final synthesis |

## 9. High-Level Architecture

```
[Frontend: Next.js]
   |  upload UI, dashboard, chat
   v
[Backend API: FastAPI]
   |  auth, orchestration, job queue
   v
[Ingestion & Processing Pipeline]
   - Parsers (CSV, txt, docx)
   - Chunking + embeddings
   - Vector DB (pgvector / Pinecone)
   v
[AI/ML Layer]
   - Theme extraction (LLM, structured output)
   - Clustering + dedup
   - RICE-style scoring
   - RAG-based chat over corpus
   v
[Postgres]  <- structured feature/eval data
[Object storage] <- raw uploaded files
```

## 10. Milestones (suggested)

1. **Week 1–2:** Repo, architecture skeleton, auth, upload flow (frontend + backend stub).
2. **Week 3–4:** Ingestion pipeline (parsing, chunking, embeddings, vector store).
3. **Week 5–6:** Theme extraction + clustering + scoring (core AI/ML logic).
4. **Week 7:** Dashboard UI for ranked features + evidence trace-back.
5. **Week 8:** RAG chat interface.
6. **Week 9:** CI/CD hardening, deployment, polish, demo data + walkthrough.

## 11. Open Questions

- Single LLM provider or provider-agnostic (LiteLLM) from day 1?
- Self-host embeddings or use API (cost vs. control)?
- How much of the scoring rubric should be user-configurable vs. fixed for MVP?
