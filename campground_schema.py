"""Structured campground fields: the vocabulary, the merge, and the registry.

`docs/campground-schema.md` is the design record and the reason for every rule
here; this module is its executable half. Stdlib only — it is reachable from the
web app, so it stays inside `ekko_trips_requirements.txt`'s closure.

Three invariants from that doc are enforced here rather than merely described:

1. **Absent means unknown.** A missing key means nobody looked; `False` means
   somebody looked and there is none. Nothing in this module ever writes a
   placeholder to stand in for "not determined", and `apply_update` removes a
   key rather than blanking it.

2. **A group merges per-subkey.** The flat whitelist on the campground PUT is
   what stops a UI save clobbering `waterfront_evidence`, which the client never
   receives. A nested group re-creates that bug one level down: a form sending
   `hookups` with the four keys it knows about would wipe a fifth that an
   extraction pass wrote. So a group the client omits is untouched, a subkey the
   client omits inside a group it did send is untouched, and only an explicit
   null (or "") clears one.

3. **An unknown subkey is an ERROR, not a silent drop.** The flat whitelist
   fails quietly — a field missing from it just never saves, which is a trap the
   doc warns about. Multiplied across nine groups that becomes untenable, so
   this module refuses the write and names the key. Adding a field to the form
   without adding it here now fails loudly on the first save.

Depth: groups merge per-subkey, but a subkey whose value is an object
(`min_stay`, `nonresident`, `reserve_until`, `prereq_pass`) is replaced WHOLE.
Those are single conceptual rules — part-merging a waiver into a minimum-stay
rule yields a rule nobody wrote.
"""

# ── Field-spec vocabulary ───────────────────────────────────────────────────
# ("kind", constraint). Kinds: bool, int, num, str, mmdd, obj.

BOOL = ("bool", None)
NUM = ("num", None)
STR = ("str", None)
MMDD = ("mmdd", None)          # "MM-DD" — recurring, so deliberately no year


def INT(*allowed):
    """Integer field; with args, restricted to those values.

    The allowed values stay an ordered tuple rather than a set: the manage form
    renders them as a dropdown, and "0, 20, 30, 50" is the order an author would
    read them in. Membership tests on a handful of values cost nothing.
    """
    return ("int", tuple(allowed) if allowed else None)


def ENUM(*values):
    return ("str", tuple(values))


def OBJ(**fields):
    return ("obj", fields)


def LIST(spec, slots=2):
    """An ordered list of rules, replaced whole like an OBJ.

    Forced by the first agency actually verified. Indiana runs TWO minimum-stay
    rules at once — two nights on weekends, waived if the site is still unrented
    three days out, and three nights on holiday weekends which the waiver
    explicitly does NOT touch ("Required holiday minimum stays are excluded from
    this relaxed rule"). A single rule object cannot hold that, and every one of
    the four states verified so far has the same weekend + holiday pair.

    `slots` is how many the manage form draws; the value itself is unbounded.
    """
    return ("list", (spec, slots))


# ── The schema ──────────────────────────────────────────────────────────────
# Mirrors docs/campground-schema.md §4. Every key is optional at every level;
# absent is unknown. Adding a field here is what makes it savable — see
# invariant 3 above.

SCHEMA = {
    "rating": {
        "source": ENUM("rvlife", "goodsam"),
        "stars": NUM,
        "price_tier": INT(0, 1, 2, 3, 4),   # the RV Life "$" count, as imported
        "checked": STR,                      # "YYYY-MM"
        "note": STR,
    },
    "hookups": {
        "electric": INT(0, 20, 30, 50),      # HIGHEST amp available at a site
        "water": BOOL,                       # at the site, not a communal spigot
        "sewer": BOOL,
        "dump": BOOL,                        # on-site dump station; independent of sewer
        "note": STR,
    },
    "sites": {
        "count": INT(),
        "max_rig_ft": INT(),
        "pull_through": BOOL,
        "note": STR,
    },
    "facilities": {
        "showers": BOOL,
        "flush_toilets": BOOL,
        "vault_toilets": BOOL,
        "potable_water": BOOL,               # communal spigots, even with no hookups
        "laundry": BOOL,
        "camp_store": BOOL,
        "wifi": BOOL,
        "note": STR,
    },
    "season": {
        "year_round": BOOL,
        "opens": MMDD,
        "closes": MMDD,
        "note": STR,
    },
    "booking": {
        "reservable": BOOL,
        "platform": ENUM("recreation.gov", "reserveamerica", "usedirect",
                         "goingtocamp", "campspot", "roverpass", "hipcamp",
                         "sepaq", "operator", "phone", "none"),
        "url": STR,
        "window_opens_days": INT(),
        # Conditional by necessity: Iowa's FCFS is what its cutoff CREATES, so a
        # flat fcfs boolean cannot tell Iowa and Maryland apart. Evaluated
        # against a query's arrival date, never stored as a verdict.
        "reserve_until": OBJ(relative_to=ENUM("arrival"),
                             at=STR,                 # "HH:MM" local
                             offset_hours=NUM),      # negative = before arrival
        "fcfs": ENUM("never", "always", "after_cutoff", "some_sites"),
        # The waiver is the whole point: a scalar nights=2 drops all 41 Indiana
        # state parks from a one-night search when every one of them qualifies.
        # A LIST because agencies run several at once and a waiver may apply to
        # one but not another. An evaluator takes the strictest rule whose
        # `applies` matches the arrival date.
        "min_stay": LIST(OBJ(nights=INT(),
                             applies=ENUM("always", "weekend", "holiday",
                                          "summer"),
                             season=STR,
                             waived_if=OBJ(booking_within_days=INT()))),
        "max_stay_nights": INT(),
        "note": STR,                         # anything the vocabulary can't hold
    },
    "fees": {
        # BASE rate: what a RESIDENT pays for a plain site with no amenities.
        # Every other key here modifies it. Storing the non-resident or
        # with-hookups price instead would make the field incomparable between
        # agencies and double-count whenever a modifier is applied on top.
        "nightly_low": NUM,
        "nightly_high": NUM,
        "currency": ENUM("USD", "CAD"),
        "reservation_fee": NUM,
        # Three distinct mechanics; flattening them loses the cases that matter.
        # A prerequisite pass is a function of TRIP LENGTH — a season pass
        # amortizes fine over a week and terribly over one night.
        "nonresident": OBJ(type=ENUM("surcharge", "multiplier"),
                           amount=NUM, factor=NUM,
                           per=ENUM("stay", "night")),
        "prereq_pass": OBJ(name=STR, price=NUM,
                           valid=ENUM("season", "year", "day")),
        # A park ENTRANCE fee is not a camping surcharge, and conflating them
        # misreports both. Indiana charges every vehicle to enter ($7 resident,
        # $15 non-resident) and has no non-resident camping rate at all; New
        # York has no differential gate fee and a real $5/night camping
        # surcharge. Stored as both sides so the differential is derivable
        # rather than baked in.
        # `per` matters as much as the amount: Indiana's $15 is once per camping
        # stay, Michigan's Recreation Passport is an annual vehicle pass at $15
        # resident / $40 non-resident, and a day rate can be better or worse
        # than the annual one depending purely on trip length.
        "entrance": OBJ(resident=NUM, nonresident=NUM,
                        per=ENUM("vehicle_day", "vehicle_stay", "vehicle_year",
                                 "person_day")),
        # Per-night add-ons on top of the base rate. Both systems verified so
        # far price the amenities separately, and they are exactly what a search
        # filters on: electric costs $7-8/night extra in NY State and in Suffolk
        # County, and a waterfront site $6-10. A cost estimate that ignores them
        # understates the night a traveller actually needs.
        # `water` is priced apart from `electric` where an agency sells the two
        # separately: Salisbury and Scusset Beach charge $4 for water and $6 for
        # electric on the same site, so folding them into full_hookup would
        # invent a bundle Massachusetts does not sell.
        "surcharges": OBJ(electric=NUM, water=NUM, sewer=NUM, full_hookup=NUM,
                          waterfront=NUM, oceanfront=NUM, weekend=NUM,
                          premium_site=NUM, pet=NUM),
        "checked": STR,
        "note": STR,
    },
    "discounts": {
        "good_sam": BOOL,
        "passport_america": BOOL,
        "koa_value_kard": BOOL,
        "military": BOOL,
        # America the Beautiful Senior/Access — halves camping at most USFS and
        # USACE sites, so it belongs on the registry row, not on 3,738 entries.
        "interagency_senior_access": BOOL,
        "note": STR,
    },
}

GROUPS = tuple(SCHEMA)

# Top-level scalars this module owns, alongside the groups.
POLICY_REF = "policy_ref"
# `policy_ref: "none"` means INHERIT NOTHING — the entry is its own agency. It
# exists because `{ownership}:{state}` is derived and therefore unavoidable: an
# entry cannot be `ownership: state` in Georgia without inheriting `state:GA`,
# and Jekyll Island is legitimately both a state park and outside the state
# park system (its own authority, Campspot rather than ReserveAmerica, its own
# gate fee, and a Georgia ParkPass explicitly not valid). Leaving it to inherit
# would print the agency's booking window and cutoff under "Typical for Georgia
# state parks" on the one campground they are wrong for, which is exactly the
# confident-falsehood-at-scale failure doc §3 exists to prevent.
POLICY_REF_NONE = "none"
PROVENANCE = "provenance"

# Per-group provenance for ENTRY-scoped verification (see doc §3). Group-level
# rather than per-field because that is how the research happens: you read one
# agency page and fill one block.
PROVENANCE_FIELDS = {
    "source": STR,
    "checked": STR,
    # derived  = a machine read it (note prose, an availability calendar)
    # manual   = a person read the agency's own page
    # reported = sourced, but NOT from the primary — a search summary of a page
    #            that blocks automated fetch, or a firsthand account. Ranks
    #            below manual and must say so in `source`; without this value a
    #            secondary reading is indistinguishable from an unrecorded one,
    #            and the Florida row would look exactly like a row nobody
    #            bothered to stamp.
    "method": ENUM("derived", "manual", "reported"),
}

# The record that an extraction pass READ this entry's note — kept whether or
# not the note yielded anything, which is the only thing that makes a re-run
# incremental. Without it, the ~70% of notes that hold no structured fact would
# be re-sent to the model on every single pass, and re-billed, forever.
#
# It is the same distinction `detect_people.py` stores in photo_people.json: a
# recorded 0 means "looked, nobody there", an absent key means "not scanned".
# Here, absent means nobody has read this note; present with no resulting values
# means it was read and said nothing extractable. Neither is a claim about the
# campground, so this is not the placeholder §2.1 forbids — a placeholder is a
# fabricated VALUE, this is an audit record of an action that really happened.
#
# One block per ENTRY rather than per group, deliberately: five group-level
# provenance blocks on each of 12.7k entries would add a quarter of a million
# lines to the file to record the same fact five times. Groups that actually
# yield a value still get their own `provenance` entry, which is where doc §3's
# per-group source/method record belongs.
NOTE_SCAN = "note_scan"
NOTE_SCAN_FIELDS = {
    "sig": STR,        # hash of the note text this scan read
    "checked": STR,    # "YYYY-MM-DD"
    "model": STR,      # which model read it, so a re-read can be targeted
}

_TRUE = {"true", "yes", "1", "on", "t"}
_FALSE = {"false", "no", "0", "off", "f"}
# What a form sends for "unknown". Both clear the key; neither stores a value.
_CLEARS = (None, "")


class SchemaError(ValueError):
    """A write that the vocabulary refuses. Carries a human-readable path."""


# ── Coercion ────────────────────────────────────────────────────────────────

def _coerce(spec, value, path):
    """Validate and normalize one value against its spec.

    Forms send strings for everything, so "50" must become 50 and "true" must
    become True — but "maybe" must raise rather than quietly becoming truthy.
    """
    kind, constraint = spec

    if kind == "bool":
        if isinstance(value, bool):
            return value
        s = str(value).strip().lower()
        if s in _TRUE:
            return True
        if s in _FALSE:
            return False
        raise SchemaError(f"{path}: expected a boolean, got {value!r}")

    if kind in ("int", "num"):
        if isinstance(value, bool):    # bool is an int subclass; never silently numeric
            raise SchemaError(f"{path}: expected a number, got {value!r}")
        try:
            num = float(value)
        except (TypeError, ValueError):
            raise SchemaError(f"{path}: expected a number, got {value!r}")
        if kind == "int":
            if num != int(num):
                raise SchemaError(f"{path}: expected a whole number, got {value!r}")
            num = int(num)
            if constraint is not None and num not in constraint:
                allowed = ", ".join(str(v) for v in constraint)
                raise SchemaError(f"{path}: {num} is not one of {allowed}")
        return num

    if kind == "mmdd":
        s = str(value).strip()
        parts = s.split("-")
        ok = len(parts) == 2 and all(p.isdigit() and len(p) == 2 for p in parts)
        if ok:
            mm, dd = int(parts[0]), int(parts[1])
            ok = 1 <= mm <= 12 and 1 <= dd <= 31
        if not ok:
            raise SchemaError(f"{path}: expected MM-DD, got {value!r}")
        return s

    if kind == "str":
        s = str(value).strip()
        if constraint is not None and s not in constraint:
            allowed = ", ".join(constraint)
            raise SchemaError(f"{path}: {s!r} is not one of {allowed}")
        return s

    if kind == "list":
        item_spec, _ = constraint
        if not isinstance(value, list):
            raise SchemaError(f"{path}: expected a list, got {value!r}")
        out = []
        for i, item in enumerate(value):
            if item in _CLEARS:
                continue          # a blank slot in the form is not a rule
            coerced = _coerce(item_spec, item, f"{path}[{i}]")
            if coerced:
                out.append(coerced)
        return out

    if kind == "obj":
        if not isinstance(value, dict):
            raise SchemaError(f"{path}: expected an object, got {value!r}")
        out = {}
        for key, val in value.items():
            if key not in constraint:
                raise SchemaError(f"{path}.{key}: unknown field")
            if val in _CLEARS:
                continue           # absent is unknown; never a placeholder
            out[key] = _coerce(constraint[key], val, f"{path}.{key}")
        return out

    raise SchemaError(f"{path}: unhandled field kind {kind!r}")


# ── The merge ───────────────────────────────────────────────────────────────

def apply_update(target, data):
    """Merge structured groups from `data` into the entry `target`, in place.

    Returns the set of group names actually touched. Raises SchemaError — before
    mutating anything — if the payload names a field the vocabulary doesn't
    hold, so a half-applied write is impossible.

    Semantics (doc §8.1):
      group absent from `data`      -> untouched
      group present, value null/""  -> whole group removed
      subkey absent from the group  -> untouched
      subkey null/""                -> that subkey removed
      group left empty              -> removed entirely, never left as {}
    """
    # Validate the whole payload first. A SchemaError must leave `target` exactly
    # as it was, or a typo'd field would half-save and the entry would carry a
    # mixture of old and new values with no record of which.
    staged = {}
    for group, incoming in data.items():
        if group == POLICY_REF:
            staged[group] = (None if incoming in _CLEARS
                             else _coerce(STR, incoming, POLICY_REF))
            continue
        if group == PROVENANCE:
            staged[group] = _stage_provenance(incoming)
            continue
        if group == NOTE_SCAN:
            staged[group] = (None if incoming in _CLEARS else
                             _coerce(OBJ(**NOTE_SCAN_FIELDS), incoming, NOTE_SCAN))
            continue
        if group not in SCHEMA:
            continue                   # not ours — the flat whitelist handles it
        if incoming in _CLEARS:
            staged[group] = None
            continue
        if not isinstance(incoming, dict):
            raise SchemaError(f"{group}: expected an object, got {incoming!r}")
        fields = SCHEMA[group]
        staged_group = {}
        for key, value in incoming.items():
            if key not in fields:
                raise SchemaError(f"{group}.{key}: unknown field")
            if value in _CLEARS:
                staged_group[key] = None
                continue
            coerced = _coerce(fields[key], value, f"{group}.{key}")
            # An empty list or object is the ABSENCE of a rule, not a rule that
            # says nothing — clear the key rather than storing [] or {}.
            staged_group[key] = coerced if coerced or coerced in (0, False) else None
        staged[group] = staged_group

    touched = set()
    for group, value in staged.items():
        touched.add(group)
        if value is None:
            target.pop(group, None)
            continue
        if group in (POLICY_REF, NOTE_SCAN):
            target[group] = value
            continue
        current = dict(target.get(group) or {})
        for key, val in value.items():
            if val is None:
                current.pop(key, None)
            else:
                current[key] = val
        if current:
            target[group] = current
        else:
            target.pop(group, None)     # an emptied group is unknown, not {}
    return touched


def _stage_provenance(incoming):
    """Validate a provenance payload: {group: {source, checked, method}}."""
    if incoming in _CLEARS:
        return None
    if not isinstance(incoming, dict):
        raise SchemaError(f"{PROVENANCE}: expected an object, got {incoming!r}")
    out = {}
    for group, block in incoming.items():
        if group not in SCHEMA:
            raise SchemaError(f"{PROVENANCE}.{group}: unknown group")
        if block in _CLEARS:
            out[group] = None
            continue
        out[group] = _coerce(OBJ(**PROVENANCE_FIELDS), block,
                             f"{PROVENANCE}.{group}")
    return out


# ── Registry resolution ─────────────────────────────────────────────────────

def policy_refs(entry):
    """Registry rows this entry inherits from, MOST SPECIFIC FIRST.

    Three levels, because two kinds of agency are shaped differently:

      1. an explicit `policy_ref` — a county, or a named federal agency
      2. `{ownership}:{state}` — where the state IS the agency (state parks,
         provincial parks), which is most of the database
      3. `{ownership}` alone — where it is not. Federal camping policy is set
         per-agency and largely by recreation.gov, not per state, so without
         this level a single federal rule would need fifty identical
         `federal:XX` rows. This level is what makes the 3,738 federal entries
         reachable at all.

    More specific wins per FIELD, not per row, so a `federal` baseline and a
    `federal:usfs` override compose rather than replacing one another.

    The sentinel `policy_ref: "none"` returns NO rows at all. Levels 2 and 3 are
    derived from ownership and state, so they cannot otherwise be declined, and
    an entry that is genuinely state-owned yet outside the state agency's system
    would inherit terms that are wrong for it (see POLICY_REF_NONE).
    """
    refs = []
    explicit = (entry.get(POLICY_REF) or "").strip()
    if explicit.lower() == POLICY_REF_NONE:
        return refs
    if explicit:
        refs.append(explicit)
    ownership = (entry.get("ownership") or "").strip()
    state = (entry.get("state") or "").strip()
    if ownership and state:
        refs.append(f"{ownership}:{state}")
    if ownership:
        refs.append(ownership)
    return refs


def policy_ref(entry):
    """The most specific registry row this entry names. See `policy_refs`."""
    refs = policy_refs(entry)
    return refs[0] if refs else None


def _inherited(entry, registry):
    """Merge every registry level this entry inherits, least specific first."""
    merged = {}
    for ref in reversed(policy_refs(entry)):
        row = registry.get(ref)
        if not row:
            continue
        for group, values in row.items():
            if group in (PROVENANCE, NOTE_SCAN) or not isinstance(values, dict):
                continue
            merged.setdefault(group, {}).update(values)
    return merged


def resolve(entry, registry=None):
    """Effective structured fields for one entry, with each group's scope.

    Returns ``{group: {"values": {...}, "scope": ..., "inherited": [keys]}}``,
    where scope is ``"entry"``, ``"agency"`` or ``"mixed"``. Nothing is copied
    into stored entries — inheritance happens HERE, on read, so a registry
    correction propagates instantly and "verified" stays literally checkable:
    the entry has its own key, or it does not.

    `inherited` names the keys the AGENCY supplied, because a group-level scope
    is not enough for a reader-facing surface. A mixed group holds both kinds of
    value at once, and doc §3 forbids an inherited one from phrasing itself as a
    fact about the park — so the popup has to know which half is which, field by
    field, not merely that the group has some of each.

    A group absent from both the entry and the registry is absent from the
    result. It is unknown, and unknown must never render as a value, nor be
    grounds to exclude the entry from a search (doc §2.2).
    """
    registry = registry or {}
    row = _inherited(entry, registry)
    out = {}
    for group in SCHEMA:
        own = entry.get(group) or {}
        inherited = row.get(group) or {}
        if not own and not inherited:
            continue
        values = dict(inherited)
        values.update(own)
        if own and inherited:
            scope = "entry" if set(own) >= set(inherited) else "mixed"
        else:
            scope = "entry" if own else "agency"
        out[group] = {"values": values, "scope": scope,
                      "inherited": [k for k in values if k not in own]}
    return out


def field_scope(entry, group, key, registry=None):
    """Where one field's value comes from: 'entry', 'agency', or None."""
    if key in (entry.get(group) or {}):
        return "entry"
    row = _inherited(entry, registry or {})
    if key in (row.get(group) or {}):
        return "agency"
    return None


def validate_row(row, label="row"):
    """Validate one registry row against the same vocabulary entries use.

    Returns a normalized copy. Raises SchemaError naming the offending field, so
    a malformed registry fails where it is written rather than silently
    inheriting a wrong value to every campground under it.
    """
    if not isinstance(row, dict):
        raise SchemaError(f"{label}: expected an object")
    staged = {}
    apply_update(staged, {k: v for k, v in row.items()
                         if k not in (POLICY_REF, NOTE_SCAN)})
    return staged


# ── Client projection ───────────────────────────────────────────────────────
# The manage form renders from THIS, served by the route, rather than from a
# hand-kept copy in the template. A second vocabulary in JavaScript would drift
# the first time a field was added on one side only, and the failure mode is
# quiet: the form would keep saving happily while silently omitting the field.

GROUP_LABELS = {
    "rating": "Rating",
    "hookups": "Hookups",
    "sites": "Sites",
    "facilities": "Facilities",
    "season": "Season",
    "booking": "Booking",
    "fees": "Fees",
    "discounts": "Discounts",
}

# Only where the key doesn't read well on its own; everything else is derived.
FIELD_LABELS = {
    "fcfs": "First-come, first-served",
    "url": "Booking URL",
    "window_opens_days": "Booking opens (days ahead)",
    "reserve_until": "Booking closes",
    "min_stay": "Minimum stay",
    "max_stay_nights": "Maximum stay (nights)",
    "max_rig_ft": "Max rig length (ft)",
    "electric": "Electric (amps)",
    "dump": "Dump station",
    "potable_water": "Potable water",
    "nightly_low": "Nightly rate (low)",
    "nightly_high": "Nightly rate (high)",
    "reservation_fee": "Reservation fee",
    "nonresident": "Non-resident charge",
    "prereq_pass": "Required pass",
    "price_tier": "Price tier ($ count)",
    "good_sam": "Good Sam",
    "passport_america": "Passport America",
    "koa_value_kard": "KOA Value Kard",
    "interagency_senior_access": "America the Beautiful Senior/Access",
    "opens": "Opens (MM-DD)",
    "closes": "Closes (MM-DD)",
    "year_round": "Open year-round",
    "relative_to": "Relative to",
    "at": "At (HH:MM)",
    "offset_hours": "Offset (hours)",
    "booking_within_days": "Waived if booking within (days)",
    "waived_if": "Waiver",
    "entrance": "Park entrance fee",
    "surcharges": "Per-night amenity surcharges",
    "full_hookup": "Full hookup",
    "premium_site": "Premium/flagship site",
    "oceanfront": "Oceanfront",
    "nightly_low": "Base nightly rate (low, resident)",
    "nightly_high": "Base nightly rate (high, resident)",
    "resident": "Resident",
    "nonresident": "Non-resident",
    "season": "Season it applies in",
    "applies": "Applies",
    "nights": "Nights",
    "checked": "Checked (YYYY-MM)",
}


def _label(key):
    return FIELD_LABELS.get(key) or key.replace("_", " ").capitalize()


def _spec_to_client(spec, key):
    kind, constraint = spec
    if kind == "list":
        item_spec, slots = constraint
        return {"kind": "list", "label": _label(key), "slots": slots,
                "item": _spec_to_client(item_spec, key)}
    if kind == "obj":
        return {"kind": "obj", "label": _label(key),
                "fields": [dict(_spec_to_client(s, k), key=k)
                           for k, s in constraint.items()]}
    out = {"kind": kind, "label": _label(key)}
    if constraint is not None:
        out["choices"] = list(constraint)
    return out


def to_client():
    """The vocabulary as the manage form needs it: ordered groups and fields."""
    return [{"key": group,
             "label": GROUP_LABELS.get(group, group.title()),
             "fields": [dict(_spec_to_client(spec, key), key=key)
                        for key, spec in fields.items()]}
            for group, fields in SCHEMA.items()]
