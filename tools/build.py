#!/usr/bin/env python3
"""Static site builder for Castle Road Construction.

Pages live in src/pages/*.html. Each starts with a small JSON front-matter block
between two `---` lines, followed by the page body. The builder wraps every body
in the shared <head>, header, footer and icon sprite, then writes the finished
HTML to the repository root.

Inline helpers available in page bodies:
  [[img name | alt text | sizes | class | eager]]   responsive <img> from assets/img
  [[icon name]]                                     <svg> icon from the sprite
  [[phone]] / [[phone_href]]                        business phone number

Run:  python3 tools/build.py
Requires Pillow (pip install pillow) to read image dimensions.
"""
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
IMG = ROOT / "assets" / "img"
ICONS = SRC / "icons"

SITE = {
    "name": "Castle Road Construction",
    "url": "https://www.castleroadconst.com",
    "phone": "410-836-5515",
    "phone_href": "tel:+14108365515",
    "street": "2005 E Churchville Road",
    "city": "Bel Air",
    "region": "MD",
    "zip": "21015",
    "mhic": "121766",
}

NAV = [
    ("home", "Home", "index.html"),
    ("about", "About", "about.html"),
    ("services", "Services", "services.html"),
    ("gallery", "Gallery", "gallery.html"),
    ("contact", "Contact", "contact.html"),
]

WIDTHS = [640, 1280, 2000]


def img_tag(name, alt="", sizes="100vw", cls="", eager=""):
    files = {w: IMG / f"{name}-{w}.webp" for w in WIDTHS}
    files = {w: p for w, p in files.items() if p.exists()}
    if not files:
        raise SystemExit(f"missing image: {name}")
    largest = files[max(files)]
    with Image.open(largest) as im:
        w, h = im.size
    srcset = ", ".join(
        f"assets/img/{p.name} {Image.open(p).size[0]}w" for _, p in sorted(files.items())
    )
    default = files.get(1280) or largest
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    cls_attr = f' class="{cls}"' if cls else ""
    return (
        f'<img src="assets/img/{default.name}" srcset="{srcset}" sizes="{sizes}" '
        f'width="{w}" height="{h}" alt="{alt}" {loading} decoding="async"{cls_attr}>'
    )


def icon(name, cls=""):
    c = f"icon {cls}".strip()
    return f'<svg class="{c}" aria-hidden="true" focusable="false"><use href="#i-{name}"/></svg>'


def sprite():
    symbols = []
    for svg in sorted(ICONS.glob("*.svg")):
        body = svg.read_text()
        inner = re.sub(r"^<svg[^>]*>|</svg>\s*$", "", body.strip())
        symbols.append(f'<symbol id="i-{svg.stem}" viewBox="0 0 256 256">{inner}</symbol>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" style="display:none">'
        + "".join(symbols)
        + "</svg>"
    )


def expand(text):
    def repl(m):
        parts = [p.strip() for p in m.group(1).split("|")]
        kind, *rest = parts[0].split(" ", 1)
        if kind == "img":
            args = [rest[0]] + parts[1:]
            return img_tag(*args)
        if kind == "icon":
            return icon(*rest[0].split(" ", 1))
        if kind == "phone":
            return SITE["phone"]
        if kind == "phone_href":
            return SITE["phone_href"]
        raise SystemExit(f"unknown helper: {m.group(0)}")

    return re.sub(r"\[\[(.+?)\]\]", repl, text)


def schema():
    data = {
        "@context": "https://schema.org",
        "@type": "RoofingContractor",
        "name": SITE["name"],
        "url": SITE["url"],
        "telephone": "+1-410-836-5515",
        "foundingDate": "1992",
        "image": f"{SITE['url']}/assets/img/work-new-build-dusk-1280.webp",
        "logo": f"{SITE['url']}/assets/favicon.svg",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["street"],
            "addressLocality": SITE["city"],
            "addressRegion": SITE["region"],
            "postalCode": SITE["zip"],
            "addressCountry": "US",
        },
        "areaServed": [
            {"@type": "AdministrativeArea", "name": "Harford County, MD"},
            {"@type": "State", "name": "Maryland"},
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Home improvement services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}}
                for s in [
                    "Roofing", "Windows and Doors", "Siding", "Trim and Gutters",
                    "Decks and Porches", "Kitchen and Bathroom Remodeling",
                    "Basement Remodeling", "Storm Damage Repair", "Insurance Claims",
                ]
            ],
        },
    }
    return json.dumps(data, separators=(",", ":"))


def head(meta):
    title = meta["title"]
    desc = meta["description"]
    path = meta["path"]
    og = meta.get("og", "work-new-build-dusk")
    canonical = f"{SITE['url']}/{path}".rstrip("/")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{'<base href="/">' if meta.get("base") else ""}
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#12162B">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE['url']}/assets/img/{og}-1280.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/hanken-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/styles.css">
<script type="application/ld+json">{schema()}</script>
<script>document.documentElement.classList.add('js')</script>
</head>"""


LOGO_MARK = """<svg class="logo-mark" viewBox="0 0 220 64" aria-hidden="true" focusable="false">
  <path class="logo-ring" fill-rule="evenodd" d="M110 1C49.8 1 1 15.3 1 32s48.8 31 109 31 109-14.3 109-31S170.2 1 110 1Zm0 4.2c57.3 0 101.4 12.2 101.4 26.8S167.3 58.8 110 58.8 8.6 46.6 8.6 32 52.7 5.2 110 5.2Z"/>
  <text class="logo-crc" x="110" y="42.5" text-anchor="middle">CRC</text>
</svg>"""


def header(active, dark_hero):
    links = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    mobile = []
    for i, (key, label, href) in enumerate(NAV):
        cur = ' aria-current="page"' if key == active else ""
        mobile.append(f'<li style="--i:{i}"><a href="{href}"{cur}>{label}</a></li>')
    tone = " site-header--over" if dark_hero else ""
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="header-sentinel" aria-hidden="true"></div>
<header class="site-header{tone}" data-header>
  <div class="container header-inner">
    <a class="logo" href="index.html" aria-label="Castle Road Construction home">
      {LOGO_MARK}
      <span class="logo-word">Castle Road<br>Construction</span>
    </a>
    <nav class="nav" aria-label="Primary">
      <ul>{''.join(links)}</ul>
    </nav>
    <div class="header-actions">
      <a class="header-phone" href="{SITE['phone_href']}">{icon('phone')}<span>{SITE['phone']}</span></a>
      <a class="btn btn--accent btn--sm header-cta" href="contact.html">Get a free estimate</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" data-menu-toggle>
        <span class="sr-only">Open menu</span>
        <span class="menu-bars" aria-hidden="true"><span></span><span></span></span>
      </button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" data-menu hidden>
  <div class="container mobile-menu-inner">
    <ul class="mobile-links">{''.join(mobile)}</ul>
    <div class="mobile-menu-foot">
      <a class="btn btn--accent btn--block" href="contact.html">Get a free estimate {icon('arrow-right')}</a>
      <a class="btn btn--ghost btn--block" href="{SITE['phone_href']}">{icon('phone')} Call {SITE['phone']}</a>
      <p>{SITE['street']}, {SITE['city']}, {SITE['region']} {SITE['zip']}<br>MHIC #{SITE['mhic']}</p>
    </div>
  </div>
</div>"""


FOOTER_SERVICES = [
    ("Roofing", "roofing"),
    ("Windows & Doors", "windows-doors"),
    ("Siding", "siding"),
    ("Trim & Gutters", "trim-gutters"),
    ("Decks & Porches", "decks"),
    ("Kitchen & Bath", "kitchen-bath"),
    ("Basements", "basements"),
    ("Storm Damage", "storm-damage"),
    ("Insurance Claims", "insurance-claims"),
]


def footer():
    svc = "".join(f'<li><a href="services.html#{a}">{n}</a></li>' for n, a in FOOTER_SERVICES)
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <a class="footer-logo" href="index.html" aria-label="Castle Road Construction home">
        <svg class="logo-full" viewBox="0 0 440 128" aria-hidden="true" focusable="false">
          <path class="logo-ring" fill-rule="evenodd" d="M220 2C99.5 2 2 30.6 2 64s97.5 62 218 62 218-28.6 218-62S340.5 2 220 2Zm0 8.4c114.6 0 202.8 24.4 202.8 53.6S334.6 117.6 220 117.6 17.2 93.2 17.2 64 105.4 10.4 220 10.4Z"/>
          <text class="logo-crc" x="220" y="76" text-anchor="middle">CRC</text>
          <text class="logo-sub" x="220" y="100" text-anchor="middle">CASTLE ROAD CONSTRUCTION</text>
        </svg>
      </a>
      <p class="footer-tagline">Welcome to craftsmanship.</p>
    </div>
    <div class="footer-grid">
      <div>
        <h2 class="footer-h">Services</h2>
        <ul class="footer-list footer-list--cols">{svc}</ul>
      </div>
      <div>
        <h2 class="footer-h">Company</h2>
        <ul class="footer-list">
          <li><a href="about.html">About</a></li>
          <li><a href="gallery.html">Gallery</a></li>
          <li><a href="services.html#reviews">Testimonials</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div>
        <h2 class="footer-h">Visit or call</h2>
        <ul class="footer-list">
          <li><a class="footer-phone" href="{SITE['phone_href']}">{SITE['phone']}</a></li>
          <li><a href="https://www.google.com/maps/dir/?api=1&amp;destination=2005+E+Churchville+Road+Bel+Air+MD+21015" target="_blank" rel="noopener">{SITE['street']}<br>{SITE['city']}, {SITE['region']} {SITE['zip']}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> Castle Road Construction. Licensed and insured. MHIC #{SITE['mhic']}.</p>
      <p>Serving Harford County and all of Maryland since 1992.</p>
    </div>
  </div>
</footer>"""


def build_page(src):
    raw = src.read_text()
    m = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.S)
    if not m:
        raise SystemExit(f"{src.name}: missing front matter")
    meta = json.loads(m.group(1))
    body = expand(m.group(2))
    dark = meta.get("darkHero", False)
    page_cls = meta.get("bodyClass", "")
    html = "\n".join([
        head(meta),
        f'<body class="{page_cls}">',
        sprite(),
        header(meta.get("nav", ""), dark),
        f'<main id="main">\n{body}\n</main>',
        expand(footer()),
        '<script src="assets/js/main.js" defer></script>',
        "</body>\n</html>\n",
    ])
    out = ROOT / meta["out"]
    out.write_text(html)
    print(f"built {out.relative_to(ROOT)}")


if __name__ == "__main__":
    for page in sorted((SRC / "pages").glob("*.html")):
        build_page(page)
