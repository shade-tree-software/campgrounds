"""The campground fact chips, run through the real `static/campground-schema.js`.

Every rule here is a phrasing that was shipped and found unreadable (doc §8.7),
so the test is against the SHIPPED module rather than a Python restatement of
it — the map popup and the manage form both call this file, and a copy here
would pin the copy. Needs `quickjs` (`pip install quickjs`); the dev box has no
node, see the repo's JS-testing note.

The chips are what a reader sees, so what is asserted is the whole string.
"""

import json
import os
import unittest

try:
    import quickjs
except ImportError:  # pragma: no cover - environment-dependent
    quickjs = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The one group shape the tests need from `campground_schema.to_client()`. Built
# here rather than imported so a field's LABEL changing (which is a server-side
# decision) can't quietly rewrite what this asserts about the phrasing.
GROUPS = {
    "hookups": ["electric", "water", "sewer", "dump"],
    "sites": ["count", "max_rig_ft", "pull_through"],
    "season": ["year_round", "opens", "closes"],
    "booking": ["reservable", "window_opens_days", "reserve_until", "fcfs",
                "min_stay", "max_stay_nights"],
    "fees": ["nightly_low", "nightly_high", "currency", "reservation_fee",
             "nonresident", "prereq_pass", "entrance", "surcharges"],
}

LABELS = {"max_rig_ft": "Max rig length (ft)", "electric": "Electric (amps)",
          "dump": "Dump station", "year_round": "Open year-round",
          "pull_through": "Pull through", "count": "Count"}


def group_spec(key):
    return {"key": key,
            "fields": [{"key": f, "label": LABELS.get(f, f.replace("_", " ").capitalize())}
                       for f in GROUPS[key]]}


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class ChipPhrasingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = quickjs.Context()
        with open(os.path.join(REPO, "static", "campground-schema.js"),
                  encoding="utf-8") as fh:
            cls.ctx.eval(fh.read())
        cls.ctx.eval(
            "function chips(g, v) { return JSON.stringify("
            "sfChips(JSON.parse(g), JSON.parse(v))); }")
        cls.chips_fn = cls.ctx.get("chips")

    def chips(self, group, values):
        return json.loads(self.chips_fn(json.dumps(group_spec(group)),
                                        json.dumps(values)))

    # ── Units and abbreviations ─────────────────────────────────────────────

    def test_booking_shorthand_is_spelled_out(self):
        """"180d ahead" / "max 14n" read as typos to anyone who didn't write them."""
        self.assertEqual(
            self.chips("booking", {"window_opens_days": 180, "max_stay_nights": 14}),
            ["books 180 days ahead", "max stay 14 nights"])

    def test_max_rig_length_names_what_is_measured(self):
        self.assertEqual(self.chips("sites", {"count": 22, "max_rig_ft": 25}),
                         ["22 sites", "rigs to 25 ft"])

    def test_min_stay_says_nights_once_and_when_each_rule_applies(self):
        self.assertEqual(
            self.chips("booking", {"min_stay": [{"nights": 2, "applies": "weekend"},
                                                {"nights": 3, "applies": "holiday"}]}),
            ["min stay 2 nights on weekends, 3 on holidays"])

    def test_booking_cutoff_says_what_closes_and_relative_to_what(self):
        self.assertEqual(
            self.chips("booking", {"reserve_until": {"relative_to": "arrival",
                                                     "at": "23:00"}}),
            ["book by 23:00 on arrival day"])
        self.assertEqual(
            self.chips("booking", {"reserve_until": {"relative_to": "arrival",
                                                     "offset_hours": -72}}),
            ["book by 72h before arrival"])

    def test_fcfs_enum_is_never_shown_raw(self):
        for value, expected in [("never", "no walk-up sites"),
                                ("always", "walk-ups welcome"),
                                ("after_cutoff", "walk-ups after the booking cutoff"),
                                ("some_sites", "some walk-up sites")]:
            self.assertEqual(self.chips("booking", {"fcfs": value}), [expected])

    # ── The res / non-res collision ─────────────────────────────────────────

    def test_reservation_fee_is_not_abbreviated_to_res(self):
        """Virginia prints both of these, one chip apart — see doc §8.7."""
        self.assertEqual(
            self.chips("fees", {"reservation_fee": 5,
                                "nonresident": {"type": "surcharge", "amount": 5,
                                                "per": "night"}}),
            ["+$5 booking fee", "non-resident +$5/night"])

    # ── Negatives that a label cannot carry ─────────────────────────────────

    def test_not_year_round_is_seasonal(self):
        self.assertEqual(self.chips("season", {"year_round": False}), ["seasonal"])
        self.assertEqual(self.chips("season", {"year_round": True}),
                         ["open year-round"])

    # ── Dates ───────────────────────────────────────────────────────────────

    def test_season_span_is_one_chip_in_readable_dates(self):
        self.assertEqual(
            self.chips("season", {"year_round": False, "opens": "05-01",
                                  "closes": "10-01"}),
            ["open May 1 – Oct 1"])

    def test_an_opening_date_alone_says_opens(self):
        """"open May 15" reads as if that day were the season."""
        self.assertEqual(self.chips("season", {"opens": "05-15"}), ["opens May 15"])

    def test_a_closing_date_alone_still_speaks(self):
        """`closes` folds into `opens` normally, so it is skipped — but not when
        it is the only date recorded."""
        self.assertEqual(self.chips("season", {"closes": "09-30"}),
                         ["closes Sep 30"])

    # ── Folds ───────────────────────────────────────────────────────────────

    def test_full_and_absent_hookups_fold_to_one_chip(self):
        self.assertEqual(
            self.chips("hookups", {"electric": 50, "water": True, "sewer": True,
                                   "dump": True}),
            ["full hookups (50A)", "dump station"])
        self.assertEqual(
            self.chips("hookups", {"electric": 0, "water": False, "sewer": False,
                                   "dump": True}),
            ["no hookups", "dump station"])

    def test_a_partial_hookup_set_is_not_folded(self):
        self.assertEqual(
            self.chips("hookups", {"electric": 30, "water": True, "sewer": False}),
            ["30A", "water", "no sewer"])

    def test_dated_season_drops_the_redundant_seasonal_chip(self):
        chips = self.chips("season", {"year_round": False, "opens": "04-01",
                                      "closes": "11-01"})
        self.assertNotIn("seasonal", chips)

    # ── Expansions ──────────────────────────────────────────────────────────

    def test_surcharges_name_their_amounts(self):
        """The bare label said only that some cost exists."""
        self.assertEqual(
            self.chips("fees", {"surcharges": {"electric": 7, "full_hookup": 13}}),
            ["electric +$7/night", "full hookup +$13/night"])

    def test_entrance_fee_states_what_it_is_charged_per(self):
        self.assertEqual(
            self.chips("fees", {"entrance": {"resident": 7, "nonresident": 15,
                                             "per": "vehicle_stay"}}),
            ["park entry $7 resident, $15 non-resident (per vehicle/stay)"])
        self.assertEqual(
            self.chips("fees", {"entrance": {"resident": 15, "nonresident": 40,
                                             "per": "vehicle_year"}}),
            ["annual park pass $15 resident, $40 non-resident"])
        self.assertEqual(self.chips("fees", {"entrance": {"per": "person_day"}}),
                         ["park entry fee (per person/day)"])

    # ── Money ───────────────────────────────────────────────────────────────

    def test_nightly_rate_is_a_range_with_its_unit(self):
        self.assertEqual(
            self.chips("fees", {"nightly_low": 27, "nightly_high": 43}),
            ["$27–43/night"])

    def test_canadian_rates_are_not_printed_as_us_dollars(self):
        self.assertEqual(
            self.chips("fees", {"nightly_low": 35, "currency": "CAD"}),
            ["C$35/night"])


if __name__ == "__main__":
    unittest.main()
