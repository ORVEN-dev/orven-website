# ORVEN delivery guarantee and sales funnel update

Implemented 24 October 2026 against main `470a806eac4e386df5402857d0f57c589925d23a`.

## Production deployment — 25 October 2026

The owner explicitly requested Cloudflare publication after approving the restored headlines. Published source commit `5db503a179045bcc317aaf5bd0a1c53384d7c30e` directly using the existing Wrangler configuration and account. Cloudflare reports Worker `orven` version `2164c6ff-5bc3-4438-81f1-7353a87ae327` deployed to `https://orven.orven-agency01.workers.dev`. The preceding production version is `8ad0158a-ae29-435d-9e5a-cba189c63147`.

Before deployment, the production build, 864 static checks, asset budgets and all 43 Worker/retention tests passed. After deployment, direct live GETs of all 16 localized pages plus `site.js` and `site.css` matched the local published files byte-for-byte. Live browser verification passed 32 page views across both languages at 390 and 1440 pixels, checking HTTP 200, headings, direction, overflow, exact English offer/name, localized guarantee links and terms opening. Screenshots were inspected. No inquiry or other production POST was sent.

Deployment used the existing Worker, asset and rate-limit bindings. No authentication, secrets, Google integration or retention settings were edited. This deployment does not merge PR #1 into main. Earlier statements below that the work was not deployed describe the previous review stages and are superseded by this verified production record. Legal review remains a recommendation; no legal certification is claimed.

## Current copy revision — 25 October 2026

At the owner's request, the existing English and Arabic headlines and subheadlines have been restored verbatim from `470a806`. This includes the original Home and Services hero titles/intros, Home approach intro and benefit-card headings, and Contact intro/closing headline and subheadline. Home again reads `Digital experiences. Built around your business.` and Services reads `Different businesses. Different needs.` with their original authored line breaks. Only eleven bilingual heading/intro fields changed from the approved-offer revision.

The exact approved offer, guarantee name, qualifications, full terms, placements, links, styling, Pricing, optional Hosting, FAQ, descriptive card/process copy and conversion hooks remain unchanged. The earlier implementation notes below describe the history; their references to rewritten hero/intro copy are superseded by this restoration. Campaign messaging should match the restored agency headline plus the exact approved offer and guarantee. This revision passed the production build, 864 static checks, asset budgets and the 36-view bilingual responsive funnel regression, including the exact offer text and terms interactions. It remains in the same draft PR and has not been deployed.

## Approved offer wording update

Continues the existing Pricing and sales-funnel work in PR #1 on `codex/delivery-guarantee-funnel`, based on `114ee611b1efa83812c3fcdc6fc2dd97def24ded`. Both prior chats were idle and the remote branch matched that commit when work began. No duplicate PR or pricing section was created.

Every English delivery notice now places **ORVEN 100% Delivery Guarantee** immediately above **Your Website. As Agreed. On Time. Or Your Money Back.** The offer portion is exactly `Your Website. As Agreed. On Time.` and the assurance portion is exactly `Or Your Money Back.` The latter uses the existing bronze color, with readable contrast on dark and light sections. Both portions form one paragraph with the approved punctuation and spacing. The shared generator also supplies the same wording below the guarantee name in the full terms. Arabic has a localized equivalent with the existing RTL typography.

Placement follows the existing decision points: three notices on Home (hero, Pricing and final CTA), four on Services (hero, website service, web-app service and final CTA), one beside the Contact form, and the existing closing CTAs on About, Work and both case studies. No sticky notice or extra section was introduced. Each notice retains the contractual qualification and localized terms link; the refund is for paid development fees under the stated breach/cure conditions, not an unconditional refund of external costs or a guarantee of commercial results.

The attached original PDF was recovered from the referenced conversation, confirmed to have 16 pages, and pages 8–14 were checked against the earlier extraction and rendered pages. The existing implementation of customer-focused hero copy, benefits, authentic feedback, FAQ and local conversion hooks is retained. Trust-campaign creative should use the exact approved offer and corresponding qualification, matching localized Home and its terms route.

Latest validation: production build; 864 static checks; asset budgets; 43 Worker/retention tests; 32 existing browser page views; 36 funnel views across 320/390/768/908/1024/1440 widths in both languages. Exact offer text, name order, notice count, absence of fixed positioning, clipping, CTA adjacency, terms opening/reopening, keyboard and no-JavaScript access were checked. Three inquiry outcomes were mocked locally; no production inquiry was sent. Pricing, optional Hosting, original reviews, project records, source section order, assets, design tokens and deployment configuration compare unchanged against the prior PR. Previous Lighthouse numbers below belong to the earlier revision and were not rerun for this wording update.

**Release status:** this update is prepared for review in the same draft PR, not merged or deployed. A direct live English GET returned HTTP 200 but did not contain the guarantee name or approved offer when checked. GitHub updates do not establish Cloudflare deployment. Obtain legal review of the bilingual guarantee and project contract **before advertising or publishing the guarantee**, including the contractual cure period and refund process; no new dates, notice periods or refund deadlines have been invented.

## Result

The Home and Services opening copy now addresses customer uncertainty and explains the value of clear websites and practical web apps. The primary action remains Start a Project, with the existing real work as supporting evidence. The existing multipage navigation, section order, dark/bronze identity, local fonts, portfolio, authentic Arabic feedback and labelled translations are retained.

The approved ORVEN 100% Delivery Guarantee appears beside primary conversion actions on Home, Services, Contact and the closing sections of About, Work and both case studies. Every notice states the qualifying ORVEN-attributable breach, agreed specifications or contractual deadline, contractual cure period, and refund of development fees paid. All notices use a single bilingual source object. Complete terms are available at `/en/services/#delivery-guarantee` and `/ar/services/#delivery-guarantee`, inside the existing support section. Direct links open the disclosure; repeated links reopen it after manual closure. The full text is available without JavaScript.

The terms separate development fees from external expenses and explain the 30 days of free correction of covered implementation defects. Changes outside scope and continuing maintenance have separate fees. No revenue, sales or lead guarantee is offered. No scarcity, notifications about purchases, invented proof, intrusive upsell or extra tracking provider was added.

Process, FAQ and Contact copy now explain written scope, delivery expectations, internal review and the detailed final quotation after discovery. The approved Pricing object is unchanged: EGP 8,000 / 16,000 / 35,000 starting prices, without a maximum. The approved Hosting card is unchanged: project-dependent, included in the final quotation only when requested; otherwise no hosting fee.

## Source and PDF review

The actual 16-page `How to Build A Salesman.pdf` was located in the owner's downloaded course files because the supplied `/mnt/data/` path does not exist on this Windows host. All pages were text-extracted and rendered for review. No copyrighted PDF or course imagery is added to the public repository.

Applied the PDF's principles to the existing agency site: pages 2–3 message continuity and one primary conversion goal; 8–10 customer-focused opening and clear CTA; 11 conditional assurance near CTAs; 12 customer benefits and practical differences; 13 existing genuine feedback plus FAQ; 14 moderate repeated CTAs and conversion integration points. Pages 4–7 inform the choice of a service-site journey rather than an ecommerce checkout; pages 15–16 are not used to introduce scarcity, purchase notifications or upselling.

## Campaign continuity and measurement

The trust campaign should land on the top of the localized Home page: `/ar/` for Arabic creative, `/en/` for English. Its message should match the confidence/clarity headline and the conditional delivery guarantee. Website and web-app service ads can link to `/ar/services/#websites`, `/ar/services/#applications`, and their English equivalents. Do not link trust-focused creative straight to a quote form without its explanation and guarantee.

`site.js` dispatches a local `orven:conversion` document event with exactly `event`, `action`, `section`, `page`, `language` and `version`. The current version is `trust-v1`, set by the generator. Actions distinguish Start a Project, WhatsApp, arranged calls, direct telephone calls, email and guarantee terms. `inquiry_success` fires only after the existing frontend validates a positive matching inquiry receipt; clicks are not treated as submitted inquiries.

The hook sends no network requests, saves nothing, reads no campaign parameters and includes no visitor identifiers, names, contact details or project text. It is an integration point, not a deployed analytics system or a claim that conversion is currently being measured. The existing `analytics: false` setting, consent gate and privacy text remain unchanged.

For a later approved experiment, compare a clearly named copy revision against `trust-v1` while holding the audience, ad message, offer, budget and measurement window consistent. Decide the primary outcome in advance: confirmed inquiries, with CTA clicks as secondary indicators. Review consent/privacy and implement an approved collector before reporting rates or running statistical tests. No random variant selection or storage was silently activated.

## Verification performed

- Existing production build: 16 localized pages, 27 core sections and 14 case-study sections; passed.
- Existing static checks: 864 passed, zero failed, including local routes, anchor targets and page metadata.
- Existing Worker and retention suite: 43 passed, zero failed, using mocked providers.
- Existing browser regression: 32 page views, all localized pages at 390 and 1440 CSS pixels; no overflow or page errors; images decoded; menu/Escape, FAQ, original-image lightbox, and empty-form validation passed.
- Added funnel browser checks: 30 views of Home, Services and Contact, both languages, at 390 / 768 / 908 / 1024 / 1440 CSS pixels. No clipped hero or guarantee text, no page overflow, no JavaScript errors. Verified adjacent notices, terms links, keyboard disclosure, reopening the same fragment, no-JavaScript access and localized project CTA.
- Inquiry event checks: three fully mocked responses (failure, mismatched receipt, confirmed receipt). Only the confirmed receipt emitted success. No production inquiry was submitted. Verified the event payload excludes test contact information and URL campaign parameters.
- Visually inspected both desktop and mobile Home renders. The existing section order, Pricing content, Hosting card, authentic reviews and project records compare equal to the baseline. Tokens, fonts, images, case-study content, privacy sources, public contacts, Worker, Google integration and deployment configuration are unchanged.
- Existing asset budget and six contrast pairs passed. Maximum static full-scroll page budget is 1,969,524 bytes; this is a file-size budget, not measured production bandwidth.
- One local Lighthouse mobile simulation per Home language: EN 91, AR 97; LCP approximately 2.55s / 2.25s; CLS 0 for both. Local runs are variable and do not establish production Core Web Vitals or improvement against a baseline. Reports are retained in the task's work files.

Run the new browser check with Playwright installed and a preview server on port 8774: `node tests/funnel-browser.cjs`. Set `TEST_ORIGIN` for another local origin. Existing checks remain documented in README.

## Contract review and release status

The website implements the owner's approved conditional offer. This is not legal certification. Before using it in a signed customer contract, obtain Egyptian legal review of the bilingual terms, legal contracting identity, precise deliverables and acceptance criteria, deadline and client dependencies, breach notice, contractual cure period, refund procedure/timing, external-cost breakdown and applicable mandatory rights. No numerical cure period, refund deadline or new waiver has been invented. The 30-day defect-correction period is separate from the contractual cure period and does not replace it.

Implementation and generated production files are prepared on `codex/delivery-guarantee-funnel` for review. No Cloudflare deployment was performed for this update. A GitHub push or merge is not proof of deployment. After code review and the owner's release decision, use the repository's production build/check/deploy workflow and verify the new English and Arabic copy directly on the live URLs. Preserve existing secrets, Google access and retention settings; no live intake test is required for these copy changes.
