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
    """Integer field; with args, restricted to those values."""
    return ("int", set(allowed) if allowed else None)


def ENUM(*values):
    return ("str", set(values))


def OBJ(**fields):
    return ("obj", fields)


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
    },
    "hookups": {
        "electric": INT(0, 20, 30, 50),      # HIGHEST amp available at a site
        "water": BOOL,                       # at the site, not a communal spigot
        "sewer": BOOL,
        "dump": BOOL,                        # on-site dump station; independent of sewer
    },
    "sites": {
        "count": INT(),
        "max_rig_ft": INT(),
        "pull_through": BOOL,
    },
    "facilities": {
        "showers": BOOL,
        "flush_toilets": BOOL,
        "vault_toilets": BOOL,
        "potable_water": BOOL,               # communal spigots, even with no hookups
        "laundry": BOOL,
        "camp_store": BOOL,
        "wifi": BOOL,
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
        "min_stay": OBJ(nights=INT(),
                        applies=ENUM("always", "weekend", "holiday", "summer"),
                        waived_if=OBJ(booking_within_days=INT())),
        "max_stay_nights": INT(),
        "note": STR,                         # anything the vocabulary can't hold
    },
    "fees": {
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
        "checked": STR,
    },
    "discounts": {
        "good_sam": BOOL,
        "passport_america": BOOL,
        "koa_value_kard": BOOL,
        "military": BOOL,
        # America the Beautiful Senior/Access — halves camping at most USFS and
        # USACE sites, so it belongs on the registry row, not on 3,738 entries.
        "interagency_senior_access": BOOL,
    },
}

GROUPS = tuple(SCHEMA)

# Top-level scalars this module owns, alongside the groups.
POLICY_REF = "policy_ref"
PROVENANCE = "provenance"

# Per-group provenance for ENTRY-scoped verification (see doc §3). Group-level
# rather than per-field because that is how the research happens: you read one
# agency page and fill one block.
PROVENANCE_FIELDS = {
    "source": STR,
    "checked": STR,
    "method": ENUM("derived", "manual"),   # derived = machine-extracted
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
                allowed = ", ".join(str(v) for v in sorted(constraint))
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
            allowed = ", ".join(sorted(constraint))
            raise SchemaError(f"{path}: {s!r} is not one of {allowed}")
        return s

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
            staged_group[key] = (None if value in _CLEARS
                                 else _coerce(fields[key], value, f"{group}.{key}"))
        staged[group] = staged_group

    touched = set()
    for group, value in staged.items():
        touched.add(group)
        if value is None:
            target.pop(group, None)
            continue
        if group == POLICY_REF:
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

def policy_ref(entry):
    """Which registry row this entry inherits from.

    Explicit `policy_ref` wins — `ownership` alone is too coarse for federal
    (USFS and NPS differ) and says nothing about a county. Otherwise
    `{ownership}:{state}`, which covers the state and provincial rows.
    """
    explicit = (entry.get(POLICY_REF) or "").strip()
    if explicit:
        return explicit
    ownership = (entry.get("ownership") or "").strip()
    state = (entry.get("state") or "").strip()
    if not ownership or not state:
        return None
    return f"{ownership}:{state}"


def resolve(entry, registry=None):
    """Effective structured fields for one entry, with each group's scope.

    Returns ``{group: {"values": {...}, "scope": "entry"|"agency"|"mixed"}}``.
    Nothing is copied into stored entries — inheritance happens HERE, on read,
    so a registry correction propagates instantly and "verified" stays literally
    checkable: the entry has its own key, or it does not.

    A group absent from both the entry and the registry is absent from the
    result. It is unknown, and unknown must never render as a value, nor be
    grounds to exclude the entry from a search (doc §2.2).
    """
    registry = registry or {}
    row = registry.get(policy_ref(entry)) or {}
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
        out[group] = {"values": values, "scope": scope}
    return out


def field_scope(entry, group, key, registry=None):
    """Where one field's value comes from: 'entry', 'agency', or None."""
    if key in (entry.get(group) or {}):
        return "entry"
    registry = registry or {}
    row = registry.get(policy_ref(entry)) or {}
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
    apply_update(staged, {k: v for k, v in row.items() if k != POLICY_REF})
    return staged
