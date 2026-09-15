---
name: reference-agency-policy-research
description: "How to research a state/provincial agency row for campground_policies.json — scrape ALL the agency's park pages, count the boilerplate, and treat brochures as stale"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 2d317fec-bbca-4cea-9cb6-b74f0d891a85
  modified: 2026-09-15T17:23:08.194Z
---

Method that worked for `state:WV` (2026-09-15) and should be the default for the 33
agency rows left. See [[project-campground-schema]] and doc §5.

**Read every park page, not one.** An agency's camping policy lives as boilerplate
repeated across its park pages, so the COUNT is the evidence: WV's two-night weekend
minimum appears verbatim on 19 of 23, the 14-night maximum on 19, and that is what makes
it an agency default rather than one park's rule. The same pass found the two exceptions
that a single page would have hidden (Lost River has no minimum at all; Camp Creek applies
it only Memorial Day→Labor Day) and proved a negative worth more than either: **not one
dollar figure appears on any of the 23 pages**, so "no rates published" is a measured
claim, not a failure to look.

**Mechanics.** `/sitemap_index.xml` → `page-sitemap.xml` → filter for the camping URLs;
`curl` with a browser `User-Agent` works where `urllib` gets 403 and where WebFetch can
only read one page at a time. Strip tags, collapse whitespace, then grep each page for the
candidate phrases and tally. ~25 pages costs a couple of minutes.

**The legislative rule beats the website** where one exists: WV's 58CSR32 is the authority
for the 14-night maximum and the quiet-hours/check-out terms, and it is where a residency
term turned up that no park page mentions. Scanned PDFs have no text layer — `pdftotext`
returns 3 bytes and there is no OCR on this box; read the pages with the Read tool.

**Brochures and campground-application PDFs still served from the agency's own domain are
the trap.** WV's describe held-back first-come sites and a "at least two (2) days prior to
arrival" cutoff, both from before the online system, and a search engine hands them back as
current. Date every source against the booking engine's actual behaviour.

**What an agency never publishes, leave absent.** WV keeps every rate and the booking
calendar inside its Inntopia engine; no horizon, no rate, no non-resident figure is on the
open web. Record the absence and what was checked in the row's `note` — see
[[feedback-absent-is-not-unknown]].
