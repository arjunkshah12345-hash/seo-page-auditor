# AI Search & Readability Audit — https://www.reddit.com/r/AI_Agents/comments/1slc6ed/we_shipped_4_web_apis_for_ai_agents_today_search/

*Generated 2026-10-01 02:40 UTC · live page audit via TinyFish Search + Fetch + Agent*

## Scores

| Overall | AI readability | AI visibility |
|---:|---:|---:|
| **13/100** | 21/100 | 0/100 |

**Verdict:** Effectively invisible to AI search: most AI tools cannot read this page or never see it. Start with the critical fixes.

**After fixing the list below:** projected overall **74/100** (readability 75, visibility 73) — a gain of **+61 points** from same-day fixes.

## Fix today

1. **robots.txt blocks AI crawlers: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent** (worth ~+18 pts) — AI crawler access
2. **Content only renders via JavaScript** (worth ~+18 pts) — AI readability
3. **Reading blocked by: Network security block by Reddit - 'You've been blocked by network security', Requires login to access Reddit content** (worth ~+6 pts) — AI crawler access
4. **No structured data (JSON-LD)** (worth ~+6 pts) — Machine-readable structure
5. **No meta description / og:description** (worth ~+6 pts) — Search visibility
6. **Not in top-10 for “tinyfish search and fetch”** (worth ~+16 pts) — Search visibility

## Can AI crawlers read this page?

| System | Role | Access |
|---|---|:---:|
| OpenAI (ChatGPT search/chat) | search + user-initiated | ❌ blocked |
| Anthropic (Claude) | search + assistants | ❌ blocked |
| Perplexity | answer engine | ❌ blocked |
| Google (Gemini / AI Overviews) | grounding data | ❌ blocked |
| Meta (Meta AI) | training + assistants | ❌ blocked |
| ByteDance / CC / Apple | other AI crawlers | ❌ blocked |

## Findings (prioritized)

### 🔴 CRITICAL

#### AI crawler access · robots.txt blocks AI crawlers: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent

- **Evidence:** robots.txt disallows this path for GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent. Those systems will never see the page, so AI answer engines cannot cite or recommend it. Matching rules: 


- **Fix:** Edit robots.txt and remove/replace the Disallow rules for these user agents on this path. To allow all AI crawlers explicitly:
  ```
  User-agent: GPTBot
  Allow: /
  User-agent: OAI-SearchBot
  Allow: /
  User-agent: ChatGPT-User
  Allow: /
  User-agent: ClaudeBot
  Allow: /
  User-agent: Claude-Web
  Allow: /
  ```
- *Impact if fixed: ~+18 pts overall (readability +0, visibility +45) · Source: origin HTTP*

#### AI readability · Content only renders via JavaScript

- **Evidence:** Raw server HTML contains only 0 content tags (<p>/<h>/<li>), while TinyFish Fetch — a full browser — extracted 463 words. Crawlers that don't execute JS (and many AI fetchers) see an empty shell.
- **Fix:** Serve the primary content in the initial HTML (SSR/SSG or pre-rendering). Verify: curl -s <url> | grep -c '<p' returns the real paragraph count.
- *Impact if fixed: ~+18 pts overall (readability +30, visibility +0) · Source: origin HTTP + TinyFish Fetch*

### 🟠 HIGH

#### AI crawler access · Reading blocked by: Network security block by Reddit - 'You've been blocked by network security', Requires login to access Reddit content

- **Evidence:** The browsing agent hit these walls before content: Network security block by Reddit - 'You've been blocked by network security', Requires login to access Reddit content.
- **Fix:** Remove or defer the interstitial (cookie/consent/paywall) for first-time crawlers, or at minimum make content reachable without dismissal.
- *Impact if fixed: ~+6 pts overall (readability +10, visibility +0) · Source: TinyFish Agent*

#### Machine-readable structure · No structured data (JSON-LD)

- **Evidence:** Zero application/ld+json blocks in the raw HTML — answer engines and AI search rely on schema to classify and cite pages reliably.
- **Fix:** Add this JSON-LD block inside <head> (pre-filled with this page's own data):
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": "Reddit",
    "description": "One-sentence page description",
    "url": "https://www.reddit.com/r/AI_Agents/comments/1slc6ed/we_shipped_4_web_apis_for_ai_agents_today_search/",
    "isPartOf": {
      "@type": "WebSite",
      "name": "reddit.com",
      "url": "https://reddit.com"
    },
    "publisher": {
      "@type": "Organization",
      "name": "reddit.com"
    }
  }
  </script>
  If the page is an article/product, change @type accordingly (Article, Product, …) and add sameAs links to the "reddit.com" social profiles.
- *Impact if fixed: ~+6 pts overall (readability +8, visibility +4) · Source: origin HTTP*

#### Search visibility · No meta description / og:description

- **Evidence:** Fetch found no description — search engines will improvise snippets and AI answer engines lose the page's self-description.
- **Fix:** Add to <head>: <meta name="description" content="One sentence (140–160 chars) stating what this page answers, including the primary keyword."> and mirror it in og:description.
- *Impact if fixed: ~+6 pts overall (readability +6, visibility +5) · Source: TinyFish Fetch*

#### Search visibility · Not in top-10 for “tinyfish search and fetch”

- **Evidence:** TinyFish Search top-10 for “tinyfish search and fetch” is dominated by: www.tinyfish.ai (#1), github.com (#2), www.tinyfish.ai (#4), www.tinyfish.ai (#5). This page does not appear — AI search engines inherit this ordering when citing sources.
- **Fix:** Align the page to the query: put “tinyfish search and fetch” (or a close variant) in the <title>, H1, first paragraph and one H2; add an FAQ section answering the question behind the query; then interlink to this page from your two highest-authority pages.
- *Impact if fixed: ~+16 pts overall (readability +0, visibility +40) · Source: TinyFish Search*

### 🟡 MEDIUM

#### AI crawler access · robots.txt declares no sitemap

- **Evidence:** No `Sitemap:` line in robots.txt — crawlers must discover URLs by links alone.
- **Fix:** Add `Sitemap: https://reddit.com/sitemap.xml` to robots.txt (and make sure that sitemap exists and includes this URL).
- *Impact if fixed: ~+2 pts overall (readability +0, visibility +4) · Source: origin HTTP*

#### AI readability · Useful content requires JavaScript to render

- **Evidence:** The browsing agent confirms content only appears after JS execution — full-browser fetchers cope, lighter AI fetchers and some search crawlers do not.
- **Fix:** Pre-render the primary content server-side (SSR/SSG).
- *Impact if fixed: ~+2 pts overall (readability +4, visibility +0) · Source: TinyFish Agent*

#### AI readability · Rendered page is text-light

- **Evidence:** Agent estimated ~0 visible characters on the rendered page.
- **Fix:** Add substantive text content: answer paragraph, FAQ, specs/details in static HTML.
- *Impact if fixed: ~+2 pts overall (readability +4, visibility +0) · Source: TinyFish Agent*

#### Machine-readable structure · Long page with zero H2 sections

- **Evidence:** 463 words but no <h2> anywhere in the extracted HTML — answer engines chunk pages by headings when citing sources.
- **Fix:** Split the content into 3–6 sections with descriptive <h2> headings phrased as the questions users ask.
- *Impact if fixed: ~+3 pts overall (readability +5, visibility +0) · Source: TinyFish Fetch*

#### Search visibility · Title/URL miss part of the target query

- **Evidence:** Query terms absent from the page's title and URL: fetch, tinyfish.
- **Fix:** Work these terms into the <title> and H1 naturally (e.g. “… fetch, tinyfish …”).
- *Impact if fixed: ~+3 pts overall (readability +0, visibility +8) · Source: TinyFish Search*

#### Search visibility · Title length outside the display window

- **Evidence:** Title is 88 chars: “We shipped 4 web APIs for AI agents today - Search, Fetch, Browser, Agent. : r/AI_Agents”. Search snippets truncate around 60 chars.
- **Fix:** Rewrite to 50–60 chars, front-load the primary keyword, keep the brand suffix: e.g. “<Primary Keyword> — <Brand>”.
- *Impact if fixed: ~+4 pts overall (readability +4, visibility +4) · Source: TinyFish Fetch*

### 🔵 LOW

#### Machine-readable structure · 2 H1 tags on one page

- **Evidence:** Extraction found 2 <h1> elements; a single H1 makes the page topic unambiguous.
- **Fix:** Demote all but the main headline to <h2>.
- *Impact if fixed: ~+1 pts overall (readability +2, visibility +0) · Source: TinyFish Fetch*

#### Machine-readable structure · No canonical link

- **Evidence:** No <link rel="canonical"> in the raw HTML — duplicate URLs (params, trailing slashes) can split ranking signals.
- **Fix:** Add to <head>: <link rel="canonical" href="https://www.reddit.com/r/AI_Agents/comments/1slc6ed/we_shipped_4_web_apis_for_ai_agents_today_search/">.
- *Impact if fixed: ~+1 pts overall (readability +0, visibility +3) · Source: origin HTTP*

#### Search visibility · Fewer content sections than the pages outranking it

- **Evidence:** The top-ranked pages for 'tinyfish search and fetch' average 5 H2 sections; this page has 0. Sections are how answer engines chunk and cite a page.
- **Fix:** Split the content into ~5 question-titled H2 sections, each answerable standalone.
- *Impact if fixed: ~+5 pts overall (readability +4, visibility +6) · Source: TinyFish Search + Fetch (competitor benchmark)*

#### Search visibility · Incomplete Open Graph tags

- **Evidence:** og:title=MISSING, og:description=MISSING — previews in social/chat surfaces (a growing AI-referral channel) render blank.
- **Fix:** Add og:title, og:description, og:image, og:url mirroring the <title> and meta description.
- *Impact if fixed: ~+2 pts overall (readability +2, visibility +2) · Source: origin HTTP*

### ⚪ INFO

#### AI readability · A browsing AI understands the page

- **Evidence:** Agent's one-line read: “A Reddit post in r/AI_Agents about TinyShip/ TinyFish announcing the release of 4 web APIs (Search, Fetch, Browser, and Agent) designed for…”. Key facts it extracted: TinyFish shipped 4 web APIs for AI agents: Search, Fetch, Browser, and Agent; These APIs solve common building-block problems for AI agent development; The Search and Fetch APIs were later made free for anyone building agents
- **Fix:** Keep the opening screen this clear; make sure the key facts stay in static text.
- *Source: TinyFish Agent*

## Measured data

### TinyFish Fetch — what an AI extraction layer sees

- extracted **463 words** / 3,195 chars of markdown
- title: We shipped 4 web APIs for AI agents today - Search, Fetch, Browser, Agent. : r/AI_Agents
- description: —
- language: en · author: — · published: 2026-04-14T15:34:42.861Z
- structure in extracted HTML: 2 H1 · 0 H2 · 0 H3 · 32 <p> · 0 lists · 0 tables
- semantic landmarks: main, section, summary, details
- signals: empty=no · truncated=no · boilerplate-lines=0%
- GEO signals: 3 sentence(s) with concrete stats · 0 question-phrased heading(s) · longest paragraph 105 words

### TinyFish Fetch — extraction gap (HTML view)

- Raw server HTML carries 0 content tags (<p>/<h>/<li>/<td>), while the browser-rendered extraction saw 34 content elements — the gap is what only renders via JavaScript.

### Origin HTML — what search & AI crawlers get

- HTTP 200 · 8,475 bytes raw HTML · redirect=no
- content-type: text/html
- `<title>` (6 chars): Reddit
- meta description (0 chars): —
- canonical: —
- meta robots: —
- og:title: — · og:image: —
- JSON-LD: 0 block(s), types: —
- raw HTML headings: 0 H1 · 0 H2
- images: 0 total · 0 missing alt · hreflang tags: 0

### robots.txt — AI crawler access

- AI crawlers allowed on this path: none
- **AI crawlers blocked:** GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent
- **Search crawlers blocked:** Googlebot, Bingbot
- sitemaps declared: 0

### llms.txt

- found at `https://www.reddit.com/llms.txt` · 8,405 bytes · 0 sections · 0 links

### TinyFish Search — visibility for the target query

- query “tinyfish search and fetch” → this page: **not in top-10** (of 10 results)
- query “tinyfish search and fetch reddit” → this page: **#2** (of 10 results)
  - shown as: “We shipped 4 web APIs for AI agents today - Search, Fetch ...”
  - snippet: “TinyFish Search + Fetch are free now — for anyone building agents. 17 upvotes · 10 comments. TinyFish plugin for free web search & extract · r ...”
- query “reddit” → this page: **not in top-10** (of 6 results)

| # | Who outranks / ranks alongside | URL |
|---|---|---|
| 1 | Search and Fetch are now FREE for every agent, ... (www.tinyfish.ai) | https://www.tinyfish.ai/blog/search-and-fetch-are-now-free-for-every-agent-everywhere |
| 2 | TinyFish Cookbook (github.com) | https://github.com/tinyfish-io/tinyfish-cookbook |
| 4 | Pricing (www.tinyfish.ai) | https://www.tinyfish.ai/pricing |
| 5 | TinyFish — Web Infrastructure for AI Agents (www.tinyfish.ai) | https://www.tinyfish.ai/ |
| 6 | Web Search API for AI Agents (www.tinyfish.ai) | https://www.tinyfish.ai/search |
- note: Page did not appear in the first page (top 10) of TinyFish results for the exact query.

### TinyFish Fetch — competitor benchmark (pages outranking it, fetched live)

| # | Competitor page | Words extracted | H2 sections |
|---|---|---:|---:|
| 1 | Search and Fetch are now FREE for every agent, ... — `https://www.tinyfish.ai/blog/search-and-fetch-are-now-free-for-every-agent-everywhere` | 747 | 5 |
| 2 | TinyFish Cookbook — `https://github.com/tinyfish-io/tinyfish-cookbook` | 1,614 | 17 |
| — | **This page** | 463 | 0 |

### TinyFish Agent — browsing-AI comprehension probe

- page understood: yes
- one-line read: “A Reddit post in r/AI_Agents about TinyShip/ TinyFish announcing the release of 4 web APIs (Search, Fetch, Browser, and Agent) designed for AI agents.”
- key facts extracted:
  - TinyFish shipped 4 web APIs for AI agents: Search, Fetch, Browser, and Agent
  - These APIs solve common building-block problems for AI agent development
  - The Search and Fetch APIs were later made free for anyone building agents
- js_required=yes · rendered_chars=0 · nav_links=2
- render blockers: Network security block by Reddit - 'You've been blocked by network security', Requires login to access Reddit content

---

*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and llms.txt are checked for what search/AI crawlers are told; [TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens the page in a real browser to test whether a browsing AI can understand it.*
