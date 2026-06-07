export const meta = {
  name: 'reservation-link-finder',
  description: 'Find missing reservation/official websites (or confirm FCFS) for 127 campgrounds, with adversarial URL verification',
  phases: [
    { title: 'Research', detail: 'one agent per campground: find booking model + canonical URLs' },
    { title: 'Verify', detail: 'adversarially re-fetch and confirm each proposed URL resolves to THIS campground' },
  ],
}

let items = args // compact [{id, batch, name}]
if (typeof items === 'string') items = JSON.parse(items)
if (!Array.isArray(items)) throw new Error('args did not resolve to an array; got ' + typeof items)

const RESEARCH_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['id', 'booking_model', 'reservation_url', 'official_url', 'source_urls', 'evidence', 'confidence', 'flags'],
  properties: {
    id: { type: 'number' },
    booking_model: { type: 'string', enum: ['reservable_online', 'fcfs', 'reservable_phone_only', 'closed_or_defunct', 'unconfirmed'] },
    reservation_url: { type: 'string', description: 'Deep online booking link actually loaded (recreation.gov/camping/campgrounds/<id>, ReserveAmerica deep link, state portal #!park/<id>, Campspot, or operator booking page). Empty string if none.' },
    official_url: { type: 'string', description: "Operator/agency official page actually loaded. Empty string if none." },
    source_urls: { type: 'array', items: { type: 'string' }, description: 'URLs you actually fetched as evidence' },
    evidence: { type: 'string', description: 'Concise justification, quoting what the pages showed (name/town/county match, fee, reservation system)' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    flags: { type: 'string', description: 'Inclusion-criteria concerns (membership/club park, not RV-suitable, defunct/dead site, seasonal-event-only, workforce/residential) or empty string' },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['id', 'verdict', 'final_booking_model', 'website_value', 'note_addition', 'url_resolves', 'flags', 'reason'],
  properties: {
    id: { type: 'number' },
    verdict: { type: 'string', enum: ['confirm', 'amend', 'reject'] },
    final_booking_model: { type: 'string', enum: ['reservable_online', 'fcfs', 'reservable_phone_only', 'closed_or_defunct', 'unconfirmed'] },
    website_value: { type: 'string', description: 'EXACT final value for the campgrounds.json website field: official + reservation URLs you personally re-fetched and confirmed resolve to THIS campground, newline-separated, deduped by domain, deep links preferred. Empty string if nothing could be confirmed.' },
    note_addition: { type: 'string', description: 'Prose to APPEND to the existing note ONLY for a negative reservation fact ("FCFS - not on recreation.gov", "book via Campspot, not recreation.gov") or a dead/suspect official-domain caveat. URLs never go here. Empty string for no note change.' },
    url_resolves: { type: 'boolean', description: 'Did you personally fetch the URLs and confirm they load and name this campground?' },
    flags: { type: 'string', description: 'Confirmed inclusion-criteria concern worth surfacing to the human, or empty string' },
    reason: { type: 'string', description: 'What you re-checked and why you confirmed/amended/rejected' },
  },
}

const RULES = `
PROJECT URL CONVENTIONS (campgrounds.json):
- URLs belong in the "website" field, NOT in note prose. Newline-separated if several, deduped by domain.
- Prefer deep, campground-specific links AND ideally carry BOTH the official park page AND a direct reservation link.
  - recreation.gov -> https://www.recreation.gov/camping/campgrounds/<id>
  - ReserveAmerica -> .../campgroundDetails.do?contractCode=XX&parkId=<id> (or an /explore/.../campsite-booking deep link)
  - US eDirect state portals -> <frontend>/#!park/<PlaceId>
  - private parks -> operator's own domain; include their online booking page (Campspot/their site) if one exists
- Two things stay as note PROSE, never as a URL: a NEGATIVE reservation fact ("FCFS - not on recreation.gov"; "book via Campspot, not recreation.gov") and a dead/suspect official domain recorded as a caveat.
- NEVER fabricate a URL or a recreation.gov/parkId number. Only report a link you actually loaded and that shows THIS campground's name + town/county.
- Many USFS/USACE/federal river sites are free + FCFS by default; assume FCFS unless a real booking channel exists.
`

function researchPrompt(item) {
  return `You are researching ONE campground to find its real booking model and canonical website/reservation URLs. It currently has NO website recorded (or only an info page) and we want to fill that gap.

First, load its full record:
  python3 -c "import json;print(json.dumps([x for x in json.load(open('/tmp/wf_targets.json')) if x['id']==${item.id}][0],indent=2))"

That gives you name, state, ownership, coordinates (lat,lng), phone, and the existing note. The coordinates are authoritative — use them to disambiguate similarly-named places.

Your job:
1. Use web search + fetching real pages to determine the BOOKING MODEL:
   - reservable_online: there is an online booking system (recreation.gov, ReserveAmerica, a state reservation portal, Campspot, or the operator's own booking page).
   - fcfs: first-come, first-served, no online/phone reservations.
   - reservable_phone_only: reservations exist but only by phone (no online system); record the phone if found.
   - closed_or_defunct: appears permanently closed / no longer operating.
   - unconfirmed: you genuinely cannot tell.
2. Find the OFFICIAL operator/agency page (official_url) AND the deep online RESERVATION link (reservation_url) when one exists. Actually LOAD each page and confirm it names this campground + matches the town/county/coords.
3. For public FCFS sites: verify FCFS by checking that recreation.gov does NOT have a bookable campground page for it. If recreation.gov DOES list it as bookable, it is reservable_online — return that /camping/campgrounds/<id> link.
4. For state parks (VT, GA, etc.) and county/regional parks: find the official reservation portal and the specific park's deep link.
5. For private parks: find the operator's own domain; include their online booking page if any. If the only "site" is a dead placeholder, note that and treat booking as phone-only or unconfirmed.
6. Flag any inclusion-criteria concern you stumble on (membership/club park, not RV-suitable / sites too small, defunct, seasonal-event-only, workforce/residential).

${RULES}

Return the structured result for id ${item.id} (${item.name}). Put every page you fetched in source_urls. Be honest: empty strings + low confidence beat a guess.`
}

function verifyPrompt(item, research) {
  return `You are an ADVERSARIAL verifier. A researcher proposed booking info for ONE campground. Your default stance is skepticism: try to REFUTE every URL and the booking model before accepting it.

Campground id ${item.id} (${item.name}). Load its authoritative record (name, coords, town/county, ownership, existing note) first:
  python3 -c "import json;print(json.dumps([x for x in json.load(open('/tmp/wf_targets.json')) if x['id']==${item.id}][0],indent=2))"

Researcher's finding (JSON):
${JSON.stringify(research)}

Do this:
1. PERSONALLY fetch the proposed reservation_url and official_url. For EACH: confirm it (a) actually loads / is a real live page, and (b) names THIS campground and matches its town/county/coordinates — not a different or similarly-named place. If a URL 404s, redirects to a generic homepage, or names a different campground, REJECT that URL.
2. Independently sanity-check the booking_model. If the researcher said FCFS, do a quick check that there is no recreation.gov/ReserveAmerica booking page; if they said reservable_online, confirm the booking system really covers this campground.
3. Decide the FINAL website_value: only URLs you personally confirmed resolve to this campground, official + reservation, newline-separated, deduped by domain, deep links preferred. If you confirmed nothing, return an empty string (do NOT pass through unverified links).
4. note_addition: only for a negative reservation fact ("FCFS - not on recreation.gov", "book via Campspot, not recreation.gov") or a dead/suspect-domain caveat. Otherwise empty. URLs never go in note_addition.
5. verdict: confirm (researcher right), amend (corrected URLs/model), or reject (nothing usable confirmed).
6. Carry forward any real inclusion-criteria concern in flags.

${RULES}

Set url_resolves true only if you actually fetched and confirmed the URLs in website_value. Return the structured verdict for id ${item.id}.`
}

log(`Starting reservation-link research for ${items.length} campgrounds`)

const results = await pipeline(
  items,
  (item) => agent(researchPrompt(item), { label: `research:${item.id} ${item.name}`.slice(0, 60), phase: 'Research', schema: RESEARCH_SCHEMA, agentType: 'general-purpose' })
    .then((r) => ({ ...r, _item: item })),
  (research, item) => agent(verifyPrompt(item, research), { label: `verify:${item.id} ${item.name}`.slice(0, 60), phase: 'Verify', schema: VERDICT_SCHEMA, agentType: 'general-purpose' })
    .then((v) => ({ ...v, batch: item.batch, name: item.name, research })),
)

const out = results.filter(Boolean)
log(`Done: ${out.length}/${items.length} campgrounds processed`)
return out
