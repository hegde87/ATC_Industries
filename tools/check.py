#!/usr/bin/env python3
"""Static checks for the built site. Run after tools/build.py.

Checks every root *.html file for: unresolved local links and images, missing
#fragment targets, duplicate ids, CSS classes with no rule in styles.css,
leftover template syntax, inline styles/scripts (blocked by the CSP) and
images without alt text. Exits non-zero on any problem.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
CSS = (ROOT / "styles.css").read_text()
CSS_CLASSES = set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"url\([^)]*\)", "", CSS)))
JS_CLASSES = {"is-open", "is-scrolled", "is-locked", "is-active"}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.refs: list[tuple[str, str]] = []
        self.classes: set[str] = set()
        self.problems: list[str] = []
        self.in_ld = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        for c in (a.get("class") or "").split():
            self.classes.add(c)
        if "style" in a:
            self.problems.append(f"inline style on <{tag}>")
        if any(k.startswith("on") for k in a):
            self.problems.append(f"inline event handler on <{tag}>")
        if tag == "script":
            if a.get("type") == "application/ld+json":
                self.in_ld = True
            elif not a.get("src"):
                self.problems.append("inline <script>")
        if tag == "img" and "alt" not in a:
            self.problems.append(f"img without alt: {a.get('src')}")
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append((tag, a[key]))
        for key in ("srcset", "imagesrcset"):
            for part in (a.get(key) or "").split(","):
                if part.strip():
                    self.refs.append((tag, part.strip().split()[0]))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self.in_ld = False


def main() -> int:
    pages = sorted(ROOT.glob("*.html"))
    parsed = {}
    for path in pages:
        p = Page()
        text = path.read_text()
        p.feed(text)
        if "{{" in text or "{CRUMBS}" in text:
            p.problems.append("unexpanded template syntax")
        parsed[path.name] = p

    failures = 0
    unknown_classes: dict[str, set[str]] = {}
    for name, p in parsed.items():
        dupes = {i for i in p.ids if p.ids.count(i) > 1}
        if dupes:
            p.problems.append(f"duplicate ids: {sorted(dupes)}")
        for tag, ref in p.refs:
            u = urlparse(ref)
            if u.scheme or ref.startswith(("mailto:", "tel:", "//")):
                continue
            target = unquote(u.path).lstrip("/") or (name if not u.path else "index.html")
            if u.path == "" and u.fragment:
                target = name
            if not (ROOT / target).exists():
                p.problems.append(f"missing <{tag}> target: {ref}")
                continue
            if u.fragment and target.endswith(".html") and u.fragment not in ("top",):
                if u.fragment not in parsed.get(target, Page()).ids:
                    p.problems.append(f"missing #fragment: {ref}")
        for c in {c for c in p.classes - CSS_CLASSES - JS_CLASSES if not c.startswith("page-")}:
            unknown_classes.setdefault(c, set()).add(name)
        for prob in p.problems:
            print(f"FAIL {name}: {prob}")
            failures += 1

    for c, where in sorted(unknown_classes.items()):
        print(f"WARN class .{c} has no CSS rule (used in {len(where)} page(s), e.g. {sorted(where)[0]})")

    print(f"\nChecked {len(pages)} pages: {failures} failure(s), {len(unknown_classes)} unstyled class name(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
