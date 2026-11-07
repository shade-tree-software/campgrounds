"""The "Campgrounds only" role (AWH 2026-11-07): the campground map, and nothing of the family.

Two promises are pinned here:

1. **Default deny.** Every route in the app, crawled as a campgrounds-only
   account and as a campgrounds-only share link, is refused (a page redirects to
   the map, anything else is a 403) unless it is on `CAMPGROUNDS_ONLY_ENDPOINTS`
   or login-exempt. A route added later is covered without anyone remembering
   to gate it — that is the point of crawling rather than listing.

2. **No leak on the pages it may see.** The map page, its popups, the manifest
   and the header carry no home, no family location, no trip, no visit count, no
   home-relative climate and none of the app's family names.

Accounts and share links are temporary files; the real users.json,
share_tokens.json, access log and campground-view log are never touched. The
leak checks read the real home.json / family.json / trips when this machine has
them, which is where a leak would come from.

    python -m unittest tests.test_campgrounds_only -v
"""

import json
import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import ekko_trips_app as A  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402

_SAVED = {}
TOKEN = "cgonlytesttoken0000000000000000"


def setUpModule():
    tmp = tempfile.mkdtemp()
    for name in ("USERS_FILE", "SHARE_TOKENS_FILE", "ACCESS_LOG_FILE", "CAMPGROUND_VIEWS_FILE"):
        _SAVED[name] = getattr(A, name)
        setattr(A, name, os.path.join(tmp, name.lower()))
    h = generate_password_hash("x")
    with open(A.USERS_FILE, "w") as fh:
        json.dump({"admin": {"password_hash": h, "is_admin": True},
                   "viewer": {"password_hash": h},
                   "camper": {"password_hash": h, "campgrounds_only": True},
                   # Stored with flags the role overrides: it must still win.
                   "camper2": {"password_hash": h, "campgrounds_only": True,
                               "can_upload": True, "can_view_campgrounds": False},
                   "boss": {"password_hash": h, "is_admin": True, "campgrounds_only": True}},
                  fh)
    with open(A.SHARE_TOKENS_FILE, "w") as fh:
        json.dump({TOKEN: {"label": "t", "next": "/", "campgrounds_only": True}}, fh)


def tearDownModule():
    for name, value in _SAVED.items():
        setattr(A, name, value)


def _client(user):
    c = A.app.test_client()
    with c.session_transaction() as sess:
        sess["_user_id"] = user
        sess["_fresh"] = True
    return c


def _share_client():
    c = A.app.test_client()
    r = c.get("/s/" + TOKEN)
    assert r.status_code == 302, r.status_code
    return c


# Login-exempt endpoints (see `_require_login_globally`) are the same for every
# visitor, logged in or not; `logout` would end the session mid-crawl.
_EXEMPT = {"login", "logout", "service_worker", "offline", "sw_reset", "share_login",
           "serve_tile", "serve_pmtiles", "static"}


def _url_for_rule(rule):
    url = rule.rule
    for arg, conv in rule._converters.items():
        kind = type(conv).__name__
        val = "1" if kind in ("IntegerConverter", "NumberConverter") else (
            "1/0/x.jpg" if kind == "PathConverter" else "x")
        url = re.sub(r"<[^>]*\b%s>" % re.escape(arg), val, url)
    return url


class TestRole(unittest.TestCase):

    def test_the_role_overrides_the_other_capabilities(self):
        u = A._load_users()
        self.assertTrue(u["camper"].campgrounds_only)
        self.assertFalse(u["camper2"].can_upload)
        self.assertTrue(u["camper2"].can_view_campgrounds)
        self.assertFalse(u["boss"].campgrounds_only, "an admin never has it")
        self.assertFalse(u["viewer"].campgrounds_only)

    def test_a_share_link_carries_it(self):
        user = A.load_user(A.SHARE_ID_PREFIX + TOKEN)
        self.assertTrue(user.campgrounds_only)


class TestDefaultDeny(unittest.TestCase):

    def crawl(self, client):
        allowed, checked = A.CAMPGROUNDS_ONLY_ENDPOINTS | _EXEMPT, 0
        for rule in A.app.url_map.iter_rules():
            if rule.endpoint in allowed:
                continue
            url = _url_for_rule(rule)
            for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
                with self.subTest(endpoint=rule.endpoint, method=method, url=url):
                    r = client.open(url, method=method, json={})
                    checked += 1
                    if r.status_code == 302:
                        self.assertTrue(r.headers["Location"].startswith("/campgrounds/map"),
                                        r.headers["Location"])
                    else:
                        self.assertEqual(r.status_code, 403)
                        self.assertNotIn(b"trip", r.data.lower())
        self.assertGreater(checked, 60, "the crawl found too few routes to mean anything")

    def test_an_account_reaches_only_the_map(self):
        self.crawl(_client("camper"))

    def test_a_share_link_reaches_only_the_map(self):
        self.crawl(_share_client())

    def test_the_landing_page_sends_it_to_the_map(self):
        r = _client("camper").get("/")
        self.assertEqual(r.headers["Location"], "/campgrounds/map")
        r = _client("camper").get("/trips/42")
        self.assertIn("notice=campgrounds_only", r.headers["Location"])

    def test_other_roles_are_untouched(self):
        self.assertEqual(_client("viewer").get("/trips/stats").status_code, 200)
        self.assertEqual(_client("boss").get("/trips/stats").status_code, 200)


def _family_strings():
    """Names and coordinates a leak would carry: home, family homes, trips."""
    out = set()
    home = A._load_json(A.HOME_FILE)
    if home.get("home_lat") is not None:
        out.add(str(home["home_lat"]))
        out.add(str(home["home_long"]))
    for name in home.get("home_place_names") or []:
        out.add(name)
    _, family = A._map_config()
    for f in family:
        out.update((f["label"], str(f["lat"]), str(f["lng"])))
    # A trip's title that is just a campground's name ("Gambrill State Park") is
    # on the map legitimately; any other title would be a leak.
    names = "\n".join([r["name"] for r in A._load_campgrounds()]
                      + [s.get("name") or "" for s in A._load_roadside()])
    for t in A.parse_trips():
        s = t.get("summary") or ""
        if len(s) > 12 and s not in names:
            out.add(s)
    return {s for s in out if s}


class TestNoLeak(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = _client("camper")
        r = cls.client.get("/campgrounds/map")
        assert r.status_code == 200, r.status_code
        cls.page = r.get_data(as_text=True)
        cls.secrets = _family_strings()

    def test_the_map_carries_no_home_family_or_trips(self):
        self.assertIn("const HOME = null;", self.page)
        self.assertIn("const FAMILY = [];", self.page)
        self.assertIn("const CG_ONLY = true;", self.page)
        for s in self.secrets:
            # Whole values only: a family coordinate's digits can begin some
            # campground's longer one ("43.0722" inside "43.07223").
            pat = r"(?<![\w.])" + re.escape(s) + r"(?![\w])"
            self.assertIsNone(re.search(pat, self.page), msg=f"leaks {s!r}")

    def test_no_visit_counts_or_home_relative_climate(self):
        markers = json.loads(re.search(r"const CAMPGROUNDS = (\[.*?\]);\n", self.page).group(1))
        self.assertGreater(len(markers), 1000)
        for m in markers:
            self.assertNotIn("visit_count", m)
            self.assertNotIn("climate", m)
        modes = json.loads(re.search(r"const COLOR_MODES = (\[.*?\]);\n", self.page).group(1))
        self.assertEqual([m["key"] for m in modes], ["waterfront"])

    def test_the_header_names_nothing_of_ours(self):
        head = self.page.split('<div id="main-content"')[0]
        for word in ("Hamilton", "EKKOing", "road trips", "/trips/", 'class="stats"',
                     "/campgrounds/availability"):
            self.assertNotIn(word, head, msg=f"header says {word!r}")
        self.assertIn("<title>Campgrounds</title>", head)
        self.assertNotIn('class="has-tab-bar"', head)

    def test_a_visited_campground_popup_lists_no_trips(self):
        visited = next((r["id"] for r in A._load_campgrounds() if r.get("visit_count")), None)
        if visited is None:
            self.skipTest("no visited campground on this machine")
        d = self.client.get(f"/api/campgrounds/{visited}/popup").get_json()
        self.assertNotIn("trips", d)
        admin = _client("admin").get(f"/api/campgrounds/{visited}/popup").get_json()
        self.assertIn("trips", admin, "the family still sees its own visits")

    def test_the_family_view_is_cached_apart(self):
        a = _client("admin").get("/campgrounds/map").headers["ETag"]
        self.assertNotEqual(a, self.client.get("/campgrounds/map").headers["ETag"])
        r = self.client.get("/campgrounds/map", headers={"If-None-Match": a})
        self.assertEqual(r.status_code, 200, "the family page's tag must not 304 for this role")

    def test_the_manifest_is_neutral(self):
        m = self.client.get("/manifest.json").get_json()
        self.assertEqual(m["name"], "Campgrounds")
        self.assertNotIn("EKKO", json.dumps(m))
        s = _share_client().get("/manifest.json").get_json()
        self.assertTrue(s["start_url"].startswith("/s/"))
        self.assertNotIn("EKKO", json.dumps(s))


class TestAdminApi(unittest.TestCase):

    def test_an_admin_cannot_be_made_campgrounds_only_silently(self):
        r = _client("admin").put("/api/users/boss", json={"campgrounds_only": True})
        self.assertEqual(r.status_code, 400)

    def test_turning_it_on_and_off(self):
        c = _client("admin")
        c.put("/api/users/viewer", json={"campgrounds_only": True})
        row = next(u for u in c.get("/api/users").get_json() if u["username"] == "viewer")
        self.assertTrue(row["campgrounds_only"])
        c.put("/api/users/viewer", json={"can_upload": True})
        row = next(u for u in c.get("/api/users").get_json() if u["username"] == "viewer")
        self.assertFalse(row["campgrounds_only"], "granting contributor ends the role")
        c.put("/api/users/viewer", json={"can_upload": False})

    def test_share_link_flags_are_exclusive(self):
        c = _client("admin")
        d = c.post("/api/share-links", json={"label": "x", "campgrounds_only": True,
                                             "trips_only": True}).get_json()
        self.assertEqual((d["campgrounds_only"], d["trips_only"]), (True, False))
        self.assertEqual(d["next"], "/campgrounds/map")
        d = c.put("/api/share-links/" + d["token"], json={"trips_only": True}).get_json()
        self.assertEqual((d["campgrounds_only"], d["trips_only"]), (False, True))


if __name__ == "__main__":
    unittest.main()
