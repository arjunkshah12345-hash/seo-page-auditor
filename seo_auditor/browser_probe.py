"""Browser-level comprehension probe via TinyFish Agent (endpoint 3, metered).

Fetch shows what a *fetcher* extracts. But AI assistants increasingly browse:
they open the page in a real browser, wait for JS, and read what renders.
This probe sends one goal-driven TinyFish Agent run that reads the page like
an AI assistant would and reports whether it can understand and answer from it.

Kept to a single metered run per audit; skippable with --no-browser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import tinyfish_client as tf

_GOAL = (
    "You are an AI research assistant evaluating this page for a user. Visit the page and read "
    "what actually renders. Answer strictly in JSON with these keys: "
    '"page_understood" (boolean: true if you can tell what this page is about), '
    '"what_is_this_page" (string: one sentence describing what the page is about), '
    '"key_facts" (array of 3 strings: the three most important facts/claims/figures on the page), '
    '"main_topic_guess" (string), '
    '"nav_links_seen" (integer: how many navigation/action links are visible), '
    '"rendered_content_chars" (integer: rough count of visible text characters), '
    '"js_required" (boolean: true if the useful content only appears with JavaScript), '
    '"render_blockers" (array of strings: anything that blocks reading - cookie wall, paywall, login wall, interstitial)'
)


@dataclass
class BrowserReport:
    attempted: bool = True
    understood: bool | None = None
    summary: str | None = None
    key_facts: list[str] = field(default_factory=list)
    js_required: bool | None = None
    rendered_chars: int | None = None
    nav_links: int | None = None
    render_blockers: list[str] = field(default_factory=list)
    run_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "page_understood": {"type": "boolean"},
        "what_is_this_page": {"type": "string"},
        "key_facts": {"type": "array", "items": {"type": "string"}},
        "main_topic_guess": {"type": "string"},
        "nav_links_seen": {"type": "integer"},
        "rendered_content_chars": {"type": "integer"},
        "render_blockers": {"type": "array", "items": {"type": "string"}},
        "js_required": {"type": "boolean"},
    },
    "required": ["page_understood", "what_is_this_page", "key_facts", "js_required"],
}


def _coerce_bool(v: Any) -> bool | None:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in ("true", "yes", "1")
    return None


def run_browser_probe(url: str) -> BrowserReport:
    rep = BrowserReport()
    try:
        res = tf.agent_run(url, _GOAL, output_schema=_SCHEMA, timeout=420.0)
    except tf.TinyFishError as exc:
        rep.run_error = str(exc)
        return rep
    if res.status != "COMPLETED":
        rep.run_error = res.error or f"agent run status: {res.status}"
        return rep
    data = res.result

    def _int(v: Any) -> int | None:
        try:
            return int(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    rep.understood = _coerce_bool(data.get("page_understood"))
    summary = data.get("what_is_this_page")
    rep.summary = str(summary) if summary else None
    facts = data.get("key_facts")
    if isinstance(facts, list):
        rep.key_facts = [str(x) for x in facts][:5]
    js = data.get("js_required")
    rep.js_required = _coerce_bool(js)
    rep.rendered_chars = _int(data.get("rendered_content_chars"))
    rep.nav_links = _int(data.get("nav_links_seen"))
    blockers = data.get("render_blockers")
    if isinstance(blockers, list):
        rep.render_blockers = [str(x) for x in blockers if x]
    return rep
