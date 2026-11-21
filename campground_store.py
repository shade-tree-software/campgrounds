"""Load and save the campground database across its two tracked files.

`campgrounds.json` crossed GitHub's 50 MB warning on 2026-11-21 (55.7 MB, and
phase 7 adds ~1 MB every two days), so the four audit-record fields moved out
into a tracked sidecar, `campgrounds_audit.json`:

    waterfront_evidence  inclusion_evidence  note_scan  verify_scan

They were ~13 MB of the file. No page, API or client script reads any of them —
the web app stripped them from every browser-bound payload already — so the app
reads `campgrounds.json` alone and never needs the sidecar. Only the curation
and audit tools do, and they go through `load()` / `save()` here:

    import campground_store
    rows = campground_store.load()      # entries with their audit fields merged in
    ...edit rows...
    campground_store.save(rows)         # audit fields to the sidecar, the rest to the main file

The sidecar is `{"<id>": {field: value, ...}}`, in main-file entry order, holding
only entries that have at least one audit field. Both files are written as
`json.dumps(..., ensure_ascii=False, indent=2) + "\\n"` — the canonical format
the main file was already in, so a save only diffs the entries it changed.

`save()` MERGES by default: a field an entry doesn't carry keeps its sidecar
value. That is what makes it safe for a script that loaded the main file raw
(without the audit fields) to save through here. Entries no longer in `rows` do
lose their sidecar row — a dropped campground takes its audit record with it.
To delete an audit field from an entry, pass `authoritative=True` with rows that
came from `load()`.

An audit field found in the main file (an old script that wrote one there
directly) is read as the newer value and moved to the sidecar on the next save;
`tests/test_campground_store.py` pins that the main file carries none.

Stdlib only. Scripts run as `python3 -I` don't get the repo root on sys.path,
so they insert it themselves before importing this.
"""

import json
import os
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
CAMPGROUNDS_JSON = os.path.join(ROOT, "campgrounds.json")

AUDIT_FIELDS = ("waterfront_evidence", "inclusion_evidence", "note_scan", "verify_scan")


def audit_path(path=CAMPGROUNDS_JSON):
    """The sidecar beside a main file, named after it (a test's temp main file gets its own)."""
    stem = os.path.splitext(os.path.abspath(path))[0]
    return stem + "_audit.json"      # campgrounds.json -> campgrounds_audit.json


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def load_audit(path=CAMPGROUNDS_JSON):
    """The sidecar as {id(int): {field: value}}; a missing sidecar is empty."""
    try:
        with open(audit_path(path), encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        return {}
    return {int(k): v for k, v in raw.items()}


def load(path=CAMPGROUNDS_JSON):
    """Every main-file entry with its audit fields merged back in."""
    with open(path, encoding="utf-8") as fh:
        rows = json.load(fh)
    audit = load_audit(path)
    for e in rows:
        for k, v in audit.get(e.get("id"), {}).items():
            e.setdefault(k, v)      # a value still in the main file is the newer one
    return rows


def split(rows, audit=None, authoritative=False):
    """(main rows without audit fields, sidecar dict keyed by str id)."""
    old = {} if authoritative or audit is None else audit
    main, side = [], {}
    for e in rows:
        rec = {k: e[k] for k in AUDIT_FIELDS if k in e}
        main.append({k: v for k, v in e.items() if k not in AUDIT_FIELDS})
        i = e.get("id")
        if i is None:
            continue
        merged = dict(old.get(i, {}))
        merged.update(rec)
        merged = {k: merged[k] for k in AUDIT_FIELDS if k in merged}
        if merged:
            side[str(i)] = merged
    return main, side


def _write(path, text):
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=os.path.basename(path) + ".", suffix=".tmp")
    try:
        # mkstemp makes the file 0600; keep the target's mode (or the umask default).
        try:
            mode = os.stat(path).st_mode & 0o777
        except FileNotFoundError:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(tmp, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save(rows, path=CAMPGROUNDS_JSON, authoritative=False):
    """Write rows: audit fields to the sidecar, everything else to the main file.

    The sidecar goes first: a crash between the two leaves the new audit record
    beside the old main file, which `load()` still reads correctly.
    """
    main, side = split(rows, load_audit(path), authoritative)
    _write(audit_path(path), dumps(side))
    _write(path, dumps(main))
    return main, side
