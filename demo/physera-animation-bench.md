# AI Search & Readability Audit — https://www.physera.ai/research/animation

*Generated 2026-10-01 03:00 UTC · live page audit via TinyFish Search + Fetch + Agent*

## Scores

| Overall | AI readability | AI visibility |
|---:|---:|---:|
| **59/100** | 89/100 | 14/100 |

**Verdict:** Significant barriers: AI tools struggle to read or find this page. Work the critical/high findings first.

**After fixing the list below:** projected overall **87/100** (readability 89, visibility 84) — a gain of **+28 points** from same-day fixes.

## Fix today

1. **Site not found for brand query “physera”** (worth ~+12 pts) — Authority & provenance
2. **Not in top-10 for “web animation benchmark”** (worth ~+16 pts) — Search visibility

## Can AI crawlers read this page?

| System | Role | Access |
|---|---|:---:|
| OpenAI (ChatGPT search/chat) | search + user-initiated | ✅ allowed |
| Anthropic (Claude) | search + assistants | ✅ allowed |
| Perplexity | answer engine | ✅ allowed |
| Google (Gemini / AI Overviews) | grounding data | ✅ allowed |
| Meta (Meta AI) | training + assistants | ✅ allowed |
| ByteDance / CC / Apple | other AI crawlers | ✅ allowed |

## Findings (prioritized)

### 🟠 HIGH

#### Authority & provenance · Site not found for brand query “physera”

- **Evidence:** A search for the site's own brand token “physera” surfaced no page from physera.ai in the top 10 — a sign of weak indexing or brand signals.
- **Fix:** Make sure the domain/brand string appears in the <title>, H1, JSON-LD Organization name, and is linked from the homepage nav; submit the URL in Search Console.
- *Impact if fixed: ~+12 pts overall (readability +0, visibility +30) · Source: TinyFish Search*

#### Search visibility · Not in top-10 for “web animation benchmark”

- **Evidence:** TinyFish Search top-10 for “web animation benchmark” is dominated by: www.mdpi.com (#1), motion.dev (#2), www.reddit.com (#3), gsap.com (#4). This page does not appear — AI search engines inherit this ordering when citing sources.
- **Fix:** Align the page to the query: put “web animation benchmark” (or a close variant) in the <title>, H1, first paragraph and one H2; add an FAQ section answering the question behind the query; then interlink to this page from your two highest-authority pages.
- *Impact if fixed: ~+16 pts overall (readability +0, visibility +40) · Source: TinyFish Search*

### 🟡 MEDIUM

#### Machine-readable structure · No H1 survives extraction

- **Evidence:** The extracted HTML contains no <h1> — answer engines use it to anchor what the page is about.
- **Fix:** Make the page headline an <h1> containing the primary keyword, exactly once.
- *Impact if fixed: ~+3 pts overall (readability +5, visibility +0) · Source: TinyFish Fetch*

#### Search visibility · Materially thinner than the pages outranking it

- **Evidence:** Pages above it for 'web animation benchmark' carry 8,445 words and 16 H2 sections (median of the top 2 fetched live: https://www.mdpi.com/2313-433X/12/1/45, https://motion.dev/magazine/web-animation-performance-tier-list); this page extracts 3,650 words and 14 H2s. Depth is a proxy for answer completeness.
- **Fix:** Add roughly 4,795 words covering the sub-questions the leaders answer in their 16 sections — and ship an FAQ block; pages with FAQPage schema are disproportionately lifted into AI answers.
- *Impact if fixed: ~+5 pts overall (readability +4, visibility +6) · Source: TinyFish Search + Fetch (competitor benchmark)*

#### Search visibility · Title/URL miss part of the target query

- **Evidence:** Query terms absent from the page's title and URL: benchmark, web.
- **Fix:** Work these terms into the <title> and H1 naturally (e.g. “… benchmark, web …”).
- *Impact if fixed: ~+3 pts overall (readability +0, visibility +8) · Source: TinyFish Search*

### 🔵 LOW

#### Search visibility · Meta description length off the display window

- **Evidence:** Description is 58 chars (ideal 140–160): “Evaluating Frontier Models on Web Animation Reconstruction”.
- **Fix:** Rewrite to 140–160 chars: what the page answers + one differentiator + a verb.
- *Impact if fixed: ~+1 pts overall (readability +0, visibility +2) · Source: TinyFish Fetch*

### ⚪ INFO

#### Authority & provenance · No llms.txt (opportunity)

- **Evidence:** No /llms.txt found — the emerging convention AI tools use to fetch a curated, markdown map of a site.
- **Fix:** Publish /llms.txt listing your key pages in markdown with one-line descriptions:
  ```
  # <Site name>
  
  > One-sentence what this site is.
  
  ## Pages
  - [This page](<url>): what it answers
  - [Docs](<url>): …
  ```
- *Impact if fixed: ~+1 pts overall (readability +2, visibility +0) · Source: origin HTTP*

#### AI readability · A browsing AI understands the page

- **Evidence:** Agent's one-line read: “A research benchmark called Animation Bench by Physera that evaluates how well frontier multimodal coding agents (GPT-6 Astra, Claude Fable…”. Key facts it extracted: Four frontier models were tested on 48 real-world web animation tasks from 32 l…; Models scored significantly lower on motion consistency (mean 0.38–0.47) than o…; GPT-6 Astra ranked first with an overall score of 0.594, followed by Claude Fab…
- **Fix:** Keep the opening screen this clear; make sure the key facts stay in static text.
- *Source: TinyFish Agent*

## Measured data

### TinyFish Fetch — what an AI extraction layer sees

- extracted **3650 words** / 29,509 chars of markdown
- title: Animation Bench | Physera
- description: Evaluating Frontier Models on Web Animation Reconstruction
- language: en · author: Physera · published: —
- structure in extracted HTML: 0 H1 · 14 H2 · 13 H3 · 118 <p> · 6 lists · 8 tables
- semantic landmarks: main, article, section, table, figure, summary, details
- signals: empty=no · truncated=no · boilerplate-lines=4%
- GEO signals: 8 sentence(s) with concrete stats · 4 question-phrased heading(s) · longest paragraph 94 words

### TinyFish Fetch — extraction gap (HTML view)

- Raw server HTML carries 715 content tags (<p>/<h>/<li>/<td>), while the browser-rendered extraction saw 132 content elements — the gap is what only renders via JavaScript.

### Origin HTML — what search & AI crawlers get

- HTTP 200 · 414,060 bytes raw HTML · redirect=no
- content-type: text/html; charset=utf-8
- `<title>` (25 chars): Animation Bench | Physera
- meta description (58 chars): Evaluating Frontier Models on Web Animation Reconstruction
- canonical: https://physera.ai/research/animation
- meta robots: index, follow
- og:title: Animation Bench | Physera · og:image: present
- JSON-LD: 1 block(s), types: Organization, WebSite
- raw HTML headings: 1 H1 · 14 H2
- images: 231 total · 0 missing alt · hreflang tags: 0

### robots.txt — AI crawler access

- AI crawlers allowed on this path: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent
- sitemaps declared: 1

### llms.txt

- not found (HTTP 404)

### TinyFish Search — visibility for the target query

- query “web animation benchmark” → this page: **not in top-10** (of 10 results)
- query “web animation benchmark physera” → this page: **not in top-10** (of 10 results)
- query “physera” → this page: **not in top-10** (of 10 results)

| # | Who outranks / ranks alongside | URL |
|---|---|---|
| 1 | A Cross-Device and Cross-OS Benchmark of Modern Web ... (www.mdpi.com) | https://www.mdpi.com/2313-433X/12/1/45 |
| 2 | The Web Animation Performance Tier List | Motion Magazine (motion.dev) | https://motion.dev/magazine/web-animation-performance-tier-list |
| 3 | The Web Animation Performance Tier List - Motion Blog (www.reddit.com) | https://www.reddit.com/r/javascript/comments/1opwrvx/the_web_animation_performance_tier_list_motion/ |
| 4 | JavaScript Animation Speed Test (gsap.com) | https://gsap.com/js/speed.html |
| 5 | Master Web Animations in 2 Hours | Build an Awwwards-Level ... (www.youtube.com) | https://www.youtube.com/watch?v=AW1yfBKRMKc |
- note: Page did not appear in the first page (top 10) of TinyFish results for the exact query.

### TinyFish Fetch — competitor benchmark (pages outranking it, fetched live)

| # | Competitor page | Words extracted | H2 sections |
|---|---|---:|---:|
| 1 | A Cross-Device and Cross-OS Benchmark of Modern Web ... — `https://www.mdpi.com/2313-433X/12/1/45` | 8,445 | 16 |
| 2 | The Web Animation Performance Tier List | Motion Magazine — `https://motion.dev/magazine/web-animation-performance-tier-list` | 3,761 | 2 |
| — | **This page** | 3,650 | 14 |

### TinyFish Agent — browsing-AI comprehension probe

- page understood: yes
- one-line read: “A research benchmark called Animation Bench by Physera that evaluates how well frontier multimodal coding agents (GPT-6 Astra, Claude Fable 5.1, GPT-6 Sol, Claude Opus 5.5) can reconstruct web page animations versus static screenshots.”
- key facts extracted:
  - Four frontier models were tested on 48 real-world web animation tasks from 32 live commercial websites, producing 192 total reconstructions.
  - Models scored significantly lower on motion consistency (mean 0.38–0.47) than on visual similarity (mean 0.63–0.71), revealing that while agents can match static appearance, they struggle with timing, sequencing, and interaction behaviors.
  - GPT-6 Astra ranked first with an overall score of 0.594, followed by Claude Fable 5.1 (0.548), GPT-6 Sol (0.516), and Claude Opus 5.5 (0.507), with cost showing little correlation to performance.
- js_required=no · rendered_chars=8700 · nav_links=5

---

*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and llms.txt are checked for what search/AI crawlers are told; [TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens the page in a real browser to test whether a browsing AI can understand it.*
