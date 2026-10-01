# SEO Page Auditor — "Can AI read my page, and can search find it?"

**AI Search & Readability Auditor built on [TinyFish](https://www.tinyfish.ai).**
Give it any live URL (plus, optionally, the search query you care about) and it tells you:

- **What an AI tool actually sees** when it fetches the page — TinyFish Fetch is run twice (markdown + semantic HTML), exactly the extraction layer an LLM pipeline consumes.
- **Whether a browsing AI can understand it** — one TinyFish Agent run opens the page in a real browser and answers: *what is this page, what are the key facts, does content require JS, is anything walling it off?*
- **How visible it is in search, and to whom it loses** — TinyFish Search runs the target query and the brand query, rank-stable, showing position, the exact snippet shown, and the competitor pages that outrank it.
- **What crawlers are told** — raw origin HTML, `robots.txt` (per-AI-crawler: GPTBot, ClaudeBot, PerplexityBot, Google-Extended, …) and `llms.txt` are checked directly.
- **What to fix today** — every finding cites its measured evidence and ships a concrete fix (exact meta tag, ready-to-paste JSON-LD, exact robots.txt lines to remove). Two 0–100 scores (**AI readability**, **AI visibility**) plus a prioritized findings list.

Output: a Markdown report a site owner can act on the same day (plus machine-readable JSON with `--json`).

## Demo: five live audits, five different stories

Real pages audited with this tool (reports in [`demo/`](demo/), JSON alongside each):

| Page | Target query | Overall | Readability | Visibility | The story |
|---|---|---:|---:|---:|---|
| [tinyfish.ai — Fetch blog post](demo/tinyfish-fetch-blog.md) | "production-grade web fetching for AI agents" | **97** | 95 | 100 | AI-ready: ranks #1, extraction clean, Agent summarizes the key stats unprompted, llms.txt present. |
| [stripe.com/pricing](demo/stripe-pricing.md) | "stripe pricing" | **92** | 88 | 98 | Textbook hygiene: rich JSON-LD (`Product` + `FAQPage`), perfect meta, robots open. Only polish-level findings. |
| [linear.app](demo/linear-home.md) | "issue tracking tool" | **64** | 80 | 40 | The gap case: page is *readable* (Agent understands it, extraction clean) but *invisible* for the category query — no JSON-LD, not in top-10, and the live competitor benchmark shows the pages above it carry ~4,300 words vs its 870. Projected **86/100** after the listed fixes. |
| [reddit.com thread](demo/reddit-thread.md) | "tinyfish search and fetch" | **13** | 21 | 0 | The cautionary tale: robots.txt blocks **all 12 major AI crawlers**, content is JS-only, and the browsing AI hit a 403 wall. AI tools literally cannot see or read it. Projected **74/100** after fixes. |
| [physera.ai — Animation Bench](demo/physera-animation-bench.md) | "web animation benchmark" | **59** | 89 | 14 | The invisible-but-readable case: the browsing AI nails the page ("a research benchmark … that evaluates how well frontier multimodal coding agents …"), extraction is clean — but it's not in the top-10 for its own category, the brand query finds nothing, and the pages above it carry 8,445 words vs its 3,650. Projected **87/100** after fixes. |

Each report carries:

- a **"Can AI crawlers read this page?"** access matrix (OpenAI / Anthropic / Perplexity / Google / Meta / others) from robots.txt verdicts,
- a **"Fix today"** list where every item shows its **point impact** (e.g. "worth ~+18 pts") and cites its measured evidence,
- a **projected score** if the same-day list is fixed (e.g. Reddit: 13 → 74),
- when the page loses its target query, a **competitor benchmark**: the pages outranking it are fetched live with TinyFish Fetch and compared on extracted words and section count — with a concrete "add ~N words covering the sub-questions in their M sections" instruction.

## Robustness — stress-tested on the edge cases

The engine was deliberately run against hostile inputs to flush out false positives, then hardened:

- **Thin pages** (example.com): extraction-floor scoring instead of misleading head-tag noise.
- **PDFs** (an arxiv.org paper): recognized via `Content-Type` — one honest critical finding ("publish an HTML version"), and the PDF is *not* punished with missing-canonical/JSON-LD/OG findings that make no sense for a binary document.
- **Non-English pages** (de.wikipedia.org): UA-gated origins get an automatic honest-bot-UA retry (Wikipedia 403s generic browser strings but serves honest crawlers — and the report says so either way), and meaningless brand tokens (`de`, `v2`) are never probed as "brand queries".
- **Dead domains**: clean critical findings ("origin unreachable", "AI fetchers cannot extract"), no crashes, no invented positives.

## Quick start

```bash
cd seo-auditor
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
export TINYFISH_API_KEY=...   # never commit this

.venv/bin/seo-audit https://example.com/blog/my-post "best running shoes 2026" -o report.md --json
```

Useful flags:

| Flag | What it does |
|---|---|
| `query` (positional, optional) | The search query whose results page you want to rank in |
| `-o report.md` | Write the Markdown report to a file |
| `--json` | Also write `report.json` (full measured data, findings, scores) |
| `--no-browser` | Skip the TinyFish Agent probe (the one metered call) |
| `--fail-under N` | Exit 1 when the overall score is below N — CI gate for AI-readiness |
| `--location` / `--language` | Geo/language for the Search probes (e.g. `US` / `en`) |

Exit code `2` = TinyFish API problem (missing key, rate limit, outage). Findings never crash the audit: each probe degrades independently.

## How TinyFish is used (and why it can't be faked with canned data)

| TinyFish endpoint | Role in the audit | Why it matters |
|---|---|---|
| **Fetch** (`api.fetch.tinyfish.ai`) | Two live probes per audit: `format: markdown` (the LLM view: words, title/description metadata, extraction completeness) and `format: html` (which headings/paragraphs/lists/semantic elements survive extraction). Always `ttl: 0` — a forced live fetch, never a cached copy. | This *is* what an AI tool is fed. If Fetch can't extract it, an AI can't read it. The gap between the browser-rendered extraction and raw origin HTML exposes JS-only content. |
| **Search** (`api.search.tinyfish.ai`) | Runs the target query (and `query + brand`, and the brand alone) against live, rank-stable results: position, snippet shown, competitor URLs. | Search position is what AI search engines inherit when picking sources to cite. The snippet is compared against the page's own description. |
| **Agent** (`agent.tinyfish.ai`) | One goal-driven browser run with structured output (`output_schema`): page understanding, key facts, JS requirement, render blockers. | AI assistants browse; they don't just fetch. This catches walls and JS-only content that extraction alone can't see. |

Every audit is against the **live page** — Fetch with `ttl: 0`, fresh origin HTTP requests, fresh searches. No saved copies, no fixtures in production code (fixtures exist only in offline tests).

## Scoring model

- **AI readability (0–100)** — penalties per finding, e.g. empty extraction −45, `noindex` −40, PDF document −40 (floored: extracted text still earns partial credit), JS-only rendering −30, no JSON-LD −8 … (see `seo_auditor/findings.py::compute_scores`; every deduction maps to a finding id).
- **AI visibility (0–100)** — e.g. not-in-top-10 −40, robots-blocking AI crawlers −45, brand query miss −30, top-3 rank +8 …
- **Overall** = weighted mix (70/30 readability/visibility; 60/40 when a target query is given).

## Development

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check . && .venv/bin/ruff format --check .
.venv/bin/mypy seo_auditor
.venv/bin/pytest -q
```

Tests are fully offline: all TinyFish/HTTP calls are mocked at the client boundary, including failure paths (rate limits, non-200s, robots edge cases, agent failures).

## Project layout

```
seo_auditor/
  tinyfish_client.py  # Search / Fetch / Agent wrappers (retries, auth, error types)
  readability.py      # Fetch probes: markdown + semantic-HTML extraction metrics
  technical.py        # Origin HTML head/meta/JSON-LD, robots.txt, llms.txt
  visibility.py       # Search probes: rank, competitors, snippet alignment
  browser_probe.py    # Agent probe: browsing-AI comprehension
  findings.py         # evidence-backed findings, concrete fixes, scores
  report.py           # Markdown report rendering
  audit.py            # orchestration
  cli.py              # `seo-audit` entrypoint
```
