# Castle Road Construction website

A ground-up rebuild of [castleroadconst.com](https://www.castleroadconst.com), replacing the Wix site with a fast, hand-built static site.

## Pages

These are the same pages as the old site, so existing links keep working:

| URL | File | Notes |
| --- | --- | --- |
| `/` | `index.html` | Hero, credentials, services explorer, recent work, storm and insurance, process, testimonials, service area, estimate form |
| `/about` | `about.html` | Company story, facts, guarantees, certifications, products, community work |
| `/services` | `services.html` | All 9 services with deep links (`/services#roofing`, etc.), testimonials, FAQ |
| `/gallery` | `gallery.html` | 22 real job photos with category filters and a full-screen viewer |
| `/contact` | `contact.html` | Contact form, phone, address, directions, map |

## Editing

The finished HTML in the repository root is generated. Edit the sources instead, then rebuild:

```
src/pages/*.html     page content (JSON front matter + HTML body)
src/icons/*.svg      Phosphor icons, bundled into an inline sprite
tools/build.py       shared head, header, footer, schema.org data, image helper
assets/css/styles.css
assets/js/main.js
```

```bash
pip install pillow        # one-time, used to read image sizes
python3 tools/build.py    # regenerates the root *.html files
```

Preview locally with `python3 -m http.server` and open http://localhost:8000.

Inside page bodies:

- `[[img name | alt | sizes | class | eager]]` outputs a responsive `<img>` with width and height set (no layout shift).
- `[[icon name]]` outputs an icon from the sprite.
- `[[phone]]` and `[[phone_href]]` output the business phone.

### Adding photos

Put WebP files in `assets/img/` as `name-640.webp`, `name-1280.webp` and, optionally, `name-2000.webp`. Then reference them with `[[img name | ...]]`. To add one to the gallery, copy any `<li class="tile">` block in `src/pages/gallery.html` and set `data-cat` to one or more of: `exteriors roofing baths porches commercial community`.

## Forms

Both forms (home page estimate and contact page) are set up for **Netlify Forms**. Deploy on Netlify and submissions show up in the Netlify dashboard with no other setup.

To host anywhere else, add `data-endpoint="https://formspree.io/f/XXXX"` (or any service that accepts a form POST) to each `<form>`. If a submission fails, visitors are shown the phone number.

## Deploying

The site is plain static files with no build step on the server.

- **Netlify:** connect the repo; `netlify.toml` is included.
- **Vercel:** connect the repo; `vercel.json` turns on clean URLs (`/about` instead of `/about.html`).
- **Any host:** upload the repository root (the `src/` and `tools/` folders are optional).

Then point the `castleroadconst.com` domain at the new host.

## What's included

- Brand colors taken from the CRC logo (navy `#383E70`, orange `#F26E3D`), with the logo rebuilt as a sharp SVG.
- Self-hosted Archivo and Hanken Grotesk fonts.
- Automatic dark mode, reduced-motion support, keyboard-accessible menu, lightbox and forms.
- Local SEO: per-page titles and descriptions, Open Graph tags, `RoofingContractor` schema.org data, `sitemap.xml` and `robots.txt`.
- Every photo in "Recent work", the gallery, the hero and the testimonials section is Castle Road's own work, taken from the original site. Supporting stock photography (Unsplash license) is used only where no job photo existed: the crew-at-work, storm, plans, family room, trim detail, carpentry and golden-hour CTA images (files prefixed `stock-`).
