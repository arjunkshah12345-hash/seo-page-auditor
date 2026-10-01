"""seo-auditor: AI Search & Readability Auditor built on TinyFish.

Audits a live URL (optionally against a target search query) and reports:
1. What an AI extraction layer sees when it reads the page (TinyFish Fetch).
2. Whether a browsing AI agent can understand and answer from the page (TinyFish Agent).
3. How the page shows up in search for the target query, and who outranks it (TinyFish Search).
4. Whether AI crawlers are allowed in at all (robots.txt / llms.txt / meta robots).
5. Prioritized, evidence-backed findings with concrete fixes.
"""

__version__ = "0.2.0"
