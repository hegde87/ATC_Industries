# ATC Industries website

Static marketing site for ATC Industries (engineering plastic components for OEMs). It is plain HTML, one stylesheet and one small script — no framework and no runtime dependencies. The live preview is served by Coolify (nginx) from the repository root at https://atctemp.parshvaweb.com.

## How the site is built

The HTML files in the repository root are **generated** — do not edit them by hand.

| Edit this | To change |
| --- | --- |
| `src/pages/*.html` | Page content. Each file has a small front-matter block (title, description, breadcrumb, hero image) followed by the page body. |
| `products.json` | Products. One page per product (`product-<id>.html`) is generated from it. |
| `tools/build.py` | Shared header, footer, forms, navigation, contact details and process data (the `SITE`, `PROCESSES` and `UNITS` blocks at the top). |
| `styles.css` | Visual design. Tokens are defined at the top; see `design.md`. |
| `site.js` | Mobile menu, dropdowns, product filter, enquiry forms, maps and image viewer. |

After editing, run (Python 3 with Pillow):

```bash
python3 tools/optimize_images.py   # only when images in assets/ were added or changed
python3 tools/build.py             # regenerates every page, sitemap.xml and robots.txt
python3 tools/check.py             # checks links, images, ids and CSP-safe markup
```

`tools/make_icons.py` regenerates the favicon, touch icons, `site.webmanifest` and the default social-share image.

To preview locally: `python3 -m http.server 8000`, then open http://localhost:8000/.

### Images

Put original images in `assets/`. `optimize_images.py` writes responsive WebP versions to `assets/img/` (480–2000px wide) plus `manifest.json`; pages refer to images by their original filename and the builder picks the right files, sizes and dimensions.

### Deployment

Pushing to `main` and redeploying the Coolify application publishes the site. The nginx configuration adds compression, caching (CSS and JS are cache-busted by the builder) and security headers, including a Content Security Policy — which is why pages must not contain inline `style` attributes or inline scripts (the build fails if they do).

## Important before publication

- Forms prepare an email in the visitor's email app (mailto). Nothing is stored or sent by the website. For a production launch, consider a server-side form with spam protection and a privacy notice.
- Confirm with management: production capacities (cutting / HF welding is shown as "On request"), unit floor areas, certificate scope and validity, and the leadership, mission and vision copy.
- The thermoformed rear-cover product now uses the "Molded Black Industrial Panel Cover" photo; confirm it shows the correct part.
- Map pins are address searches, not verified entrances.
- Higher-resolution originals of the presentation photos (radomes, pallets, HF welder) would improve quality.

## History

- **V7 (October 2026):** full redesign and rebuild — new design system, light header with the logo legible, generated pages from `src/`, responsive WebP images, self-hosted fonts, individual product pages, SEO metadata (canonical, Open Graph, structured data, sitemap), accessibility pass, click-to-load maps, image viewer, and security headers.
- **V6.4:** home and About banners use the approved orange extrusion line.
- **V4–V6:** processing capability pages, contract manufacturing, mission/vision, Why ATC hexagons, product catalogue and presentation photographs. See `README_V4_9.txt` and `README_V5_0.txt` for earlier notes.
