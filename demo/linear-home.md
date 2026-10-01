# AI Search & Readability Audit — https://linear.app/

*Generated 2026-10-01 02:37 UTC · live page audit via TinyFish Search + Fetch + Agent*

## Scores

| Overall | AI readability | AI visibility |
|---:|---:|---:|
| **64/100** | 80/100 | 40/100 |

**Verdict:** Significant barriers: AI tools struggle to read or find this page. Work the critical/high findings first.

**After fixing the list below:** projected overall **86/100** (readability 88, visibility 84) — a gain of **+22 points** from same-day fixes.

## Fix today

1. **No structured data (JSON-LD)** (worth ~+6 pts) — Machine-readable structure
2. **Not in top-10 for “issue tracking tool”** (worth ~+16 pts) — Search visibility

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

#### Machine-readable structure · No structured data (JSON-LD)

- **Evidence:** Zero application/ld+json blocks in the raw HTML — answer engines and AI search rely on schema to classify and cite pages reliably.
- **Fix:** Add this JSON-LD block inside <head> (pre-filled with this page's own data):
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Linear – The system for product development",
    "description": "Purpose-built for planning and building products with AI agents.",
    "url": "https://linear.app/",
    "isPartOf": {
      "@type": "WebSite",
      "name": "linear.app",
      "url": "https://linear.app"
    },
    "publisher": {
      "@type": "Organization",
      "name": "linear.app"
    }
  }
  </script>
  If the page is an article/product, change @type accordingly (Article, Product, …) and add sameAs links to the "linear.app" social profiles.
- *Impact if fixed: ~+6 pts overall (readability +8, visibility +4) · Source: origin HTTP*

#### Search visibility · Not in top-10 for “issue tracking tool”

- **Evidence:** TinyFish Search top-10 for “issue tracking tool” is dominated by: en.wikipedia.org (#1), www.reddit.com (#2), www.happyfox.com (#3), www.atlassian.com (#4). This page does not appear — AI search engines inherit this ordering when citing sources.
- **Fix:** Align the page to the query: put “issue tracking tool” (or a close variant) in the <title>, H1, first paragraph and one H2; add an FAQ section answering the question behind the query; then interlink to this page from your two highest-authority pages.
- *Impact if fixed: ~+16 pts overall (readability +0, visibility +40) · Source: TinyFish Search*

### 🟡 MEDIUM

#### Search visibility · Materially thinner than the pages outranking it

- **Evidence:** Pages above it for 'issue tracking tool' carry 4,258 words and 10 H2 sections (median of the top 2 fetched live: https://en.wikipedia.org/wiki/Comparison_of_issue-tracking_systems, https://www.reddit.com/r/softwaredevelopment/comments/vk9ai5/what_issue_tracking_software_does_your_team_use/); this page extracts 872 words and 6 H2s. Depth is a proxy for answer completeness.
- **Fix:** Add roughly 3,386 words covering the sub-questions the leaders answer in their 10 sections — and ship an FAQ block; pages with FAQPage schema are disproportionately lifted into AI answers.
- *Impact if fixed: ~+5 pts overall (readability +4, visibility +6) · Source: TinyFish Search + Fetch (competitor benchmark)*

#### Search visibility · Title/URL miss part of the target query

- **Evidence:** Query terms absent from the page's title and URL: issue, tool, tracking.
- **Fix:** Work these terms into the <title> and H1 naturally (e.g. “… issue, tool, tracking …”).
- *Impact if fixed: ~+3 pts overall (readability +0, visibility +8) · Source: TinyFish Search*

### 🔵 LOW

#### Authority & provenance · No author or date metadata

- **Evidence:** Fetch found no author and no published date — AI answer engines weight provenance when choosing sources to cite.
- **Fix:** Add author byline markup: <meta name="author" content="…">, a visible byline, and datePublished/author in JSON-LD.
- *Impact if fixed: ~+2 pts overall (readability +3, visibility +0) · Source: TinyFish Fetch*

#### Authority & provenance · No quotable statistics on the page

- **Evidence:** 872 words extracted, but not one sentence contains a concrete number or stat (counts, percentages, timings). Answer engines disproportionately cite passages with verifiable figures.
- **Fix:** Add 2–3 concrete, sourced numbers to the body (e.g. 'cut p95 latency from 40s to 12s across 1,200 runs') near the top of the page.
- *Impact if fixed: ~+2 pts overall (readability +3, visibility +0) · Source: TinyFish Fetch*

#### Machine-readable structure · No question-phrased headings

- **Evidence:** 6 H2 sections, none phrased as a question (Who/What/How/…?). Answer engines chunk pages by headings and match them to user questions when deciding what to cite.
- **Fix:** Rephrase 2–3 H2s as the questions users actually type (e.g. 'How much does … cost?'), and answer each in its first paragraph.
- *Impact if fixed: ~+1 pts overall (readability +2, visibility +0) · Source: TinyFish Fetch*

#### Search visibility · Meta description length off the display window

- **Evidence:** Description is 64 chars (ideal 140–160): “Purpose-built for planning and building products with AI agents.”.
- **Fix:** Rewrite to 140–160 chars: what the page answers + one differentiator + a verb.
- *Impact if fixed: ~+1 pts overall (readability +0, visibility +2) · Source: TinyFish Fetch*

### ⚪ INFO

#### AI readability · A browsing AI understands the page

- **Evidence:** Agent's one-line read: “Linear.app is the homepage for Linear, a product development management system designed for teams to plan, build, and ship software product…”. Key facts it extracted: Linear powers over 40,000 product teams, from ambitious startups to major enter…; The platform is purpose-built for the AI era with AI agents that can draft PRDs…; Key features include Intake & Integrations (converting feedback to issues), Pla…
- **Fix:** Keep the opening screen this clear; make sure the key facts stay in static text.
- *Source: TinyFish Agent*

## Measured data

### TinyFish Fetch — what an AI extraction layer sees

- extracted **872 words** / 6,778 chars of markdown
- title: Linear – The system for product development
- description: Purpose-built for planning and building products with AI agents.
- language: en · author: — · published: —
- structure in extracted HTML: 1 H1 · 6 H2 · 1 H3 · 174 <p> · 1 lists · 0 tables
- semantic landmarks: main, section
- signals: empty=no · truncated=no · boilerplate-lines=6%
- GEO signals: 0 sentence(s) with concrete stats · 0 question-phrased heading(s) · longest paragraph 21 words

### TinyFish Fetch — extraction gap (HTML view)

- Raw server HTML carries 102 content tags (<p>/<h>/<li>/<td>), while the browser-rendered extraction saw 181 content elements — the gap is what only renders via JavaScript.

### Origin HTML — what search & AI crawlers get

- HTTP 200 · 1,287,158 bytes raw HTML · redirect=no
- content-type: text/html; charset=utf-8
- `<title>` (43 chars): Linear – The system for product development
- meta description (64 chars): Purpose-built for planning and building products with AI agents.
- canonical: https://linear.app
- meta robots: —
- og:title: Linear – The system for product development · og:image: present
- JSON-LD: 0 block(s), types: —
- raw HTML headings: 1 H1 · 7 H2
- images: 38 total · 0 missing alt · hreflang tags: 0

### robots.txt — AI crawler access

- AI crawlers allowed on this path: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent
- sitemaps declared: 1

### llms.txt

- found at `https://linear.app/llms.txt` · 10,414 bytes · 27 sections · 157 links

### TinyFish Search — visibility for the target query

- query “issue tracking tool” → this page: **not in top-10** (of 10 results)
- query “issue tracking tool linear” → this page: **#1** (of 7 results)
  - shown as: “Linear – The system for product development”
  - snippet: “A new species of product tool. ... Probably also worth tracking startup timing so we know how often this happens! @Linearcreate issues and assign to me.”
- query “linear” → this page: **#1** (of 10 results)
  - shown as: “Linear – The system for product development”
  - snippet: “A new species of product tool. Purpose-built for modern teams with AI workflows at its core, Linear sets a new standard for planning and building products.”

| # | Who outranks / ranks alongside | URL |
|---|---|---|
| 1 | Comparison of issue-tracking systems (en.wikipedia.org) | https://en.wikipedia.org/wiki/Comparison_of_issue-tracking_systems |
| 2 | What issue tracking software does your team use? Are you ... (www.reddit.com) | https://www.reddit.com/r/softwaredevelopment/comments/vk9ai5/what_issue_tracking_software_does_your_team_use/ |
| 3 | Best Issue Tracking Software for IT & Support Teams 2026 (www.happyfox.com) | https://www.happyfox.com/helpdesk/use-cases/issue-tracking-software/ |
| 4 | Top 6 Issue Tracking Software to Streamline Workflows (www.atlassian.com) | https://www.atlassian.com/agile/project-management/issue-tracking-software |
| 5 | 13 Best bug tracking software tools to adopt during AI boom (pieces.app) | https://pieces.app/blog/best-bug-tracking-software |
- note: Page did not appear in the first page (top 10) of TinyFish results for the exact query.

### TinyFish Fetch — competitor benchmark (pages outranking it, fetched live)

| # | Competitor page | Words extracted | H2 sections |
|---|---|---:|---:|
| 1 | Comparison of issue-tracking systems — `https://en.wikipedia.org/wiki/Comparison_of_issue-tracking_systems` | 4,258 | 10 |
| 2 | What issue tracking software does your team use? Are you ... — `https://www.reddit.com/r/softwaredevelopment/comments/vk9ai5/what_issue_tracking_software_does_your_team_use/` | 1,451 | 0 |
| — | **This page** | 872 | 6 |

### TinyFish Agent — browsing-AI comprehension probe

- page understood: yes
- one-line read: “Linear.app is the homepage for Linear, a product development management system designed for teams to plan, build, and ship software products with AI-powered workflows.”
- key facts extracted:
  - Linear powers over 40,000 product teams, from ambitious startups to major enterprises.
  - The platform is purpose-built for the AI era with AI agents that can draft PRDs, write code, open PRs, and triage issues alongside human developers.
  - Key features include Intake & Integrations (converting feedback to issues), Planning & Monitoring (initiatives, roadmaps, PRDs), AI & Automations (Linear Agent, Coding Sessions), and Build & Ship (Git automations, guided reviews, diffs).
- js_required=no · rendered_chars=8500 · nav_links=10

---

*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and llms.txt are checked for what search/AI crawlers are told; [TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens the page in a real browser to test whether a browsing AI can understand it.*
