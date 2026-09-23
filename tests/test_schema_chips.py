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
    "hookups": ["electric", "water", "sewer"],
    "facilities": ["vault_toilets", "potable_water", "dump"],
    "sites": ["count", "max_rig_ft", "pull_through"],
    "season": ["year_round", "opens", "closes"],
    "booking": ["reservable", "window_opens_days", "reserve_until", "fcfs",
                "min_stay", "max_stay_nights"],
    "fees": ["nightly_low", "nightly_high", "currency", "reservation_fee",
             "nonresident", "prereq_pass", "entrance", "surcharges"],
    "discounts": ["good_sam", "military", "interagency_senior_access"],
}

LABELS = {"max_rig_ft": "Max rig length (ft)", "electric": "Electric (amps)",
          "dump": "Dump station", "year_round": "Open year-round",
          "pull_through": "Pull through", "count": "Count",
          "good_sam": "Good Sam",
          "interagency_senior_access": "America the Beautiful Senior/Access"}


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

    # ── Discounts ───────────────────────────────────────────────────────────

    def test_a_discount_chip_names_what_it_buys(self):
        """The label names the CLUB. "good sam" beside "showers" tells a reader
        who has never heard of it nothing, and one who has cannot tell whether
        it means a discount, a rating or a listing."""
        self.assertEqual(self.chips("discounts", {"good_sam": True}),
                         ["Good Sam discount"])

    def test_a_measured_no_says_so(self):
        self.assertEqual(self.chips("discounts", {"good_sam": False}),
                         ["no Good Sam discount"])

    def test_an_ordinary_word_is_not_capitalised(self):
        """A chip run reads as prose, so only the proper nouns keep their case."""
        self.assertEqual(self.chips("discounts", {"military": True, "good_sam": True}),
                         ["Good Sam discount", "military discount"])

    def test_the_interagency_pass_is_named_the_way_it_is_sold(self):
        """"America the Beautiful Senior/Access discount" is the title of the
        pass, not a sentence; the chip says what a camper buys at the gate."""
        self.assertEqual(self.chips("discounts", {"interagency_senior_access": True}),
                         ["America the Beautiful senior/access discount"])

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

    def test_min_stay_season_bound_is_never_dropped(self):
        """Maryland's and Pennsylvania's weekend minimum runs Memorial Day to
        Labor Day and does not exist outside it. Dropping `season` reported
        both as year-round — stricter than the rule, in the direction a reader
        cannot check."""
        self.assertEqual(
            self.chips("booking", {"min_stay": [
                {"nights": 2, "applies": "weekend",
                 "season": "Memorial Day - Labor Day"},
                {"nights": 3, "applies": "holiday"}]}),
            ["min stay 2 nights on weekends (Memorial Day - Labor Day), "
             "3 on holidays"])

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
            self.chips("hookups", {"electric": 50, "water": True, "sewer": True}),
            ["full hookups (50A)"])

    def test_dump_station_is_a_facility(self):
        # Not a hookup: nothing at the site connects to it (AWH 2026-09-23).
        self.assertEqual(self.chips("facilities", {"dump": True}), ["dump station"])
        self.assertEqual(self.chips("facilities", {"dump": False}),
                         ["no dump station"])

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



@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class GroupNoneTest(unittest.TestCase):
    """A group answered "none" as a whole (doc §8.8).

    Built from the REAL `to_client()` rather than the hand-kept GROUPS above,
    because the rule turns on server metadata: which groups carry `none`, and
    each field's kind/choices, which decide its none value.
    """

    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, REPO)
        import campground_schema
        cls.schema = campground_schema.to_client()
        cls.ctx = quickjs.Context()
        with open(os.path.join(REPO, "static", "campground-schema.js"),
                  encoding="utf-8") as fh:
            cls.ctx.eval(fh.read())
        cls.ctx.eval("const S = " + json.dumps(cls.schema) + ";"
                     "function g(k) { return S.find(x => x.key === k); }"
                     "function chips(k, v, keys) { return JSON.stringify(sfChips("
                     "g(k), JSON.parse(v), keys ? new Set(JSON.parse(keys)) : undefined)); }"
                     "function noneOf(k) { const o = {}; g(k).fields.forEach(f => {"
                     "const n = sfNoneValue(f); if (n !== undefined) o[f.key] = n; });"
                     "return JSON.stringify(o); }")

    def chips(self, group, values, keys=None):
        return json.loads(self.ctx.eval(
            "chips(%s, %s, %s)" % (json.dumps(group), json.dumps(json.dumps(values)),
                                   json.dumps(json.dumps(keys)) if keys else "null")))

    def none_of(self, group):
        return json.loads(self.ctx.eval("noneOf(%s)" % json.dumps(group)))

    def test_the_none_groups_are_the_three_asked_for(self):
        self.assertEqual({g["key"] for g in self.schema if g["none"]},
                         {"hookups", "facilities", "discounts"})

    def test_every_field_of_a_none_group_has_a_none_value(self):
        # Otherwise the checkbox would leave a field unknown and the popup's
        # "none" would never fire for that group.
        for g in self.schema:
            if not g["none"]:
                continue
            fields = {f["key"] for f in g["fields"] if f["key"] != "note"}
            self.assertEqual(set(self.none_of(g["key"])), fields, g["key"])

    def test_electric_none_is_zero_amps(self):
        self.assertEqual(self.none_of("hookups")["electric"], 0)

    def test_whole_group_absent_reads_none(self):
        for group in ("hookups", "facilities", "discounts"):
            self.assertEqual(self.chips(group, self.none_of(group)), ["none"], group)

    def test_one_unknown_field_keeps_the_itemised_chips(self):
        # Unknown is not none: dump unrecorded means nobody looked.
        values = self.none_of("facilities")
        del values["dump"]
        self.assertNotIn("none", self.chips("facilities", values))

    def test_hookups_none_is_the_three_connections(self):
        self.assertEqual(set(self.none_of("hookups")), {"electric", "water", "sewer"})
        self.assertIn("dump", self.none_of("facilities"))

    def test_one_yes_keeps_the_itemised_chips(self):
        values = dict(self.none_of("facilities"), vault_toilets=True)
        self.assertNotIn("none", self.chips("facilities", values))

    def test_partial_key_run_is_not_a_whole_group(self):
        # The popup's verified half restricted to two keys (the rest inherited)
        # must not claim the whole group is none.
        self.assertEqual(
            self.chips("discounts", self.none_of("discounts"), ["good_sam", "military"]),
            ["no Good Sam discount", "no military discount"])

    def test_other_groups_never_fold(self):
        self.assertEqual(self.chips("sites", {"pull_through": False}),
                         ["no pull-throughs"])


@unittest.skipIf(quickjs is None, "quickjs not installed (pip install quickjs)")
class PopupChipsTest(unittest.TestCase):
    """The map popup's cut (`sfPopupChips`): only the "no"s that change a
    camper's plan get a chip (AWH 2026-09-23)."""

    setUpClass = classmethod(GroupNoneTest.setUpClass.__func__)
    none_of = GroupNoneTest.none_of

    def chips(self, group, values, keys=None):
        return json.loads(self.ctx.eval(
            "JSON.stringify(sfPopupChips(g(%s), %s, %s))"
            % (json.dumps(group), json.dumps(values),
               "new Set(%s)" % json.dumps(keys) if keys else "undefined")))

    def test_no_flush_and_no_vault_is_no_toilets(self):
        self.assertEqual(self.chips("facilities", {"showers": True, "flush_toilets": False,
                                                   "vault_toilets": False, "dump": True}),
                         ["showers", "no toilets", "dump station"])

    def test_one_kind_of_toilet_shows_only_that_kind(self):
        self.assertEqual(self.chips("facilities", {"flush_toilets": False,
                                                   "vault_toilets": True}),
                         ["vault toilets"])
        self.assertEqual(self.chips("facilities", {"flush_toilets": True,
                                                   "vault_toilets": False}),
                         ["flush toilets"])

    def test_comfort_facilities_speak_only_when_yes(self):
        self.assertEqual(self.chips("facilities", {"showers": False, "laundry": False,
                                                   "camp_store": True, "wifi": False,
                                                   "potable_water": False}),
                         ["no potable water", "camp store"])

    def test_discounts_speak_only_when_yes(self):
        self.assertEqual(self.chips("discounts", {"good_sam": False, "military": True}),
                         ["military discount"])
        self.assertEqual(self.chips("discounts", self.none_of("discounts")), [])

    def test_water_and_sewer_speak_only_when_yes(self):
        self.assertEqual(self.chips("hookups", {"electric": 30, "water": True,
                                                "sewer": False}),
                         ["30A", "water"])
        self.assertEqual(self.chips("hookups", {"electric": 0, "water": False}),
                         ["no electric"])

    def test_a_dry_campground_still_says_so(self):
        """Dropping the false water/sewer first would unfold it to "no electric"."""
        self.assertEqual(self.chips("hookups", {"electric": 0, "water": False,
                                                "sewer": False}),
                         ["none"])
        self.assertEqual(self.chips("hookups", {"electric": 0, "water": False,
                                                "sewer": False}, ["water", "sewer",
                                                                  "electric"]),
                         ["none"])

    def test_whole_facilities_none_still_reads_none(self):
        self.assertEqual(self.chips("facilities", self.none_of("facilities")), ["none"])

    def test_restricted_keys_are_respected(self):
        self.assertEqual(self.chips("facilities", {"showers": True, "flush_toilets": False,
                                                   "vault_toilets": False},
                                    ["showers"]),
                         ["showers"])


if __name__ == "__main__":
    unittest.main()
