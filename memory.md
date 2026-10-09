# Kiji Yuki — Website

**Status:** live
**Last updated:** 2026-10-09

## What this is

Static HTML/CSS site for the Gibbs family holiday home in Japan — Kiji Yuki,
3107-1 Hotaka, Kijimadaira, Shimotakai District, Nagano 389-2301.

Five pages: `index.html`, `about.html`, `house.html`, `guide.html`,
`availability.html`. Plus two Vercel serverless functions in `api/`.

## ⚠ Purpose and hard constraints — read before changing anything

**This is NOT a booking site and must not read like one.** It is purely an
informational site for friends and family who are thinking about using the
house.

**There is no minpaku licence** (Japan's private lodging / 民泊 registration),
so the property cannot be marketed or operated as paid accommodation.

These are all **deliberate** — do not "fix" them:

- **No contact details anywhere.** No email, no phone, no contact form.
  (Commit `ed46dba` removed the contact section on purpose.)
- **No pricing or rates.** Ever.
- **`robots.txt` is `Disallow: /`** and every page carries
  `<meta name="robots" content="noindex">`. The site is intentionally
  invisible to search engines. Do not propose SEO work, structured data,
  sitemaps, or un-noindexing it.
- The availability calendar sits behind a question gate for the same reason.

Copy should avoid commercial-accommodation vocabulary. Words like "booking",
"guests max", rates/fees, and Airbnb-style capacity stat bars cut against the
site's own stated purpose. (The word "booking" was removed site-wide on
2026-10-09 for this reason.)

Guest-facing practical detail (house guide, area guide) is welcome — the thing
to avoid is transactional framing, not hospitality information.

## Deployment

- **Domain:** kijiyuki.com, registered through Cloudflare
- **Host:** Vercel, auto-deploys from `main`
- **Repo:** https://github.com/MrGibbsTeach/kijiyuki
- **Local path:** `D:\Nextcloud\Clayton\Work\kijiyuki`
  (moved from OneDrive to Nextcloud; git works fine from here)

**The live site serves `www.kijiyuki.com`.** The apex `kijiyuki.com`
308-redirects to it. Note the `<link rel="canonical">` tags still point at the
apex (non-www) — harmless while the site is noindex, but it is a mismatch.

DNS (Cloudflare), both "DNS only", proxy disabled:
- `kijiyuki.com` → CNAME → `c5a34b0252de07ca.vercel-dns-017.com`
- `www.kijiyuki.com` → CNAME → same

Workflow: edit locally → commit → `git push origin main` → Vercel deploys in
seconds.

## The availability gate

`availability.html` asks "What is the surname of one of the owners?"
(answer: Gibbs). The answer is **not** published anywhere on the site.

- `api/verify.js` — checks the answer server-side against
  `AVAILABILITY_ANSWERS`, returns an HMAC-signed token valid 90 days
- `api/calendar-url.js` — verifies the token, then returns
  `CALENDAR_EMBED_URL`

Env vars live in Vercel project settings, never in the repo:
`AVAILABILITY_SECRET`, `AVAILABILITY_ANSWERS`, `CALENDAR_EMBED_URL`.

Implementation is sound (HMAC, `timingSafeEqual`, server-side check, no secret
reaches the client). Known soft spots, both accepted for now: **no rate
limiting** (rapid wrong guesses are not throttled beyond a 400 ms delay), and
the answer is guessable from the domain owner / GitHub account. Stakes are low
— a correct answer only reveals a calendar.

## CSS architecture

`assets/css/main.css` is the shared stylesheet: reset, CSS variables, nav,
hamburger, mobile menu, footer, scroll-reveal, skip-link, the `.icon` SVG
styles, and the shared page/section heading base (`.page-header`,
`.page-eyebrow`, `.page-title`, `.s-eyebrow`, `.s-title`, `.s-body`).

Each page then has its own `<style>` block for genuinely page-specific
components (index: hero/gallery/lightbox; guide: tabs/accordions/resort cards;
house: packing filter). **`main.css` loads before the inline block on every
page, so inline rules override the base** — that is how per-page title sizes
work. Keep it that way.

Most of the remaining ~52 KB of inline CSS is genuinely page-specific, not
duplication. Checked 2026-10-09: only the heading patterns actually repeated.

## ⚠ Known outstanding work

**1. Photos — the big one, deliberately deferred ("pinned") 2026-10-09.**
- `assets/img/` is **90 MB**. Individual house photos are 2.5–6.5 MB at
  4000–4624 px wide.
- The homepage alone references **76.8 MB** of images; **6.1 MB loads before
  first paint** (3.4 MB eager hero `exterior-winter.jpg` + a 2.7 MB CSS
  background `IMG20260122130312.jpg`, which cannot lazy-load). Roughly 10 s on
  real 4G.
- No `srcset`, no `<picture>`, no WebP, no `width`/`height` (so layout shifts),
  and no `vercel.json`, so Vercel image optimisation is off.
- Proven in testing: resizing to 2000 px + WebP gives **~94 % reduction
  (90 MB → ~5 MB) with no visible quality loss**.
- The opposite problem also exists: **12 area/resort images are under 900 px**
  (smallest 228×221) and look blurry. Their dimensions suggest they were taken
  from other sites — worth checking before anything is ever indexed.
- Clayton's own view: many of the photos "are not even good photos" and want
  replacing, not just compressing.

**2. `assets/iiyama_line_en.pdf` is 40 MB**, linked as a download from the area
guide. Same media-weight bucket as the photos.

**3. `assets/img/updated/front.png` is an unreferenced 11 MB PNG** committed to
the repo. Nothing links to it.

**4. House WiFi** — "coming soon, get an eSIM" is the current message on
`about.html` and `house.html`, and Clayton confirmed it should stay that way
for now.

**5. `.vehicle-points`** on index.html is a wrapper div with no CSS. Harmless,
pre-existing.

The `.git` directory is ~130 MB because the large media is in history.

## Content decisions already settled

- **"Iiyama Line"** — capital I, capital L. Decision made 2026-10-09; it is a
  proper noun (飯山線). Was lowercase "iiyama Line" in 19 places including two
  meta descriptions. **Image filenames stay lowercase/hyphenated**
  (`iiyama-line-1.jpg`, `iiyama_line_en.pdf`) — do not rename those.
- **Bed count** — the house sleeps **14**: two queens, two singles, two bunks
  across four bedrooms, plus four futons for any tatami room. An earlier
  "10 Beds + 4 futons" stat was wrong (it double-counted to reach 14) and has
  been removed. Do not reintroduce a bed *count* in the stat bar; the bedroom
  cards plus the summary line carry the detail.
- **Nav** is identical on all five pages: The House · Area Guide · Location ·
  About · Availability · [House Guide button]. The current page gets
  `href="#" class="nav-link active" aria-current="page"`; "House Guide" is
  always the terminal `.btn-nav` / `.menu-cta`.
- **Icons** are thin-line inline SVGs with `class="icon"`, stroked in
  `currentColor` and sized in `em`. Colour emoji were removed 2026-10-09
  because they clashed with the restrained Shippori Mincho / Jost typography.
  Typographic marks (★ ✓ ✦ ⚠ ✕) are intentional and were kept.
- Tone: no AI speech patterns, no em-dash tics, no corporate language. This
  has been cleaned up repeatedly (commits `2646d99`, `b7361e8`) — keep it
  plain and human.
- **`house.html` arrival section is "Arrival & settling in"**, not
  "check-in" (changed 2026-10-09, including both meta descriptions).
  Check-in language reads transactional.
- **"A day at the house"** narrative was **removed** from `house.html` on
  2026-10-09 (it was added in `d639d16`). Do not reintroduce it.
- **No claims about village mobile coverage.** The "Mobile coverage in the
  village is fine" line was removed 2026-10-09 — it could not be stood behind.
- **Trains:** do not say you can take the Iiyama Line one more stop to
  Kijimadaira station. That was incorrect and was removed from `house.html`
  on 2026-10-09. Shinkansen to Iiyama, then bus or taxi.
- **Big shop is TSURUYA Iiyama**, next to the shinkansen station — not the
  local <span lang="ja">イーストア滝沢商店</span>.
- **Heating:** reverse cycle aircon is being installed **end of 2026**;
  kerosene is described as *additional* winter heating.
- **Apostrophes are straight** (`'`) throughout every page — no `&rsquo;`,
  no curly quotes.

### The Iiyama Line — verified 2026-10-09

The train tab on `guide.html` was wrong and has been corrected. The facts:

- The JR Iiyama Line (飯山線) runs **Toyono → Echigo-Kawaguchi**, 31 stations,
  96.7 km. Most trains run through to/from **Nagano**.
- **There is no station in Kijimadaira.** The nearest is **Iiyama**
  (Hokuriku Shinkansen + Iiyama Line), ~15 min by taxi or bus to the house.
- **Only the Hakutaka** Hokuriku Shinkansen service stops at Iiyama
  (not Kagayaki, not Asama). Tokyo → Iiyama is about 1 hr 45 min, direct —
  **not** via Nagano.
- **Yudanaka and Shinshu-Nakano are on the Nagano Electric Railway**
  (Nagaden), not the Iiyama Line. Snow monkeys by train = Iiyama Line to
  Nagano, Nagaden to Yudanaka, short bus. Driving is quicker (~35 min).
- **Tokamachi** connects to the **Hokuhoku Line**, not the Joetsu Line.
  **Echigo-Kawaguchi** is the Joetsu Line connection.

### Area guide (`guide.html`)

- **Overview tiles run non-winter first** (2026-10-09): Green Season,
  Cherry Blossoms, Onsens, Snow Monkeys, Eating & Drinking, Iiyama Line,
  Ski Resorts. Ski resorts deliberately last. **Note the tab bar still runs
  in a different order** (Onsens, Snow Monkeys, Green Season, Ski Resorts,
  Eating, Iiyama Line, Blossoms) — not yet aligned.
- **Bike hire** options listed in the Green Season tab: Shinetsu Shizenkyo
  Activity Center at Iiyama station (widest range), Michi-no-Eki FARMUS
  Kijimadaira (e-bikes, closest), Compass House (high-end Specialized,
  e-bikes Apr–Nov / MTB Jul–Oct).
- **Tsudoy sits above the food cards**, not inside the grid — Clayton wants
  the bar next door given top billing.
- **Bakery Hoshino** (ベーカリーホシノ, 3005-1 Hotaka,
  https://www.bakery-hoshino.com/) is the first entry under cafes and
  bakeries. **100 m from the house** and, per Clayton, the best thing in the
  village. Open 9:00–16:30, closed Mondays, sells out.
- Onsens are described as ranging from quiet local baths to the bathhouses of
  **Nozawa Onsen and Shibu Onsen**.

## Related

- Property is tracked financially in Gibbs Dashboard (Japan property tab,
  Japan IO loan via Buxfer xxxx1687, Japan offset xxxx1463)
- Connected to the kijiyuki project in Claude's project index (HUB.md)
