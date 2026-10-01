# AI Search & Readability Audit — https://www.tinyfish.ai/blog/production-grade-web-fetching-for-ai-agents

*Generated 2026-10-01 02:33 UTC · live page audit via TinyFish Search + Fetch + Agent*

## Scores

| Overall | AI readability | AI visibility |
|---:|---:|---:|
| **97/100** | 95/100 | 100/100 |

**Verdict:** AI-ready: readable by AI tools and visible in search. Keep it fresh.

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

### 🟡 MEDIUM

#### Machine-readable structure · No H1 survives extraction

- **Evidence:** The extracted HTML contains no <h1> — answer engines use it to anchor what the page is about.
- **Fix:** Make the page headline an <h1> containing the primary keyword, exactly once.
- *Impact if fixed: ~+3 pts overall (readability +5, visibility +0) · Source: TinyFish Fetch*

### ⚪ INFO

#### AI readability · A browsing AI understands the page

- **Evidence:** Agent's one-line read: “A TinyFish blog post announcing the launch of the TinyFish Fetch API, a dual-layer web page fetching and content extraction service designe…”. Key facts it extracted: In testing across 200 URLs, over 10% of "successful" fetches returned nearly em…; The Fetch API is a dual-layer service that renders URLs via Chromium, extracts …; The article compares Fetch API with competing tools including Exa, Firecrawl, a…
- **Fix:** Keep the opening screen this clear; make sure the key facts stay in static text.
- *Source: TinyFish Agent*

#### Search visibility · Ranks #2 for “production-grade web fetching for AI agents”

- **Evidence:** Strong: position 2 for the target query. Protect it.
- **Fix:** Keep this page fresh (update stats/dates) and watch the competitors listed in the report.
- *Source: TinyFish Search*

## Measured data

### TinyFish Fetch — what an AI extraction layer sees

- extracted **1302 words** / 8,999 chars of markdown
- title: Reliable Web Fetching for AI Agents | TinyFish Fetch API
- description: Over 10% of successful fetches return near-empty text. TinyFish Fetch API renders in Chromium and returns agent-ready Markdown, HTML, or JSON.
- language: en · author: Chenlu Ji · published: 2026-04-14T13:00:00.000Z
- structure in extracted HTML: 0 H1 · 9 H2 · 4 H3 · 45 <p> · 8 lists · 0 tables
- semantic landmarks: main, article, figure, summary, details
- signals: empty=no · truncated=no · boilerplate-lines=0%
- GEO signals: 2 sentence(s) with concrete stats · 4 question-phrased heading(s) · longest paragraph 48 words

### TinyFish Fetch — extraction gap (HTML view)

- Raw server HTML carries 128 content tags (<p>/<h>/<li>/<td>), while the browser-rendered extraction saw 54 content elements — the gap is what only renders via JavaScript.

### Origin HTML — what search & AI crawlers get

- HTTP 200 · 183,650 bytes raw HTML · redirect=no
- content-type: text/html; charset=utf-8
- `<title>` (72 chars): Reliable Web Fetching for AI Agents | TinyFish Fetch API | TinyFish Blog
- meta description (142 chars): Over 10% of successful fetches return near-empty text. TinyFish Fetch API renders in Chromium and returns agent-ready Markdown, HTML, or JSON.
- canonical: https://www.tinyfish.ai/blog/production-grade-web-fetching-for-ai-agents
- meta robots: —
- og:title: Reliable Web Fetching for AI Agents | TinyFish Fetch API · og:image: present
- JSON-LD: 2 block(s), types: Organization, WebSite, WebPage, ImageObject, BreadcrumbList, BlogPosting, Person
- raw HTML headings: 1 H1 · 9 H2
- images: 11 total · 0 missing alt · hreflang tags: 0

### robots.txt — AI crawler access

- AI crawlers allowed on this path: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent
- sitemaps declared: 1

### llms.txt

- found at `https://www.tinyfish.ai/llms.txt` · 34,539 bytes · 6 sections · 135 links

### TinyFish Search — visibility for the target query

- query “production-grade web fetching for AI agents” → this page: **#2** (of 10 results)
  - shown as: “Production-Grade Web Fetching for AI Agents”
  - snippet: “Fetch API is a dual-layer web page fetching and content extraction service built for AI agents. It renders URLs through Chromium, extracts ...”
- query “production-grade web fetching for AI agents tinyfish” → this page: **not in top-10** (of 0 results)
- query “tinyfish” → this page: **not in top-10** (of 7 results)

| # | Who outranks / ranks alongside | URL |
|---|---|---|
| 1 | We shipped 4 web APIs for AI agents today - Search, Fetch ... (www.reddit.com) | https://www.reddit.com/r/AI_Agents/comments/1slc6ed/we_shipped_4_web_apis_for_ai_agents_today_search/ |
| 3 | Building Production-Grade AI Agents with MCP & A2A (dev.to) | https://dev.to/exploredataaiml/building-production-grade-ai-agents-with-mcp-a2a-a-guide-from-the-trenches-2m96 |
| 4 | Production-Grade A.I. Agents MASTERCLASS (www.youtube.com) | https://www.youtube.com/watch?v=upTlhKQbnsE&xstg=CAMSBhUD_LL2Hw%3D%3D |
| 5 | Agent 101: Launching production-grade agents at scale (nebius.com) | https://nebius.com/blog/posts/launch-production-agents-at-scale |
| 6 | Web Search and Deep Research for AI Agents (www.firecrawl.dev) | https://www.firecrawl.dev/blog/deep-research-for-ai-agents |

### TinyFish Fetch — competitor benchmark (pages outranking it, fetched live)

| # | Competitor page | Words extracted | H2 sections |
|---|---|---:|---:|
| 1 | We shipped 4 web APIs for AI agents today - Search, Fetch ... — `https://www.reddit.com/r/AI_Agents/comments/1slc6ed/we_shipped_4_web_apis_for_ai_agents_today_search/` | 463 | 0 |
| — | **This page** | 1,302 | 9 |

### TinyFish Agent — browsing-AI comprehension probe

- page understood: yes
- one-line read: “A TinyFish blog post announcing the launch of the TinyFish Fetch API, a dual-layer web page fetching and content extraction service designed for AI agents that renders URLs through Chromium and returns structured content in Markdown, HTML, or JSON.”
- key facts extracted:
  - In testing across 200 URLs, over 10% of "successful" fetches returned nearly empty content—enough to pass validation but not enough for AI agents to reason on.
  - The Fetch API is a dual-layer service that renders URLs via Chromium, extracts structured content, and returns it in Markdown, HTML, or JSON, supporting batch processing of up to 10 URLs.
  - The article compares Fetch API with competing tools including Exa, Firecrawl, and Crawl4AI, and includes a curl code example for API usage with SSRF protections.
- js_required=no · rendered_chars=3500 · nav_links=22

---

*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and llms.txt are checked for what search/AI crawlers are told; [TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens the page in a real browser to test whether a browsing AI can understand it.*
