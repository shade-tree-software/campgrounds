#!/usr/bin/env python3
"""Fill `discounts.good_sam` (and `discounts.military`) from the Good Sam directory.

docs/campground-schema.md §7 phase 5, §4.4. Good Sam's campground directory is a
Next.js app whose listings are JS-rendered, but the data behind it sits in an
Algolia index (see the Good Sam ratings reference for how the key is obtained:
a 2-hour secured key from an AppSync query, no account needed).

**`isGsPark` is the flag, and "presence in the index" is NOT.** §4.4 guessed that
membership in the index effectively IS the Good Sam network flag. Measured
2026-09-20, it is not close: the index holds 24,462 asset rows covering the whole
directory — national forests, state parks, county parks, anything the guide
lists — and only 3,578 of those rows carry `campground.isGsPark`. A Good Sam Park
is the network designation, and Good Sam's own directory states the promise it
makes: "Every Good Sam Park offers a 10% discount to the more than 2-million Good
Sam members." That sentence is the reason this maps onto a `discounts` field at
all; being *rated* by a Good Sam inspector (a three-number facility/restroom/
appeal score, which most listed parks carry) promises nothing and is not read here.

**A no is recorded, an absence is not.** A park the directory lists with
`isGsPark: false` is a measured no — the directory knows the park and does not
designate it — so it writes `good_sam: false`. A park the directory does not list
at all writes NOTHING: absence from an index is not evidence of refusal (§2.1),
and the directory is a US/Canada RV-park guide that was never trying to be a
census of the 12,774 entries here. That is the same distinction `recgov_hookups`
draws between "every RV site is typed NONELECTRIC" and "no site says".

**`military` is true-only.** `paymentInfo.discounts` carries `militarydiscnt` on
about 40% of listings and has no Good Sam entry at all (the network flag lives
in `isGsPark`), so the list is read as a positive claim only: present -> true,
absent -> unknown. Unlike `isGsPark` there is no directory-wide designation whose
absence means anything — a park that gives a military discount and never told
Good Sam looks identical to one that doesn't.

Two steps, like `recgov_hookups`: `--fetch` caches the directory to the gitignored
`trip_data/goodsam_parks.json`, and every later run matches and derives from that
cache for free. Dry-run by default; `--apply` writes.
"""

import argparse
import difflib
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import campground_schema as cs

CAMPGROUNDS_JSON = "campgrounds.json"
CACHE_JSON = os.path.join("trip_data", "goodsam_parks.json")

APPSYNC = "https://llx3tsxl2jaarct3rynyyaci3e.appsync-api.us-east-1.amazonaws.com/graphql"
APPSYNC_KEY = "da2-oeeljcqa6rcljmmook5my3iuv4"
APP_ID = "VT01MNVCP5"
INDEX = "gs-ml-cb-assets-prod"

# Algolia serves at most 1,000 records per filtered query and offset paging
# cannot reach past that, so a bucket bigger than this is split on the next
# axis rather than silently truncated — TX alone is 2,936 rows. The axes are
# tried in order and every one of them is a facet on this index.
PAGE_LIMIT = 1000
SPLIT_AXES = ("campground.type", "type", "campground.address.city")
HITS_PER_PAGE = 1000
PAUSE_S = 0.3

# The index is per ASSET (a site type within a park: back-in, pull-through,
# cabin), so one campground appears several times. Everything read here is a
# property of the CAMPGROUND, so rows collapse by `campground.id`.
CACHE_VERSION = 1


def _post(url, body, headers, timeout=60):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    for key, value in headers.items():
        req.add_header(key, value)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def search_key():
    """A 2-hour secured Algolia key, minted by an AppSync query.

    The index's search key is deliberately not static. `userToken` is only a
    rate-limit bucket, so any UUID does.
    """
    query = {"query": "query($t:String!){getCampgroundSearchAuthSecret(userToken:$t)"
                      "{secret expiresIn}}",
             "variables": {"t": str(uuid.uuid4())}}
    data = _post(APPSYNC, query,
                 {"x-api-key": APPSYNC_KEY, "Content-Type": "application/json"})
    return data["data"]["getCampgroundSearchAuthSecret"]["secret"]


class Algolia:
    """Thin search client that re-mints its key when the 2-hour one expires."""

    def __init__(self):
        self.url = f"https://{APP_ID.lower()}-dsn.algolia.net/1/indexes/{INDEX}/query"
        self.key = search_key()

    def _headers(self):
        return {"X-Algolia-API-Key": self.key,
                "X-Algolia-Application-Id": APP_ID,
                "Content-Type": "application/json"}

    def query(self, params):
        time.sleep(PAUSE_S)
        try:
            return _post(self.url, {"params": params}, self._headers())
        except urllib.error.HTTPError as exc:
            if exc.code not in (401, 403):
                raise
            self.key = search_key()
            return _post(self.url, {"params": params}, self._headers())

    def count(self, filters):
        return self.query(f"hitsPerPage=0&filters={urllib.parse.quote(filters)}")["nbHits"]

    def facet(self, name, filters=None):
        params = ["hitsPerPage=0", "maxValuesPerFacet=1000",
                  "facets=" + urllib.parse.quote(json.dumps([name]))]
        if filters:
            params.append("filters=" + urllib.parse.quote(filters))
        data = self.query("&".join(params))
        return (data.get("facets") or {}).get(name, {})

    def hits(self, filters):
        """Every hit for a filter that is known to fit under the page limit."""
        out, page = [], 0
        while True:
            data = self.query(f"hitsPerPage={HITS_PER_PAGE}&page={page}"
                              f"&filters={urllib.parse.quote(filters)}")
            out.extend(data["hits"])
            page += 1
            if page >= data.get("nbPages", 1):
                return out


def _quote(value):
    return '"' + str(value).replace('"', '\\"') + '"'


def walk(client, filters, count, axes=SPLIT_AXES):
    """Every hit for `filters`, splitting on the next axis when it is too big.

    Algolia will not page past 1,000 records, so a state over that is read as
    several disjoint queries instead. Splitting is the whole reason TX, CA and
    FL are not quietly short.
    """
    if count <= PAGE_LIMIT:
        return client.hits(filters)
    if not axes:
        raise RuntimeError(f"cannot split further: {filters} has {count} rows")
    axis, rest = axes[0], axes[1:]
    buckets = client.facet(axis, filters)
    if not buckets:
        return walk(client, filters, count, rest)
    out = []
    for value, sub_count in sorted(buckets.items(), key=lambda kv: -kv[1]):
        out.extend(walk(client, f"{filters} AND {axis}:{_quote(value)}", sub_count, rest))
    covered = sum(buckets.values())
    if covered < count:
        # A facet that does not cover every row (a record missing the field)
        # would silently drop the remainder, so ask for exactly those.
        missing = " AND ".join(f"NOT {axis}:{_quote(v)}" for v in buckets)
        out.extend(walk(client, f"{filters} AND ({missing})", count - covered, rest))
    return out


def compact(hit):
    """One campground, reduced to what a match and a discount need."""
    cg = hit.get("campground") or {}
    addr = cg.get("address") or {}
    geo = addr.get("geoLocation") or {}
    discounts = [d.get("id") for d in ((cg.get("paymentInfo") or {}).get("discounts") or [])
                 if isinstance(d, dict)]
    return {
        "id": cg.get("id"),
        "name": cg.get("name") or hit.get("name"),
        "city": addr.get("city"),
        "state": addr.get("stateCode"),
        "country": addr.get("countryCode"),
        "lat": geo.get("lat"),
        "lng": geo.get("lng"),
        "gs": bool(cg.get("isGsPark")),
        "military": "militarydiscnt" in discounts,
        "type": cg.get("type"),
        # Kept for auditing a surprising match by hand, not read by the derive.
        "advertiser": cg.get("onlineAdvertiser"),
        "phone": (cg.get("phone") or {}).get("number") if isinstance(cg.get("phone"), dict)
                 else cg.get("phone"),
    }


def load_cache():
    try:
        with open(CACHE_JSON, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return {}
    if data.get("version") != CACHE_VERSION:
        return {}
    return data.get("parks") or {}


def save_cache(parks):
    os.makedirs(os.path.dirname(CACHE_JSON), exist_ok=True)
    tmp = CACHE_JSON + ".tmp"
    payload = {"version": CACHE_VERSION, "fetched": time.strftime("%Y-%m-%d"),
               "parks": parks}
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, CACHE_JSON)


def run_fetch(only_states=None):
    """Walk the directory state by state into the cache, saving as it goes."""
    client = Algolia()
    states = client.facet("campground.address.stateCode")
    if only_states:
        states = {k: v for k, v in states.items() if k in set(only_states)}
    parks = load_cache()
    total = sum(states.values())
    print(f"{len(states)} states/provinces, {total} asset rows to read")
    done = 0
    for state, count in sorted(states.items(), key=lambda kv: kv[0]):
        hits = walk(client, f"campground.address.stateCode:{_quote(state)}", count)
        added = 0
        for hit in hits:
            row = compact(hit)
            if row["id"] is None:
                continue
            if row["id"] not in parks:
                added += 1
            # A later row for the same campground carries the same campground
            # block; keep the first and let a True win on either flag.
            held = parks.get(row["id"])
            if held:
                row["gs"] = held["gs"] or row["gs"]
                row["military"] = held["military"] or row["military"]
            parks[row["id"]] = row
        save_cache(parks)
        done += count
        print(f"  {state:>3}  {len(hits):>5} rows  +{added:<5} parks "
              f"({done}/{total})")
    print(f"cached {len(parks)} campgrounds")


# ── Matching ────────────────────────────────────────────────────────────────

# Words that say nothing about WHICH campground this is. Dropped before the
# names are compared so "Shoshone RV Park" and "Shoshone Campground" agree.
STOP = {"campground", "campgrounds", "rv", "park", "parks", "resort", "resorts",
        "camp", "camps", "camping", "the", "of", "at", "a", "and", "sites",
        "site", "llc", "inc", "area", "coe", "cg", "recreation", "rec",
        "company", "on", "in", "de", "du", "la", "le", "les"}

# Words that DISTINGUISH two campgrounds sharing a stem — Silver Lake East and
# Silver Lake West are 400 m apart and are not each other. A name carrying one
# of these where the other does not is vetoed however well the stems match.
MODIFIERS = {"east", "west", "north", "south", "upper", "lower", "little",
             "big", "old", "new", "i", "ii", "iii", "1", "2", "3", "a", "b", "c"}

# (metres, minimum similarity, whole-name match required). The bands trade
# naming variation against distance: the Good Sam pin is geocoded from a mailing
# address and this database pins the campground itself, so a real pair can sit a
# kilometre or two apart — but at that range only a whole-name match is trusted.
BANDS = ((3000, 0.90, True), (800, 0.75, False), (250, 0.62, False))
SEARCH_M = 3000
RIVAL_MARGIN = 0.12
GRID_DEG = 0.05


def _strip_accents(text):
    return "".join(c for c in unicodedata.normalize("NFKD", text)
                   if not unicodedata.combining(c))


def variants(name):
    """The strings a name might reasonably be matched on.

    Good Sam writes a public campground as `Parent/Child` (`Uinta-Wasatch-Cache/
    Sunrise`, `Lake Roosevelt NRA/Keller Ferry Campground`) where this database
    writes `Sunrise Campground (Bear Lake)`. So each side offers its whole name,
    each slash segment, and each of those with a parenthetical dropped or
    promoted — 68 matches in the first run come from a parenthetical alone.
    """
    text = _strip_accents(name or "").lower().replace("&", " and ")
    out = {text}
    out.update(part.strip() for part in text.split("/"))
    for part in list(out):
        out.add(re.sub(r"\([^)]*\)", " ", part).strip())
        out.update(inner.strip() for inner in re.findall(r"\(([^)]*)\)", part))
    return {v for v in out if v}


def _tokens(text):
    words = [w for w in re.sub(r"[^a-z0-9 ]+", " ", text).split() if w]
    core = [w for w in words if w not in STOP]
    return core or words


def pair_score(a, b):
    """(similarity, whole) for one pair of name variants.

    `whole` is the guard against a SUBSET. `Camp Eagle Nest` scores 1.0 against
    `Eagle Nest Lake State Park` — its tokens are contained in the other's — and
    they are two different places 1.7 km apart, one a private park and one a
    state park. Same shape for `Rufus RV Park` against `Rufus Landing Recreation
    Area` and `Thousand Trails Crescent Bar` against `Crescent Bar Recreation
    Area`: all three wrote a discount onto a public campground before this
    existed. A whole match is one where the core token sets agree outright, or
    the strings differ only in spelling and punctuation ("Ballard's" / "Ballards"),
    and only a whole match is allowed past the close band.
    """
    ca, cb = _tokens(a), _tokens(b)
    if not ca or not cb:
        return 0.0, False
    sa, sb = set(ca), set(cb)
    overlap = len(sa & sb) / min(len(sa), len(sb))
    ratio = difflib.SequenceMatcher(None, " ".join(ca), " ".join(cb)).ratio()
    score = max(overlap, ratio)
    whole = sa == sb or ratio >= 0.90
    if (sa & MODIFIERS) != (sb & MODIFIERS):
        return min(score, 0.45), False
    return score, whole


def similarity(name_a, name_b):
    best = (0.0, False)
    for a in variants(name_a):
        for b in variants(name_b):
            got = pair_score(a, b)
            if got > best:
                best = got
    return best


def accepts(score, whole, metres):
    return any(metres <= limit and score >= need and (whole or not want_whole)
               for limit, need, want_whole in BANDS)


def haversine_m(lat1, lng1, lat2, lng2):
    radius = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    x = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lng2 - lng1) / 2) ** 2)
    return 2 * radius * math.asin(math.sqrt(x))


def coords(entry):
    try:
        lat, lng = (float(part) for part in entry["location"].split(","))
        return lat, lng
    except (KeyError, ValueError, AttributeError):
        return None


def build_grid(parks):
    grid = {}
    for park in parks.values():
        if park["lat"] is None or park["lng"] is None:
            continue
        cell = (int(park["lat"] // GRID_DEG), int(park["lng"] // GRID_DEG))
        grid.setdefault(cell, []).append(park)
    return grid


def nearby(grid, lat, lng, metres):
    span = int(metres / 111000 / GRID_DEG) + 1
    ci, cj = int(lat // GRID_DEG), int(lng // GRID_DEG)
    for i in range(ci - span, ci + span + 1):
        for j in range(cj - span, cj + span + 1):
            for park in grid.get((i, j), ()):
                found = haversine_m(lat, lng, park["lat"], park["lng"])
                if found <= metres:
                    yield found, park


def match(entry, grid):
    """The one directory listing this entry is, or None.

    Returns (park, score, metres) — or None when nothing passes the bands, and
    None again when two listings that DISAGREE about the flag are both plausible
    (a resort next door to the county park). An ambiguous pair is dropped rather
    than guessed: absent is unknown, and unknown is honest.
    """
    here = coords(entry)
    if here is None:
        return None
    scored = []
    for metres, park in nearby(grid, here[0], here[1], SEARCH_M):
        score, whole = similarity(entry.get("name") or "", park["name"] or "")
        if accepts(score, whole, metres):
            scored.append((score, metres, park))
    if not scored:
        return None
    scored.sort(key=lambda row: (-row[0], row[1]))
    best = scored[0]
    for score, _metres, park in scored[1:]:
        if (park["id"] != best[2]["id"] and best[0] - score <= RIVAL_MARGIN
                and park["gs"] != best[2]["gs"]):
            return None
    return best[2], best[0], best[1]


# ── Derive, plan, apply ─────────────────────────────────────────────────────

SOURCE = "Good Sam campground directory"
HUMAN_METHODS = {"manual", "reported"}

# Where a "not a Good Sam Park" is worth recording. The directory answers for
# every listing it holds, but a national forest campground is not a place anyone
# asks an RV club discount of, and 4,166 public entries carrying "no Good Sam
# discount" would be four-fifths noise (AWH 2026-09-20). A positive is written
# wherever it is found — the 22 municipal and concession-run parks that ARE
# network parks are exactly the surprising ones.
NEGATIVE_OWNERSHIPS = {"private", "hipcamp"}


def derive(park, entry):
    """What this listing says about this entry: {} when it says nothing.

    `good_sam` follows the directory's own designation, which carries a stated
    promise ("Every Good Sam Park offers a 10% discount to Good Sam members").
    `military` is read from `paymentInfo.discounts` and is TRUE-ONLY: the list
    is a positive claim, and a park that gives a military discount without
    telling Good Sam is indistinguishable from one that doesn't.
    """
    found = {}
    if park["gs"]:
        found["good_sam"] = True
    elif entry.get("ownership") in NEGATIVE_OWNERSHIPS:
        found["good_sam"] = False
    if park["military"]:
        found["military"] = True
    return found


def human_verified(entry):
    prov = (entry.get(cs.PROVENANCE) or {}).get("discounts") or {}
    return prov.get("method") in HUMAN_METHODS


def load_entries():
    with open(CAMPGROUNDS_JSON, encoding="utf-8") as fh:
        return json.load(fh)


def plan(rows, parks, only_state=None):
    """What an apply would do, per entry — computed, never written.

    Returns (fills, conflicts, matches, skipped). `matches` carries every
    accepted pair for `--show`, including the ones that change nothing, because
    a match is the thing worth eyeballing.
    """
    grid = build_grid(parks)
    fills, conflicts, matches = {}, [], []
    skipped = Counter()
    for entry in rows:
        if entry.get("kind", "campground") != "campground":
            continue
        if only_state and entry.get("state") != only_state:
            continue
        found = match(entry, grid)
        if found is None:
            skipped["no confident match in the directory"] += 1
            continue
        park, score, metres = found
        matches.append((entry, park, score, metres))
        if human_verified(entry):
            skipped["discounts verified by a person"] += 1
            continue
        values = derive(park, entry)
        if not values:
            skipped["listed, but says nothing for this entry"] += 1
            continue
        held = entry.get("discounts") or {}
        new = {}
        for key, value in values.items():
            if key not in held:
                new[key] = value
            elif held[key] != value:
                conflicts.append((entry, key, held[key], value))
        if new:
            fills[entry["id"]] = new
        else:
            skipped["already agrees"] += 1
    return fills, conflicts, matches, skipped


def apply(fills, today):
    """Write the fills, re-reading campgrounds.json first.

    A key is written only if it is still absent, so an edit made through the
    live admin UI while this ran is never overwritten. Same contract as
    `recgov_hookups.apply`.
    """
    rows = load_entries()
    by_id = {row["id"]: row for row in rows}
    written = 0
    for cid, values in fills.items():
        entry = by_id.get(cid)
        if entry is None or human_verified(entry):
            continue
        held = entry.get("discounts") or {}
        values = {k: v for k, v in values.items() if k not in held}
        if not values:
            continue
        prov = dict(entry.get(cs.PROVENANCE) or {})
        prov["discounts"] = {"source": SOURCE, "checked": today, "method": "derived"}
        cs.apply_update(entry, {"discounts": values, cs.PROVENANCE: prov})
        written += 1
    write_entries(rows)
    return written


def write_entries(rows):
    tmp = CAMPGROUNDS_JSON + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, CAMPGROUNDS_JSON)


def retract(parks, apply_it):
    """Drop values this source wrote that the CURRENT rules no longer derive.

    `plan` only ever fills, so a rule that TIGHTENS cannot undo its own earlier
    writes — the subset guard that stopped matching `Camp Eagle Nest` to a state
    park would leave the discount it already wrote sitting there. Only keys whose
    `discounts` provenance names this source are touched; a person's block and a
    key some other pass wrote are left alone.
    """
    rows = load_entries()
    grid = build_grid(parks)
    dropped = []
    for entry in rows:
        prov = (entry.get(cs.PROVENANCE) or {}).get("discounts") or {}
        if prov.get("source") != SOURCE or prov.get("method") in HUMAN_METHODS:
            continue
        held = entry.get("discounts") or {}
        found = match(entry, grid)
        wanted = derive(found[0], entry) if found else {}
        stale = [k for k in ("good_sam", "military")
                 if k in held and wanted.get(k) != held[k]]
        if not stale:
            continue
        dropped.append((entry, stale))
        if apply_it:
            for key in stale:
                held.pop(key, None)
            if not {k: v for k, v in held.items() if k != "note"}:
                entry.pop("discounts", None)
                prov_all = entry.get(cs.PROVENANCE) or {}
                prov_all.pop("discounts", None)
                if not prov_all:
                    entry.pop(cs.PROVENANCE, None)
    if apply_it and dropped:
        write_entries(rows)
    return dropped


def describe(fills, conflicts, matches, skipped, parks, show):
    listed_gs = sum(1 for p in parks.values() if p["gs"])
    matched_gs = {p["id"] for _e, p, _s, _m in matches if p["gs"]}
    print(f"directory: {len(parks)} campgrounds cached, {listed_gs} of them Good Sam Parks")
    print(f"matched:   {len(matches)} entries")
    print(f"           {len(matched_gs)} of the {listed_gs} Good Sam Parks reached an entry")
    counts = Counter()
    for values in fills.values():
        for key, value in values.items():
            counts[(key, value)] += 1
    print(f"to write:  {len(fills)} entries")
    for (key, value), count in sorted(counts.items()):
        print(f"           {key} = {str(value).lower():<5} {count}")
    for reason, count in skipped.most_common():
        print(f"skipped:   {count:>6}  {reason}")
    if conflicts:
        print(f"conflicts: {len(conflicts)} (held value kept — a person outranks the directory)")
        for entry, key, held, found in conflicts[:20]:
            print(f"           {entry['id']:>6} {entry['name'][:40]:<40} {key}: {held} vs {found}")
    if show:
        print("\nmatches:")
        for entry, park, score, metres in sorted(matches, key=lambda r: (-r[1]["gs"], r[3])):
            flag = "GS" if park["gs"] else "  "
            print(f"  {flag} sim {score:.2f} {metres:6.0f}m  {entry['id']:>6} "
                  f"[{entry.get('state')}/{entry.get('ownership')}] "
                  f"{entry['name'][:38]:<38} | {park['name'][:38]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true",
                    help="walk the Good Sam directory into the local cache")
    ap.add_argument("--state", metavar="XX",
                    help="limit to one state/province (matching, not fetching)")
    ap.add_argument("--fetch-state", metavar="XX", nargs="+",
                    help="fetch only these state codes")
    ap.add_argument("--show", action="store_true", help="print every accepted match")
    ap.add_argument("--apply", action="store_true", help="write the fills")
    ap.add_argument("--retract", action="store_true",
                    help="drop values this source wrote that the current rules no longer derive")
    args = ap.parse_args()

    if args.fetch or args.fetch_state:
        run_fetch(args.fetch_state)
        return 0

    parks = load_cache()
    if not parks:
        print(f"no cache at {CACHE_JSON} — run with --fetch first", file=sys.stderr)
        return 1

    if args.retract:
        dropped = retract(parks, args.apply)
        for entry, keys in dropped:
            print(f"  {entry['id']:>6} {entry['name'][:44]:<44} {', '.join(keys)}")
        verb = "dropped" if args.apply else "would drop"
        print(f"{verb} {len(dropped)} entries' values")
        return 0

    rows = load_entries()
    fills, conflicts, matches, skipped = plan(rows, parks, args.state)
    describe(fills, conflicts, matches, skipped, parks, args.show)
    if args.apply:
        written = apply(fills, time.strftime("%Y-%m-%d"))
        print(f"\nwrote {written} entries")
    else:
        print("\ndry run — pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
