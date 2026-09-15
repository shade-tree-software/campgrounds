"""What the campground map popup is allowed to say about a campground.

The popup is the only place most readers will ever meet the structured fields,
and it is where the provenance model earns its keep or fails quietly. Two rules
are pinned here:

1. **An inherited value must be attributable.** `resolve` hands the popup a
   merge of what was verified for this campground and what its agency supplies;
   doc §3 forbids the second half from reading as a fact about the park. The
   popup can only keep that promise if the server names the agency, so the
   payload carries a human phrase — "Indiana state parks", never `state:IN`,
   which cannot go in a sentence.

2. **The rating has to come back out somewhere.** `extract_rating.py` lifted the
   `RV Life 4*/$$ (auto 6/2026)` tail out of the note prose on 11,771 entries
   and into `rating`. The note is what the popup renders, so until the groups
   were surfaced that pass had made a published fact invisible everywhere but
   the admin form. A rating in the file and nothing in the popup is a
   regression, not a tidy-up.

Run from the project root:

    python -m unittest tests.test_campground_popup -v
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402


def _client():
    client = A.app.test_client()
    with open(os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "users.json")) as fh:
        admin = next(u for u, v in json.load(fh).items() if v.get("is_admin"))
    with client.session_transaction() as sess:
        sess["_user_id"] = admin
        sess["_fresh"] = True
    return client


class TestPolicyLabel(unittest.TestCase):
    """The agency's name, in a form that can finish the sentence "typical for…"."""

    REGISTRY = {"state:IN": {}, "federal": {}, "provincial:BC": {},
                "local:suffolk-county-ny": {}}

    def test_a_state_row_is_spelled_out(self):
        self.assertEqual(
            A._policy_label({"ownership": "state", "state": "IN"}, self.REGISTRY),
            "Indiana state parks")

    def test_a_province_reads_the_same_way(self):
        self.assertEqual(
            A._policy_label({"ownership": "provincial", "state": "BC"},
                            self.REGISTRY),
            "British Columbia provincial parks")

    def test_federal_is_not_per_state(self):
        # The level-3 row exists precisely because federal policy is set per
        # agency, so the phrase must not name Wyoming.
        self.assertEqual(
            A._policy_label({"ownership": "federal", "state": "WY"}, self.REGISTRY),
            "federal campgrounds")

    def test_an_explicit_ref_names_an_agency_no_pair_can_spell(self):
        entry = {"ownership": "local", "state": "NY",
                 "policy_ref": "local:suffolk-county-ny"}
        self.assertEqual(A._policy_label(entry, self.REGISTRY), "Suffolk County NY")

    def test_no_matching_row_means_no_label(self):
        # Most of the database: private and local entries with no agency to
        # inherit from. Nothing is inherited, so there is nothing to attribute.
        self.assertIsNone(
            A._policy_label({"ownership": "private", "state": "PA"}, self.REGISTRY))

    def test_a_row_that_does_not_exist_is_not_invented(self):
        self.assertIsNone(
            A._policy_label({"ownership": "state", "state": "GA"}, self.REGISTRY))


class TestPopupPayload(unittest.TestCase):
    """What `/api/campgrounds/<id>/popup` hands the renderer."""

    @classmethod
    def setUpClass(cls):
        cls.client = _client()
        with open(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "campgrounds.json")) as fh:
            cls.rows = json.load(fh)

    def _popup(self, cg_id):
        resp = self.client.get(f"/api/campgrounds/{cg_id}/popup")
        self.assertEqual(resp.status_code, 200)
        return resp.get_json()

    def _first(self, pred):
        row = next((r for r in self.rows if pred(r)), None)
        if row is None:
            self.skipTest("no entry of this shape in the live file")
        return row

    def test_an_inherited_group_arrives_with_its_agency_named(self):
        row = self._first(lambda r: r.get("ownership") == "state"
                          and r.get("state") == "IN")
        payload = self._popup(row["id"])
        self.assertEqual(payload["policy_label"], "Indiana state parks")
        booking = payload["policy"]["booking"]
        self.assertEqual(booking["scope"], "agency")
        self.assertIn("fcfs", booking["inherited"])

    def test_every_inherited_key_is_named_so_the_halves_can_be_split(self):
        # The renderer subtracts `inherited` from `values` to get the verified
        # half. If a key were missing from the list it would silently be drawn
        # as a fact about this campground.
        row = self._first(lambda r: r.get("ownership") == "state"
                          and r.get("state") == "IN")
        for group, block in self._popup(row["id"])["policy"].items():
            if block["scope"] != "agency":
                continue
            self.assertEqual(sorted(block["inherited"]), sorted(block["values"]),
                             f"{group}: a wholly inherited group left a key unnamed")

    def test_nothing_inherited_means_no_label(self):
        row = self._first(lambda r: r.get("rating")
                          and r.get("ownership") == "private"
                          and not r.get("policy_ref"))
        payload = self._popup(row["id"])
        self.assertNotIn("policy_label", payload)
        self.assertEqual(payload["policy"]["rating"]["inherited"], [])

    def test_the_rating_survives_its_removal_from_the_note(self):
        row = self._first(lambda r: (r.get("rating") or {}).get("stars"))
        payload = self._popup(row["id"])
        self.assertEqual(payload["policy"]["rating"]["values"]["stars"],
                         row["rating"]["stars"])
        self.assertNotIn("RV Life", payload.get("note") or "")

    def test_the_evidence_fields_still_never_reach_the_browser(self):
        row = self._first(lambda r: r.get("waterfront_evidence"))
        payload = self._popup(row["id"])
        self.assertNotIn("waterfront_evidence", payload)
        self.assertNotIn("inclusion_evidence", payload)


class TestMapPageCarriesTheVocabulary(unittest.TestCase):
    """The chips are rendered client-side, so the labels have to be on the page."""

    def test_the_schema_metadata_ships_with_the_map(self):
        html = _client().get("/campgrounds/map").get_data(as_text=True)
        self.assertIn("const CG_SCHEMA", html)
        self.assertIn("campground-schema.js", html)

    def test_a_vocabulary_change_invalidates_the_cached_page(self):
        # The map is ~1.9 MB gzipped and served against an ETag. The schema now
        # rides in that HTML, so a change to it that did not vary the tag would
        # be served stale — the same bug the template and module mtimes are in
        # this list to prevent.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for path in (os.path.join(here, "campground_schema.py"),
                     os.path.join(here, "static", "campground-schema.js")):
            self.assertIn(path, A._MAP_ETAG_INPUTS)


if __name__ == "__main__":
    unittest.main()
