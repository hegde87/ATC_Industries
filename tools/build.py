#!/usr/bin/env python3
"""Static site builder for ATC Industries.

Pages live in src/pages/*.html as an HTML body fragment with a small front-matter
block. This script wraps every page in the shared <head>, header and footer,
expands {{ shortcodes }}, generates one static page per product from
products.json, and writes the finished HTML, sitemap.xml and robots.txt to the
repository root (which is what the server publishes).

Usage: python3 tools/build.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import re
import shlex
from urllib.parse import quote
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "pages"
MANIFEST = json.loads((ROOT / "assets" / "img" / "manifest.json").read_text())
PRODUCTS = json.loads((ROOT / "products.json").read_text())
TODAY = dt.date.today().isoformat()

SITE = {
    "name": "ATC Industries",
    "tagline": "Smart Plastic Solutions",
    "url": "https://atctemp.parshvaweb.com",
    "email": "atcgoa@gmail.com",
    "phone": "+91 98231 36644",
    "phone_href": "+919823136644",
    "office": "G/11, Jigisha Building, Margao, Goa, India",
    "group": "The Shah Group of Companies",
}

PROCESSES = [
    {
        "slug": "injection-molding",
        "name": "Injection Molding",
        "short": "Precision components molded in engineering polymers.",
        "capacity": "500 MT / annum",
        "image": "Industrial Injection Molding Machine.png",
    },
    {
        "slug": "extrusion-profiles-sheets",
        "name": "Extrusion of Profiles and Sheets",
        "short": "Profiles, sheets, tubes and corrugated hoses.",
        "capacity": "300 MT / annum",
        "image": "Extrusion Line.png",
    },
    {
        "slug": "thermoforming-vacuum-forming",
        "name": "Thermoforming / Vacuum Forming",
        "short": "Radomes, covers, trays and formed panels up to 2.4 × 2.4 m.",
        "capacity": "1,200 MT / annum",
        "image": "Thermoforming Automatic Machine.png",
    },
    {
        "slug": "blow-molding",
        "name": "Blow Molding",
        "short": "Bellows and hollow components for appliances.",
        "capacity": "40 MT / annum",
        "image": "Blow Molding Products Showcase.png",
    },
    {
        "slug": "cutting-high-frequency-welding",
        "name": "Cutting and High Frequency Plastic Welding",
        "short": "CNC cutting and HF welding for fabricated assemblies.",
        "capacity": "On request",
        "image": "machine-hf-1.png",
    },
]

UNITS = [
    {"name": "ATC Industries", "unit": "Unit 1", "address": "Plot S-67, Verna Industrial Estate, Goa", "region": "Verna, Goa", "area": "10,000 sq. ft."},
    {"name": "Asia Trade Combines", "unit": "Unit 2", "address": "Plot O-11, Verna Industrial Estate, Goa", "region": "Verna, Goa", "area": "13,000 sq. ft."},
    {"name": "ATC Poly Industries", "unit": "Unit 3", "address": "Plot C-109, MIDC Supa Parner, Ahmednagar, Maharashtra", "region": "Supa MIDC, Maharashtra", "area": None},
    {"name": "ATC Polylex Industries", "unit": "Unit 4", "address": "D5–6, GIDC Kundai Industrial Estate, Kundaim, Goa", "region": "Kundaim, Goa", "area": None},
]

INTERESTS = [
    "General manufacturing enquiry",
    "Injection molding",
    "Extrusion / profiles",
    "Thermoforming / vacuum forming",
    "Blow molding",
    "Cutting / HF welding",
    "Hose assemblies",
    "Telecom radomes",
    "Contract manufacturing / assembly",
]

# Line icons, 24px grid, 1.75 stroke. One set for the whole site.
ICONS = {
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-up-right": '<path d="M7 17 17 7M8 7h9v9"/>',
    "arrow-left": '<path d="M19 12H5M11 18l-6-6 6-6"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "close": '<path d="M6 6l12 12M18 6 6 18"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m20 20-4.2-4.2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M4.6 4.6l1.8 1.8M17.6 17.6l1.8 1.8M2.5 12H5M19 12h2.5M4.6 19.4l1.8-1.8M17.6 6.4l1.8-1.8"/>',
    "bolt": '<path d="M13 2.5 4.5 13.5H11l-1 8 8.5-11H12l1-8z"/>',
    "leaf": '<path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15"/><path d="M5 19c3-4 6-6.5 9.5-8.5"/>',
    "recycle": '<path d="M7.5 7.5 10 3.5a2 2 0 0 1 3.4 0l1.6 2.6"/><path d="m16.5 11.5 2.8 4.7a2 2 0 0 1-1.7 3H14"/><path d="M10 19.2H6.4a2 2 0 0 1-1.7-3l1.8-3"/><path d="m13 4.5 2 1.8-2.6.9M14 21.5l-1.5-2.3 2.4-1M4.2 13.6l2.3-.5.6 2.5"/>',
    "shield": '<path d="M12 3 5 6v5.5c0 4.5 3 8 7 9.5 4-1.5 7-5 7-9.5V6l-7-3z"/><path d="m9 12 2.2 2.2L15.5 10"/>',
    "factory": '<path d="M3 20V10l5 3V10l5 3V6h3l1 7h4v7H3z"/><path d="M7 17h2M11 17h2M15 17h2"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5 9-5z"/><path d="m3 13 9 5 9-5"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18 14a6.5 6.5 0 0 1 3.5 6"/>',
    "map": '<path d="m9 4-6 2.5v13L9 17l6 2.5 6-2.5v-13L15 6.5 9 4z"/><path d="M9 4v13M15 6.5v13"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    "expand": '<path d="M15 4h5v5M9 20H4v-5M20 4l-6 6M4 20l6-6"/>',
}


# --------------------------------------------------------------------------- helpers

def esc(value: str) -> str:
    return html.escape(value, quote=True)


def asset_version(path: str) -> str:
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:10]


def icon(name: str, cls: str = "icon") -> str:
    return (
        f'<svg class="{cls}" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
        f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>'
    )


def image_entry(name: str) -> dict:
    if name not in MANIFEST:
        raise SystemExit(f"Image not found in manifest: {name!r}. Run tools/optimize_images.py")
    return MANIFEST[name]


def image_url(name: str, max_w: int = 1200) -> str:
    entry = image_entry(name)
    files = [f for f in entry["files"] if f["w"] <= max_w] or entry["files"][:1]
    return "assets/img/" + files[-1]["file"]


def largest_url(name: str) -> str:
    return "assets/img/" + image_entry(name)["files"][-1]["file"]


def srcset(name: str) -> str:
    return ", ".join(f'assets/img/{f["file"]} {f["w"]}w' for f in image_entry(name)["files"])


def img(name: str, alt: str = "", sizes: str = "100vw", cls: str = "", priority: str = "", **_: str) -> str:
    entry = image_entry(name)
    attrs = [
        f'src="{image_url(name, 800)}"',
        f'srcset="{srcset(name)}"',
        f'sizes="{esc(sizes)}"',
        f'width="{entry["width"]}"',
        f'height="{entry["height"]}"',
        f'alt="{esc(alt)}"',
    ]
    if cls:
        attrs.append(f'class="{esc(cls)}"')
    if priority:
        attrs += ['fetchpriority="high"', 'decoding="async"']
    else:
        attrs += ['loading="lazy"', 'decoding="async"']
    return "<img " + " ".join(attrs) + ">"


def figure(name: str, caption: str = "", alt: str = "", sizes: str = "(min-width: 60rem) 30vw, (min-width: 40rem) 45vw, 100vw",
           fit: str = "", group: str = "gallery", cls: str = "", **_: str) -> str:
    classes = " ".join(c for c in ["figure", f"figure--{fit}" if fit else "", cls] if c)
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (
        f'<figure class="{classes}"><a class="figure__link" href="{largest_url(name)}" data-lightbox="{esc(group)}" '
        f'aria-label="View larger: {esc(alt or caption)}">{img(name, alt or html.unescape(caption), sizes)}'
        f'<span class="figure__zoom">{icon("expand")}</span></a>{cap}</figure>'
    )


def btn(href: str, label: str, variant: str = "primary", arrow: str = "arrow-right", extra: str = "") -> str:
    ico = icon(arrow) if arrow else ""
    return f'<a class="btn btn--{variant}" href="{esc(href)}"{extra}><span>{label}</span>{ico}</a>'


# --------------------------------------------------------------------------- partials

NAV = [
    {
        "key": "company",
        "label": "Company",
        "items": [
            ("about.html", "About ATC", "Our story since 1996"),
            ("mission-vision.html", "Mission & Vision", "What drives us"),
            ("leadership.html", "Leadership", "The people behind ATC"),
            ("why-atc.html", "Why Choose ATC", "Nine reasons OEMs work with us"),
        ],
    },
    {"key": "capabilities", "label": "Capabilities", "mega": True},
    {"key": "products", "label": "Products", "href": "products.html"},
    {"key": "quality", "label": "Quality", "href": "quality.html"},
    {"key": "partners", "label": "Partners", "href": "partners.html"},
    {"key": "contact", "label": "Contact", "href": "contact.html"},
]


def current(href: str, path: str) -> str:
    return ' aria-current="page"' if href == path else ""


def header(page: dict) -> str:
    path, active = page["path"], page.get("nav", "")
    items = []
    for entry in NAV:
        is_active = " is-active" if entry["key"] == active else ""
        if "href" in entry:
            items.append(
                f'<li class="nav__item"><a class="nav__link{is_active}" href="{entry["href"]}"{current(entry["href"], path)}>{entry["label"]}</a></li>'
            )
            continue
        sub_id = f'sub-{entry["key"]}'
        if entry.get("mega"):
            proc = "".join(
                f'<li><a class="mega__process" href="{p["slug"]}.html"{current(p["slug"] + ".html", path)}>'
                f'<span class="mega__num">{i:02d}</span><span class="mega__name">{p["name"]}</span>'
                f'<span class="mega__cap">{p["capacity"]}</span></a></li>'
                for i, p in enumerate(PROCESSES, 1)
            )
            more = "".join(
                f'<li><a class="sub__link" href="{h}"{current(h, path)}><span class="sub__title">{t}</span><span class="sub__desc">{d}</span></a></li>'
                for h, t, d in [
                    ("capabilities.html", "All processing capabilities", "Five processes, one partner"),
                    ("contract-manufacturing.html", "Contract Manufacturing & Assembly", "Build-to-print, assembly and kitting"),
                    ("facilities.html", "Our Facilities", "Four units in Goa and Maharashtra"),
                ]
            )
            panel = (
                f'<div class="nav__sub nav__sub--mega" id="{sub_id}"><div class="mega">'
                f'<div class="mega__col"><p class="mega__label">Processes</p><ul class="mega__list">{proc}</ul></div>'
                f'<div class="mega__col mega__col--aside"><p class="mega__label">Services</p><ul class="sub__list">{more}</ul></div>'
                f"</div></div>"
            )
        else:
            links = "".join(
                f'<li><a class="sub__link" href="{h}"{current(h, path)}><span class="sub__title">{esc(t)}</span><span class="sub__desc">{d}</span></a></li>'
                for h, t, d in entry["items"]
            )
            panel = f'<div class="nav__sub" id="{sub_id}"><ul class="sub__list">{links}</ul></div>'
        mega_cls = " nav__item--mega" if entry.get("mega") else ""
        items.append(
            f'<li class="nav__item has-sub{mega_cls}"><button class="nav__link nav__trigger{is_active}" type="button" aria-expanded="false" '
            f'aria-controls="{sub_id}">{entry["label"]}{icon("chevron-down", "icon nav__chev")}</button>{panel}</li>'
        )
    logo = image_entry("atc-logo-transparent.png")
    return f"""<header class="site-header" data-header>
  <div class="utility">
    <div class="container utility__inner">
      <p class="utility__note">{icon("shield")}<span>ISO 9001:2015 certified · OEM plastic components since 1996</span></p>
      <ul class="utility__links">
        <li><a href="tel:{SITE["phone_href"]}">{icon("phone")}<span>{SITE["phone"]}</span></a></li>
        <li><a href="mailto:{SITE["email"]}">{icon("mail")}<span>{SITE["email"]}</span></a></li>
      </ul>
    </div>
  </div>
  <div class="masthead">
    <div class="container masthead__inner">
      <a class="brand" href="index.html" aria-label="ATC Industries home">
        <img class="brand__logo" src="{image_url("atc-logo-transparent.png", 480)}" srcset="{srcset("atc-logo-transparent.png")}" sizes="132px" width="{logo["width"]}" height="{logo["height"]}" alt="ATC Industries — Smart Plastic Solutions">
      </a>
      <nav class="nav" aria-label="Primary">
        <button class="nav__toggle" type="button" aria-expanded="false" aria-controls="nav-panel" data-nav-toggle>
          <span class="nav__toggle-open">{icon("menu")}</span><span class="nav__toggle-close">{icon("close")}</span><span class="nav__toggle-label">Menu</span>
        </button>
        <div class="nav__panel" id="nav-panel" data-nav-panel>
          <ul class="nav__list">{"".join(items)}</ul>
          <div class="nav__actions">
            {btn("contact.html", "Request a quote", "primary", "arrow-right")}
            <a class="nav__phone" href="tel:{SITE["phone_href"]}">{icon("phone")}<span>{SITE["phone"]}</span></a>
          </div>
        </div>
      </nav>
    </div>
  </div>
</header>"""


def footer() -> str:
    proc = "".join(f'<li><a href="{p["slug"]}.html">{p["name"]}</a></li>' for p in PROCESSES)
    units = "".join(f"<li><strong>{u['name']}</strong><span>{u['region']}</span></li>" for u in UNITS)
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer__lead">
      <p class="footer__statement">Have a component in mind?</p>
      <p class="footer__sub">Send us a drawing, sample or specification. Our team will review materials, process and quantities, then come back to you.</p>
      <div class="footer__actions">
        {btn("contact.html", "Request a quote", "light")}
        <a class="footer__contact" href="tel:{SITE["phone_href"]}">{icon("phone")}<span>{SITE["phone"]}</span></a>
        <a class="footer__contact" href="mailto:{SITE["email"]}">{icon("mail")}<span>{SITE["email"]}</span></a>
      </div>
    </div>
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="footer__logo" href="index.html" aria-label="ATC Industries home"><img src="{image_url("atc-logo-transparent.png", 480)}" width="480" height="254" loading="lazy" decoding="async" alt="ATC Industries — Smart Plastic Solutions"></a>
        <p>Part of {SITE["group"]}. Engineering polymer components for OEMs in home appliances, telecom and automotive since 1996.</p>
        <p class="footer__office">{icon("pin")}<span>Registered office: {SITE["office"]}</span></p>
      </div>
      <nav class="footer__col" aria-label="Company">
        <p class="footer__heading">Company</p>
        <ul><li><a href="about.html">About ATC</a></li><li><a href="mission-vision.html">Mission &amp; Vision</a></li><li><a href="leadership.html">Leadership</a></li><li><a href="why-atc.html">Why Choose ATC</a></li><li><a href="facilities.html">Facilities</a></li><li><a href="partners.html">Become a Partner</a></li></ul>
      </nav>
      <nav class="footer__col" aria-label="Capabilities">
        <p class="footer__heading">Capabilities</p>
        <ul>{proc}<li><a href="contract-manufacturing.html">Contract Manufacturing</a></li></ul>
      </nav>
      <div class="footer__col">
        <p class="footer__heading">Manufacturing units</p>
        <ul class="footer__units">{units}</ul>
      </div>
    </div>
    <div class="footer__base">
      <p>© {dt.date.today().year} ATC Industries. All rights reserved.</p>
      <ul><li><a href="products.html">Products</a></li><li><a href="quality.html">Quality &amp; certifications</a></li><li><a href="contact.html">Contact</a></li><li><a href="#top" class="footer__top">Back to top</a></li></ul>
    </div>
  </div>
</footer>"""


def field(fid: str, label: str, kind: str = "text", required: bool = False, auto: str = "", placeholder: str = "", hint: str = "") -> str:
    req = " required" if required else ""
    star = '<span class="field__req" aria-hidden="true">*</span>' if required else '<span class="field__opt">Optional</span>'
    ac = f' autocomplete="{auto}"' if auto else ""
    ph = f' placeholder="{esc(placeholder)}"' if placeholder else ""
    hint_html = f'<p class="field__hint" id="{fid}-hint">{hint}</p>' if hint else ""
    described = f"{fid}-error" + (f" {fid}-hint" if hint else "")
    if kind == "textarea":
        control = f'<textarea id="{fid}" name="{fid}" rows="5"{req}{ph} aria-describedby="{described}"></textarea>'
    else:
        control = f'<input id="{fid}" name="{fid}" type="{kind}"{req}{ac}{ph} aria-describedby="{described}">'
    return (
        f'<div class="field"><label for="{fid}">{label}{star}</label>{control}{hint_html}'
        f'<p class="field__error" id="{fid}-error" hidden></p></div>'
    )


def select(fid: str, label: str, options: list[str]) -> str:
    opts = "".join(f"<option>{esc(o)}</option>" for o in options)
    return f'<div class="field"><label for="{fid}">{label}</label><div class="select"><select id="{fid}" name="{fid}">{opts}</select>{icon("chevron-down")}</div></div>'


def form_status() -> str:
    return f"""<div class="form__status" data-form-status hidden tabindex="-1">
      <p class="form__status-title">{icon("check")}<span>Your enquiry is ready in your email app.</span></p>
      <p>If no email window opened, copy the enquiry and send it to <a href="mailto:{SITE["email"]}">{SITE["email"]}</a>, or call <a href="tel:{SITE["phone_href"]}">{SITE["phone"]}</a>.</p>
      <button class="btn btn--secondary btn--small" type="button" data-copy-enquiry>{icon("copy")}<span>Copy enquiry</span></button>
    </div>"""


def rfq_form(heading: str = "Request a quotation", **_: str) -> str:
    return f"""<form class="form" id="rfq" data-mail-form="rfq" novalidate>
  <h2 class="form__title">{heading}</h2>
  <p class="form__intro">Share what you need. Drawings and samples can follow by email.</p>
  <div class="form__grid">
    {field("name", "Your name", required=True, auto="name")}
    {field("company", "Company", required=True, auto="organization")}
    {field("email", "Email", "email", required=True, auto="email")}
    {field("phone", "Phone", "tel", auto="tel")}
    {select("interest", "Product or service", INTERESTS)}
    {field("quantity", "Estimated annual quantity", placeholder="e.g. 50,000 pcs")}
  </div>
  {field("message", "Your requirements", "textarea", required=True, placeholder="Component, application, material, drawing reference, target quantities…")}
  <button class="btn btn--primary btn--block" type="submit"><span>Prepare email enquiry</span>{icon("arrow-right")}</button>
  <p class="form__note">Submitting opens your email app with the enquiry filled in. Nothing is stored on this website.</p>
  {form_status()}
</form>"""


def partner_form(**_: str) -> str:
    return f"""<form class="form" id="partnerForm" data-mail-form="partner" novalidate>
  <h2 class="form__title">Partnership enquiry</h2>
  <p class="form__intro">Tell us about your business and the markets you serve.</p>
  <div class="form__grid">
    {field("partnerCompany", "Company name", required=True, auto="organization")}
    {field("partnerName", "Contact person", required=True, auto="name")}
    {field("partnerEmail", "Email", "email", required=True, auto="email")}
    {field("partnerPhone", "Phone", "tel", required=True, auto="tel")}
    {field("partnerLocation", "City / region", required=True, auto="address-level2")}
    {select("partnerType", "Partnership interest", ["Dealer / distributor", "OEM supply partnership", "Manufacturing collaboration", "Other business enquiry"])}
  </div>
  {field("partnerDetails", "Your business and experience", "textarea", required=True, placeholder="Current business, products handled, territory and the opportunity you see…")}
  <button class="btn btn--primary btn--block" type="submit"><span>Prepare partnership enquiry</span>{icon("arrow-right")}</button>
  <p class="form__note">Submitting opens your email app with the enquiry filled in. Nothing is stored on this website.</p>
  {form_status()}
</form>"""


def process_index(**_: str) -> str:
    rows = "".join(
        f'<li><a class="pindex__row" href="{p["slug"]}.html"><span class="pindex__num">{i:02d}</span>'
        f'<span class="pindex__main"><span class="pindex__name">{p["name"]}</span><span class="pindex__desc">{p["short"]}</span></span>'
        f'<span class="pindex__cap"><span class="pindex__cap-label">Annual capacity</span>{p["capacity"]}</span>'
        f'<span class="pindex__go">{icon("arrow-right")}</span></a></li>'
        for i, p in enumerate(PROCESSES, 1)
    )
    return f'<ol class="pindex">{rows}</ol>'


def process_aside(slug: str = "", **_: str) -> str:
    links = "".join(
        f'<li><a href="{p["slug"]}.html"{current(p["slug"] + ".html", slug + ".html")}><span>{i:02d}</span>{p["name"]}</a></li>'
        for i, p in enumerate(PROCESSES, 1)
    )
    return f"""<aside class="pside" aria-label="Processing capabilities">
  <p class="pside__title">Processing capabilities</p>
  <ol class="pside__list">{links}</ol>
  <a class="link-arrow" href="capabilities.html">{icon("arrow-left")}<span>All capabilities</span></a>
  <div class="pside__cta">
    <p>Have a part for this process?</p>
    {btn("contact.html?interest=" + quote(next(p["name"] for p in PROCESSES if p["slug"] == slug)), "Enquire", "primary")}
  </div>
</aside>"""


def process_pager(slug: str = "", **_: str) -> str:
    idx = next(i for i, p in enumerate(PROCESSES) if p["slug"] == slug)
    prev_p, next_p = PROCESSES[idx - 1], PROCESSES[(idx + 1) % len(PROCESSES)]
    return f"""<nav class="pager" aria-label="More processes">
  <a class="pager__link" href="{prev_p["slug"]}.html"><span class="pager__dir">{icon("arrow-left")}Previous process</span><span class="pager__name">{prev_p["name"]}</span></a>
  <a class="pager__link pager__link--next" href="{next_p["slug"]}.html"><span class="pager__dir">Next process{icon("arrow-right")}</span><span class="pager__name">{next_p["name"]}</span></a>
</nav>"""


def product_card(p: dict, heading: str = "h3") -> str:
    return (
        f'<li class="pcard" data-cat="{p["group"]}" data-search="{esc((p["title"] + " " + p["category"] + " " + p["description"]).lower())}">'
        f'<a class="pcard__link" href="product-{p["id"]}.html">'
        f'<span class="pcard__media">{img(p["image"], p["alt"], "(min-width: 64rem) 22vw, (min-width: 40rem) 45vw, 100vw")}</span>'
        f'<span class="pcard__body"><span class="pcard__cat">{p["category"]}</span><{heading} class="pcard__title">{p["title"]}</{heading}>'
        f'<span class="pcard__desc">{p["description"]}</span><span class="pcard__more">View product{icon("arrow-right")}</span></span></a></li>'
    )


def product_cards(limit: str = "", exclude: str = "", ids: str = "", **_: str) -> str:
    if ids:
        by_id = {p["id"]: p for p in PRODUCTS}
        items = [by_id[i] for i in ids.split(",")]
    else:
        items = [p for p in PRODUCTS if p["id"] != exclude]
        seen, varied, repeats = set(), [], []
        for p in items:
            (repeats if p["image"] in seen else varied).append(p)
            seen.add(p["image"])
        items = varied + repeats if limit else items
    if limit:
        items = items[: int(limit)]
    return '<ul class="pgrid" data-product-grid>' + "".join(product_card(p) for p in items) + "</ul>"


def unit_list(**_: str) -> str:
    rows = "".join(
        f'<li class="unit"><p class="unit__tag">{u["unit"]} · {u["region"]}</p><h3 class="unit__name">{u["name"]}</h3>'
        f'<p class="unit__addr">{u["address"]}</p>'
        + (f'<p class="unit__meta">Floor area <span class="mono">{u["area"]}</span></p>' if u["area"] else "")
        + "</li>"
        for u in UNITS
    )
    return f'<ul class="units">{rows}</ul>'


def facts(**_: str) -> str:
    data = [
        ("1996", "Established", "Part of The Shah Group of Companies"),
        ("5", "Processing technologies", "Molding, extrusion, forming, welding"),
        ("4", "Manufacturing units", "Across Goa and Maharashtra"),
        ("ISO 9001", "Quality management", "2015 standard · certified by DNV"),
    ]
    items = "".join(
        f'<div class="facts__item"><dt class="facts__label">{label}</dt><dd class="facts__value">{value}</dd><dd class="facts__note">{note}</dd></div>'
        for value, label, note in data
    )
    return f'<dl class="facts">{items}</dl>'


def cta_band(title: str = "Let’s build your next component.", text: str = "Share a drawing, sample or specification and our team will review the right process, material and quantities.", **_: str) -> str:
    return f"""<section class="cta-band" aria-labelledby="cta-band-title">
  <div class="container cta-band__inner">
    <div><h2 class="cta-band__title" id="cta-band-title">{title}</h2><p>{text}</p></div>
    <div class="cta-band__actions">{btn("contact.html", "Request a quote", "primary")}{btn("capabilities.html", "Explore capabilities", "secondary", "")}</div>
  </div>
</section>"""


def map_card(query: str = "", title: str = "", **_: str) -> str:
    q = query.replace(" ", "%20")
    return (
        f'<div class="map" data-map="https://www.google.com/maps?q={q}&amp;output=embed" data-map-title="{esc(title)}">'
        f'<div class="map__placeholder">{icon("map", "icon map__icon")}<p>Map loads from Google only when you ask for it.</p>'
        f'<button class="btn btn--secondary btn--small" type="button" data-map-load><span>Show map</span></button></div></div>'
    )


SHORTCODES = {
    "img": img,
    "figure": figure,
    "rfq_form": rfq_form,
    "partner_form": partner_form,
    "process_index": process_index,
    "process_aside": process_aside,
    "process_pager": process_pager,
    "product_cards": product_cards,
    "units": unit_list,
    "facts": facts,
    "cta_band": cta_band,
    "map": map_card,
}

SHORTCODE_RE = re.compile(r"\{\{\s*(\w[\w-]*)(.*?)\}\}", re.S)


def expand(text: str) -> str:
    def repl(match: re.Match) -> str:
        name, raw = match.group(1), match.group(2).strip()
        tokens = shlex.split(raw) if raw else []
        args, kwargs = [], {}
        for tok in tokens:
            if "=" in tok and re.match(r"^\w[\w-]*=", tok):
                k, v = tok.split("=", 1)
                kwargs[k.replace("-", "_")] = v
            else:
                args.append(tok)
        if name == "icon":
            return icon(args[0], kwargs.get("cls", "icon"))
        if name == "btn":
            return btn(args[0], args[1], kwargs.get("variant", "primary"), kwargs.get("arrow", "arrow-right"))
        if name == "site":
            return esc(SITE[args[0]])
        if name not in SHORTCODES:
            raise SystemExit(f"Unknown shortcode: {name}")
        return SHORTCODES[name](*args, **kwargs)

    return SHORTCODE_RE.sub(repl, text)


# --------------------------------------------------------------------------- page shell

def parse(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    meta: dict = {}
    if text.startswith("---"):
        _, front, text = text.split("---", 2)
        for line in front.strip().splitlines():
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta, text.strip()


def breadcrumb_ld(page: dict) -> dict | None:
    crumbs = page.get("crumbs")
    if not crumbs:
        return None
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"}]
    for i, (label, href) in enumerate(crumbs, 2):
        items.append({"@type": "ListItem", "position": i, "name": label, "item": f'{SITE["url"]}/{href}'})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


def organization_ld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": SITE["url"] + "/#organization",
        "name": SITE["name"],
        "slogan": SITE["tagline"],
        "url": SITE["url"] + "/",
        "logo": SITE["url"] + "/" + largest_url("atc-logo-transparent.png"),
        "email": SITE["email"],
        "telephone": SITE["phone"],
        "foundingDate": "1996",
        "parentOrganization": {"@type": "Organization", "name": SITE["group"]},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "G/11, Jigisha Building",
            "addressLocality": "Margao",
            "addressRegion": "Goa",
            "addressCountry": "IN",
        },
        "location": [
            {"@type": "Place", "name": u["name"], "address": u["address"] + ", India"} for u in UNITS
        ],
        "knowsAbout": [p["name"] for p in PROCESSES],
        "hasCredential": {"@type": "EducationalOccupationalCredential", "name": "ISO 9001:2015", "recognizedBy": {"@type": "Organization", "name": "DNV"}},
    }


def layout(page: dict, body: str) -> str:
    path = page["path"]
    url = SITE["url"] + "/" + ("" if path == "index.html" else path)
    title = page["title"]
    desc = page["description"]
    hero = page.get("hero")
    og = SITE["url"] + "/" + (image_url(page["og"], 1200) if page.get("og") else "assets/img/og-default.jpg")
    css_v, js_v = asset_version("styles.css"), asset_version("site.js")

    preload_hero = ""
    if hero:
        preload_hero = (
            f'<link rel="preload" as="image" href="{image_url(hero, 800)}" imagesrcset="{srcset(hero)}" '
            f'imagesizes="{esc(page.get("hero_sizes", "(min-width: 60rem) 50vw, 100vw"))}" fetchpriority="high">'
        )

    ld = [x for x in [breadcrumb_ld(page)] if x] + page.get("ld", [])
    if path == "index.html":
        ld = [organization_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["url"] + "/", "publisher": {"@id": SITE["url"] + "/#organization"}}] + ld
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = '<meta name="robots" content="noindex, follow">' if page.get("noindex") else ""
    canonical = "" if page.get("noindex") else f'<link rel="canonical" href="{url}">'

    return f"""<!doctype html>
<!-- Generated by tools/build.py from {page["source"]}. Edit the source file, then run: python3 tools/build.py -->
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}{canonical}
<meta name="theme-color" content="#f7fbfb">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ATC Industries">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{esc(page.get("og_title", title))}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="assets/icons/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="assets/fonts/space-grotesk-latin-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ibm-plex-sans-latin-var.woff2" as="font" type="font/woff2" crossorigin>
{preload_hero}
<link rel="stylesheet" href="styles.css?v={css_v}">
{ld_html}
</head>
<body class="page-{path.removesuffix(".html")}" id="top">
<a class="skip-link" href="#main">Skip to main content</a>
{header(page)}
<main id="main" tabindex="-1">
{body}
</main>
{footer()}
<script src="site.js?v={js_v}" defer></script>
</body>
</html>
"""


def crumbs_html(page: dict) -> str:
    crumbs = page.get("crumbs")
    if not crumbs:
        return ""
    parts = ['<li><a href="index.html">Home</a></li>']
    for i, (label, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append(f'<li><span aria-current="page">{esc(label)}</span></li>')
        else:
            parts.append(f'<li><a href="{href}">{esc(label)}</a></li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(parts)}</ol></nav>'


def parse_crumbs(value: str, path: str) -> list:
    out = []
    for part in [p.strip() for p in value.split(">") if p.strip()]:
        label, _, href = part.partition("|")
        out.append((label.strip(), (href.strip() or path)))
    return out


# --------------------------------------------------------------------------- products

def product_page(p: dict) -> tuple[dict, str]:
    path = f'product-{p["id"]}.html'
    proc = next((x for x in PROCESSES if x["slug"] == p.get("process")), None)
    proc_html = (
        f'<div class="spec__row"><dt>Process</dt><dd><a href="{proc["slug"]}.html">{proc["name"]}</a></dd></div>' if proc else ""
    )
    apps = "".join(f"<li>{icon('check')}<span>{a}</span></li>" for a in p.get("highlights", []))
    body = f"""<section class="page-hero page-hero--compact">
  <div class="container">
    {{CRUMBS}}
    <h1 class="page-hero__title">{p["title"]}</h1>
    <p class="page-hero__lede">{p["description"]}</p>
  </div>
</section>
<section class="section">
  <div class="container product">
    <div class="product__media">{figure(p["image"], "", p["alt"], "(min-width: 60rem) 55vw, 100vw", "contain", "product")}</div>
    <div class="product__info">
      <p class="product__cat">{p["category"]}</p>
      <h2 class="product__title">Built to your specification</h2>
      <p>{p["detail"]}</p>
      <ul class="checklist">{apps}</ul>
      <dl class="spec">
        <div class="spec__row"><dt>Category</dt><dd>{p["category"]}</dd></div>
        {proc_html}
        <div class="spec__row"><dt>Specifications</dt><dd>Material grades, dimensions and minimum order quantities on enquiry</dd></div>
      </dl>
      <div class="product__actions">
        {btn("contact.html?interest=" + quote(p["title"]), "Request a quote", "primary")}
        {btn("products.html", "All products", "secondary", "")}
      </div>
    </div>
  </div>
</section>
<section class="section section--tint">
  <div class="container">
    <div class="section-head section-head--row"><h2 class="section-head__title">More products</h2><a class="link-arrow" href="products.html"><span>View all products</span>{icon("arrow-right")}</a></div>
    {product_cards(limit="4", exclude=p["id"])}
  </div>
</section>"""
    ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["title"],
        "description": p["description"],
        "image": SITE["url"] + "/" + image_url(p["image"], 1200),
        "category": p["category"],
        "brand": {"@type": "Brand", "name": SITE["name"]},
        "manufacturer": {"@type": "Organization", "name": SITE["name"], "url": SITE["url"] + "/"},
    }
    meta = {
        "path": path,
        "source": "products.json",
        "title": f'{p["title"]} | ATC Industries',
        "description": f'{p["description"]} OEM supply from ATC Industries, Goa. Request a quotation for your specification.',
        "nav": "products",
        "crumbs": [("Products", "products.html"), (p["title"], path)],
        "og": p["image"],
        "ld": [ld],
    }
    return meta, body


# --------------------------------------------------------------------------- build

def root_relative(out: str) -> str:
    """The 404 page is served at arbitrary depths, so its local URLs must start at the root."""
    out = re.sub(r'((?:href|src)=")(?!https?:|mailto:|tel:|#|/)', r"\1/", out)
    return re.sub(r'(srcset="|, )assets/', r"\1/assets/", out)


def build() -> None:
    pages = []
    for src in sorted(SRC.glob("*.html")):
        meta, body = parse(src)
        meta["path"] = src.name
        meta["source"] = f"src/pages/{src.name}"
        meta["crumbs"] = parse_crumbs(meta.get("crumbs", ""), src.name) if meta.get("crumbs") else []
        pages.append((meta, body))
    pages += [product_page(p) for p in PRODUCTS]

    for meta, body in pages:
        body = expand(body).replace("{CRUMBS}", crumbs_html(meta))
        out = layout(meta, body)
        if meta["path"] == "404.html":
            out = root_relative(out)
        if 'style="' in out:
            raise SystemExit(f"Inline style attribute found in {meta['path']} (blocked by CSP)")
        (ROOT / meta["path"]).write_text(out)
        print("built", meta["path"])

    urls = [m for m, _ in pages if not m.get("noindex")]
    sitemap = "".join(
        f'<url><loc>{SITE["url"]}/{"" if m["path"] == "index.html" else m["path"]}</loc><lastmod>{TODAY}</lastmod></url>' for m in urls
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sitemap}</urlset>\n'
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"sitemap.xml ({len(urls)} urls), robots.txt")


if __name__ == "__main__":
    build()
