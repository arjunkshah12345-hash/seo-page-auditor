# AI Search & Readability Audit — https://stripe.com/pricing

*Generated 2026-10-01 02:34 UTC · live page audit via TinyFish Search + Fetch + Agent*

## Scores

| Overall | AI readability | AI visibility |
|---:|---:|---:|
| **92/100** | 88/100 | 98/100 |

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

#### Search visibility · Title length outside the display window

- **Evidence:** Title is 14 chars: “Pricing & Fees”. Search snippets truncate around 60 chars.
- **Fix:** Rewrite to 50–60 chars, front-load the primary keyword, keep the brand suffix: e.g. “<Primary Keyword> — <Brand>”.
- *Impact if fixed: ~+4 pts overall (readability +4, visibility +4) · Source: TinyFish Fetch*

### 🔵 LOW

#### Authority & provenance · No author or date metadata

- **Evidence:** Fetch found no author and no published date — AI answer engines weight provenance when choosing sources to cite.
- **Fix:** Add author byline markup: <meta name="author" content="…">, a visible byline, and datePublished/author in JSON-LD.
- *Impact if fixed: ~+2 pts overall (readability +3, visibility +0) · Source: TinyFish Fetch*

#### AI readability · Heavy repeated boilerplate in extraction

- **Evidence:** 30% of extracted lines repeat 3+ times (nav/footer/promo residue) — this dilutes the content an AI quotes.
- **Fix:** Wrap navigation and repeated promo blocks in <nav>/<footer> or remove them from the content area so extractors can drop them.
- *Impact if fixed: ~+2 pts overall (readability +3, visibility +0) · Source: TinyFish Fetch*

#### Machine-readable structure · 5 H1 tags on one page

- **Evidence:** Extraction found 5 <h1> elements; a single H1 makes the page topic unambiguous.
- **Fix:** Demote all but the main headline to <h2>.
- *Impact if fixed: ~+1 pts overall (readability +2, visibility +0) · Source: TinyFish Fetch*

#### Search visibility · Search snippet barely matches the query

- **Evidence:** Snippet shown for “stripe pricing”: “Pay monthly. Annual subscription. Paid monthly. Based on a volume tier that works for your business. Starting at $620.00. per month, 1-year…” — little term overlap with the query, so engines may be improvising this page's description.
- **Fix:** Rewrite the meta description to answer the query directly; search engines often adopt a well-written description verbatim.
- *Impact if fixed: ~+2 pts overall (readability +0, visibility +6) · Source: TinyFish Search*

### ⚪ INFO

#### AI readability · A browsing AI understands the page

- **Evidence:** Agent's one-line read: “This is Stripe's official pricing page detailing fee structures and costs for their payment processing and financial services products.”. Key facts it extracted: Standard payments pricing is 2.9% + 30¢ per successful domestic card transactio…; Stripe supports 195+ countries, 135+ currencies, and 100+ payment methods with …; Product categories include Global Payments (Payments, Link, Checkout, Terminal,…
- **Fix:** Keep the opening screen this clear; make sure the key facts stay in static text.
- *Source: TinyFish Agent*

#### Search visibility · Ranks #1 for “stripe pricing”

- **Evidence:** Strong: position 1 for the target query. Protect it.
- **Fix:** Keep this page fresh (update stats/dates) and watch the competitors listed in the report.
- *Source: TinyFish Search*

## Measured data

### TinyFish Fetch — what an AI extraction layer sees

- extracted **3115 words** / 23,421 chars of markdown
- title: Pricing & Fees
- description: Find Stripe fees and pricing information. Find our processing fees for credit cards, pricing models and pay-as-you-go fees for businesses.
- language: en · author: — · published: —
- structure in extracted HTML: 5 H1 · 2 H2 · 6 H3 · 439 <p> · 31 lists · 0 tables
- semantic landmarks: section
- signals: empty=no · truncated=no · boilerplate-lines=30%
- GEO signals: 46 sentence(s) with concrete stats · 0 question-phrased heading(s) · longest paragraph 74 words

### TinyFish Fetch — extraction gap (HTML view)

- Raw server HTML carries 1084 content tags (<p>/<h>/<li>/<td>), while the browser-rendered extraction saw 446 content elements — the gap is what only renders via JavaScript.

### Origin HTML — what search & AI crawlers get

- HTTP 200 · 972,371 bytes raw HTML · redirect=no
- content-type: text/html; charset=utf-8
- `<title>` (18 chars): Pricing &amp; Fees
- meta description (138 chars): Find Stripe fees and pricing information. Find our processing fees for credit cards, pricing models and pay-as-you-go fees for businesses.
- canonical: https://stripe.com/pricing
- meta robots: —
- og:title: Pricing &amp; Fees · og:image: present
- JSON-LD: 1 block(s), types: FAQPage
- raw HTML headings: 153 H1 · 4 H2
- images: 57 total · 0 missing alt · hreflang tags: 89

### robots.txt — AI crawler access

- AI crawlers allowed on this path: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, Google-Extended, Bytespider, CCBot, Applebot-Extended, meta-externalagent
- sitemaps declared: 1

### llms.txt

- found at `https://stripe.com/llms.txt` · 69,923 bytes · 32 sections · 305 links

### TinyFish Search — visibility for the target query

- query “stripe pricing” → this page: **#1** (of 7 results)
  - shown as: “Pricing & Fees”
  - snippet: “Pay monthly. Annual subscription. Paid monthly. Based on a volume tier that works for your business. Starting at $620.00. per month, 1-year contract.”
- query “stripe” → this page: **not in top-10** (of 6 results)

| # | Who outranks / ranks alongside | URL |
|---|---|---|
| 3 | Stripe fees 2026: every rate and what a $100 sale nets you (checkoutpage.com) | https://checkoutpage.com/blog/stripe-processing-fees?srsltid=AU7gw4WdgqSXXDSfwAXl1qaI4ATfO-BYZxWDWmAzFxQlZ20UBiEzZ1g1 |
| 5 | Stripe fees: a complete guide to pricing & costs (wise.com) | https://wise.com/us/blog/stripe-fees |
| 6 | Stripe Fees: Pricing and Calculator (www.nerdwallet.com) | https://www.nerdwallet.com/business/software/learn/stripe-fees |
| 7 | Fees on fees on fees : r/stripe (www.reddit.com) | https://www.reddit.com/r/stripe/comments/1od8hft/fees_on_fees_on_fees/ |

### TinyFish Agent — browsing-AI comprehension probe

- page understood: yes
- one-line read: “This is Stripe's official pricing page detailing fee structures and costs for their payment processing and financial services products.”
- key facts extracted:
  - Standard payments pricing is 2.9% + 30¢ per successful domestic card transaction, with additional fees for international cards (+1.5%), currency conversion (+1%), and manually entered cards (+0.5%)
  - Stripe supports 195+ countries, 135+ currencies, and 100+ payment methods with a 99.999% historical uptime claim and a Forrester-verified 326% return on investment
  - Product categories include Global Payments (Payments, Link, Checkout, Terminal, etc.), Money Management (Connect, Treasury, Issuing), Revenue and Finance Automation (Billing, Tax, Invoicing, Sigma), and More (Radar, Identity, Atlas, Climate, Workflows)
- js_required=no · rendered_chars=8500 · nav_links=106

---

*How this audit works: [TinyFish Fetch](https://docs.tinyfish.ai/fetch-api) reads the live page twice (markdown + semantic HTML) exactly as an AI tool would; the raw origin HTML, robots.txt and llms.txt are checked for what search/AI crawlers are told; [TinyFish Search](https://docs.tinyfish.ai/search-api) shows where the page stands for the target query and who outranks it; and one [TinyFish Agent](https://docs.tinyfish.ai/agent-api) run opens the page in a real browser to test whether a browsing AI can understand it.*
