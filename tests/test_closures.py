"""Temporary closures: stored as `status`, greyed on the map, hideable (AWH 2026-09-30).

Run from the project root:

    python -m unittest tests.test_closures -v
"""

import json
import os
import re
import unittest

import campground_schema as schema

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "templates", "campground_map.html")
CAMPGROUNDS = os.path.join(ROOT, "campgrounds.json")


class TestStatusSchema(unittest.TestCase):
    def test_accepts_a_temporary_closure(self):
        e = {}
        schema.apply_update(e, {"status": {"operating": "temporarily_closed",
                                           "reopens": "spring 2027"}})
        self.assertEqual(e["status"], {"operating": "temporarily_closed",
                                       "reopens": "spring 2027"})

    def test_refuses_an_unknown_state(self):
        # A permanent closure is not a status - the entry leaves the database.
        with self.assertRaises(schema.SchemaError):
            schema.apply_update({}, {"status": {"operating": "closed"}})

    def test_clearing_removes_the_key(self):
        e = {"status": {"operating": "temporarily_closed", "reopens": "2027"}}
        schema.apply_update(e, {"status": {"reopens": None}})
        self.assertNotIn("reopens", e["status"])


class TestMarkerPayload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import ekko_trips_app as app
        except ImportError as exc:                     # pragma: no cover
            raise unittest.SkipTest(f"app not importable: {exc}")
        cls.rows = staticmethod(app._map_marker_rows)

    def _one(self, status):
        row = {"id": 1, "name": "x", "state": "MI", "location": "1,2"}
        if status is not None:
            row["status"] = status
        return self.rows([row])[0]

    def test_closed_carries_flag_and_reopens(self):
        m = self._one({"operating": "temporarily_closed", "reopens": "2027"})
        self.assertIs(m["closed"], True)
        self.assertEqual(m["reopens"], "2027")

    def test_open_and_unknown_carry_nothing(self):
        for status in (None, {"operating": "open"}, {}):
            m = self._one(status)
            self.assertNotIn("closed", m)
            self.assertNotIn("reopens", m)


class TestTemplate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(TEMPLATE, encoding="utf-8") as fh:
            cls.tpl = fh.read()

    def test_every_marker_color_goes_through_markerFill(self):
        # A direct mode-color assignment would repaint a closed dot in its
        # legend color on the first color-mode switch or inline edit.
        direct = re.findall(r"fillColor:\s*currentMode\.colors", self.tpl)
        self.assertEqual(direct, [])
        self.assertIn("return cg.closed ? CLOSED_FILL", self.tpl)

    def test_visibility_honours_show_closed(self):
        m = re.search(r"function markerVisible\(cg\) \{(.*?)\n\}", self.tpl, re.S)
        self.assertIn("(showClosed || !cg.closed)", m.group(1))

    def test_closed_shown_by_default(self):
        self.assertIn("let showClosed = STORE.get('showClosed', true);", self.tpl)


class TestStoredData(unittest.TestCase):
    def test_every_status_validates_and_has_provenance(self):
        with open(CAMPGROUNDS, encoding="utf-8") as fh:
            rows = json.load(fh)
        closed = 0
        for e in rows:
            if "status" not in e:
                continue
            schema.apply_update({}, {"status": e["status"]})
            self.assertIn("status", e.get("provenance", {}), e["id"])
            closed += e["status"].get("operating") == "temporarily_closed"
        self.assertGreater(closed, 0)


if __name__ == "__main__":
    unittest.main()
