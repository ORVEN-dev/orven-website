# ORVEN website — editable launch package

Live: https://orven.orven-agency01.workers.dev/ar/ · https://orven.orven-agency01.workers.dev/en/

Read `DELIVERY-REPORT-AR.md` for verified results, limitations, ownership, and remaining decisions. This package contains editable source and deployment configuration, not Cloudflare or Google credentials.

For the 24 October delivery-guarantee and trust-funnel update, read `SALES-FUNNEL-HANDOFF.md` for the approved terms, campaign links, local conversion hooks, current verification and release status. New funnel regression: run `node tests/funnel-browser.cjs` with Playwright and a local preview on port 8774 (or set `TEST_ORIGIN`).

## Edit and preview

Performance maintenance: `tools/responsive_images.py` (Pillow) regenerates uncropped WebP display variants after screenshot changes; the original files remain the lightbox sources. `tools/subset_arabic_fonts.py` (fonttools + brotli) regenerates Arabic webfonts from the retained TTF originals, preserving Arabic shaping, the basic Arabic block, and authored characters. Commit generated assets and their manifest. The standard-library build embeds the authored CSS into each page to avoid blocking CSS requests, and preloads both page-language fonts. Keep editing the original CSS files, not the generated inline styles.

Optional browser regression checks: install Playwright and run `node tests/performance-browser.cjs` against the preview server on port 8773, or set `TEST_ORIGIN`. It checks both languages and widths, original-image zoom, navigation and empty-form validation; it does not send an inquiry.

- `source/content.json`: navigation, all 27 core sections (including home pricing), buttons, FAQs, form messages, and English/Arabic metadata copy.
- `source/cases.json`: the two seven-section case studies.
- `source/privacy.json`: bilingual privacy policy.
- `source/site-config.json`: public contact details, public Turnstile key, site URL, provider configuration. `privacy_reviewed` means the configured text has received an implementation/editorial review; it is not legal certification.
- `source/build.py`: standard-library Python generator. `site.css`, `tokens.css`, and `site.js` control layout, design, motion, and interactions.
- `assets/`: authentic reviewed project screenshots, transparent original logo, fonts and their licences. `reference/` preserves the content brief and asset audit.
- `cloudflare/worker.mjs`: form gateway. `google/Code.gs` and `google/appsscript.json`: Google storage, owner administration and retention.
- `previews/`: actual browser screenshots. The four `home-*-desktop/mobile.jpg` files are full-page 1440/390-pixel previews. Administrative evidence is private handoff material and is not part of `dist`.

From this folder, with Python 3 installed:

```powershell
python source/build.py
python preview.py --port 8770
```

Open http://127.0.0.1:8770/review.html . The review studio switches all pages, languages and 1440/390 widths, allows text editing for review, and exports suggested edits as JSON. Apply approved edits to source files and rebuild; preview edits do not silently modify production. Test real form delivery on the live site: the production Turnstile widget is restricted to its production hostname.

`build.py` without `--production` creates a noindex preview. Rebuild production before deployment:

```powershell
python source/build.py --production
python tests/check_site.py
python tests/check_budgets.py
node --test tests/worker.test.mjs tests/retention.test.mjs
```

After validation, commit the edited source and regenerated `dist/` to `main`. The existing Cloudflare Workers Builds connection for `ORVEN-dev/orven-website` automatically builds and deploys Worker `orven` from `main`. Follow the `Workers Builds: orven` GitHub check to its Cloudflare build record, wait for success, then verify the active version and live site. Routine releases use this Git-connected path; do not publish directly from a local Wrangler command. Wrangler may still run internally as the Cloudflare deploy command; the dashboard associates that release with Build/main. Secrets already exist in the deployed Worker; never put them in `vars`, browser settings, JSON content, a public repository, or this ZIP. Preserve `GAS_SHARED_SECRET`, `GAS_WEB_APP_URL`, and `TURNSTILE_SECRET_KEY`. Google's matching `SHARED_SECRET` lives in Script properties. Do not rerun setup or create another Form for routine edits. Existing Google Form editor and responder access must remain Restricted to the owner; direct public responder access was explicitly removed and live intake retested successfully.

## Motion and the home marquee

- Smooth scrolling uses Lenis 1.3.27, self-hosted at `assets/vendor/lenis.min.js` (MIT licence beside it). `site.js` loads it only on fine pointers and never under reduced motion.
- Scroll reveals, line-split headings, image masks/parallax, the cursor label and the related-project thumbnail live at the end of `site.js` and in the Motion block of `site.css`. The hero reveal is CSS only. Content is hidden only by JavaScript, only below the fold, and everything is skipped under `prefers-reduced-motion`.
- The screenshot strip under the home hero is a trial: set `marquee.enabled` to `false` in `source/content.json` and rebuild to remove it. Thumbnails in `assets/thumbs/` are regenerated with `python tools/make_thumbs.py` (needs Pillow; the build itself does not).

## Later custom domain

Set the public build environment variable `ORVEN_SITE_URL` and the Worker's `SITE_URL` to the same HTTPS origin. `ORVEN_FORM_ENDPOINT` and `ORVEN_TURNSTILE_SITE_KEY` are also supported by the generator. Add the new hostname to the Turnstile widget before switching. Rebuild to regenerate canonical/hreflang/OG URLs, sitemap and robots, deploy, retest delivery, then redirect the old hostname deliberately. No final custom domain has been assumed or purchased.

## Retention operations

Use `RETENTION-RUNBOOK-AR.md`. The Form is the inquiry store; there is no separate leads database or automatically linked response Sheet. Script properties hold bounded operational references/status, not copies of names, contact values or project descriptions. Project records and documented legal holds are excluded from the inquiry deletion rule. Staff must record real WhatsApp/call contact and associate relevant email threads. Unregistered exports and provider backup histories cannot be automatically guaranteed deleted.

Do not run `liveSelfTest` casually: it creates and permanently deletes a synthetic inquiry and its notification. The owner explicitly approved and witnessed a successful launch test. `previewRetention` is the non-destructive operational review.

## Deployment record

25 October 2026: PR #1 merged into `main` as `a9ecd8224ca071a61ce9ca547508ddbe1722665e`, preserving all four feature commits and the pricing changes. Cloudflare automatically ran Git-connected Build `3b75f560-4cd4-4a78-8b52-42ed7d336e20` successfully, producing version `b25a6301-1d69-4e51-8d0b-7716b45a9604` at 100% traffic. The fully merged feature branch was removed; `main` is the only branch and PR #1 is merged/closed. This supersedes earlier draft/unmerged release-status statements in the historical funnel handoff. Earlier manual deployments remain historical records.

Before merge, all 16 localized pages and public assets matched the deployed feature source; the root route is intentionally handled by the language redirect. Rebuilding production reproduced the tracked pages. Validation passed 864 static checks, asset budgets, 43 Worker/retention tests, 36 responsive funnel views and 32 full-site browser views, with inquiry outcomes mocked locally.

25 October 2026: source `5db503a179045bcc317aaf5bd0a1c53384d7c30e` published directly to Worker `orven`, version `2164c6ff-5bc3-4438-81f1-7353a87ae327`. All 16 live localized pages and CSS/JS matched the published source; 32 live responsive browser views passed. See `SALES-FUNNEL-HANDOFF.md`. PR #1 remains separate from this direct deployment.

Worker `orven`, version `287cd801-20d4-414b-be9f-a2120b0fff52`, deployed 19 October 2026. Google web app version 1, description “ORVEN launch — verified save and 30-day retention.” Administrative deployment identifiers are in the private handoff report. No paid subscription was activated.

