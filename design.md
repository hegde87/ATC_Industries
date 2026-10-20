# ATC Industries — design system

The locked visual system for the site. `styles.css` implements it; change the tokens there, not per component.

## Direction

- **Audience:** OEM procurement and engineering buyers. The primary action is "Request a quote".
- **Tone:** technical and utilitarian — precise, engineered, calm, trustworthy.
- **Genre:** modern-minimal with an industrial register.
- **Macrostructures:** Split Studio for marketing pages (copy beside a photograph), Workbench spec layout for process pages (content plus a sticky process index), Index-first for the capability list.
- **Navigation:** banner (dark utility bar with ISO, phone and email) above a light masthead, with a mega menu for capabilities. The header is light because the teal logo is illegible on dark backgrounds.
- **Footer:** a statement call-to-action followed by a site index.

## Colour

All colours are tokens in `:root`, written as OKLCH with hex fallbacks. Components read the surface roles (`--surface`, `--fg`, `--fg-2`, `--fg-3`, `--line`, `--accent-fg`, `--ring`); `.surface-night` swaps them for dark bands.

| Token | Use |
| --- | --- |
| `--color-teal` (brand teal, sampled from the logo) | marks, rules, active indicators |
| `--color-teal-ink` | teal text and links on light surfaces (AA) |
| `--color-teal-deep` | primary button background |
| `--color-teal-on-night` | accents on dark bands |
| `--color-green`, `--color-blue` | logo-ring colours; used only as small marks (values, icons) |
| `--color-paper` / `-2` / `-3`, `--color-raised` | page, tinted sections, image wells, cards |
| `--color-ink` / `-2` / `-3` | text hierarchy (all AA on paper) |
| `--color-night` / `-2` | dark hero and quality band |

The olive/lime from earlier versions is retired; it is not a brand colour.

## Type

- **Display:** Space Grotesk (variable), for headings and navigation on mobile. No italic headings.
- **Body:** IBM Plex Sans (variable, plus italic).
- **Outlier:** IBM Plex Mono 500, only for capacity figures, specifications and step numbers.
- Fonts are self-hosted woff2 with metric-matched fallbacks. The scale is fluid (`--text-*`); body copy is 17px.

## Layout and spacing

- Container 77rem with fluid gutters; section rhythm `--section-y`.
- Spacing scale `--space-3xs` to `--space-3xl`; radii 4 / 8 / 12px.
- Grids use `minmax(min(100%, …), 1fr)` so nothing overflows at 320px.
- Clickable labels never wrap (`white-space: nowrap`).

## Components

Buttons (primary, secondary, light, small, block), link-arrow, facts strip, page hero, breadcrumbs, section head, split, process index rows, process rows, spec table, process sidebar and pager, figure (cover / contain / wide), gallery (auto, 2-up, 3-up), product card and filter, steps, pillars, checklist, quality band, unit cards, values, hexagon reasons (client-requested motif, Why ATC only), services, portrait and quote, eco list, contact channels, click-to-load map, form fields with inline errors, CTA band, footer, lightbox.

## Motion

Short (160ms) and medium (280ms) durations with an ease-out curve. The hero copy rises in once on load. Everything respects `prefers-reduced-motion`.

## Imagery

- Photographs sit in contained frames; infographics and catalogue images are shown with `contain` on a raised well, never cropped or used as darkened banners.
- The approved orange extrusion line is the home and About hero.
- Every image is served as responsive WebP (480–2000w) with explicit dimensions and lazy loading below the fold.

## Accessibility

Skip link, visible focus rings, `aria-current` on navigation, disclosure buttons for submenus (Escape closes), accessible form errors (`aria-invalid` / `aria-describedby`), `lang="en-IN"`, and AA contrast for all text.
