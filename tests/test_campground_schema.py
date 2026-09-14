"""The structured-field merge must not destroy what it cannot see.

`campgrounds.json` is written by two kinds of author: the admin manage page,
which sends whatever its form knows about, and offline extraction/research
passes, which write fields the form has never heard of. The flat field whitelist
on `PUT /api/campgrounds/<id>` is what keeps the first from clobbering the
second — `waterfront_evidence` survives a UI save only because the client never
receives it and the server merges from a list.

Nesting the new amenity/booking/fee groups re-creates that bug one level down:
a form that sends `hookups` containing the four keys it knows about would wipe a
fifth an extraction pass wrote, silently, on every save. These tests pin the
per-subkey merge that prevents it.

They also pin the rule the whole schema rests on — **absent means unknown**. A
missing key means nobody looked; `False` means somebody looked and there is
none. `process_rollups` read a missing mileage as a measured zero twice; at
12,768 entries the same confusion is unrecoverable, because a default written
once is indistinguishable from twelve thousand verified facts.

Run from the project root:

    python -m unittest tests.test_campground_schema -v
"""

import unittest

import campground_schema as cs


class TestPerSubkeyMerge(unittest.TestCase):
    """A save must only touch what the payload actually named."""

    def test_omitted_subkey_survives_a_save(self):
        # The hazard in one test: an extraction pass wrote `dump`; the form
        # doesn't know about it and sends the three fields it does know.
        entry = {"hookups": {"electric": 30, "water": True, "dump": True}}
        cs.apply_update(entry, {"hookups": {"electric": 50, "water": False,
                                            "sewer": True}})
        self.assertEqual(entry["hookups"],
                         {"electric": 50, "water": False, "sewer": True,
                          "dump": True})

    def test_omitted_group_is_untouched(self):
        entry = {"hookups": {"electric": 30}, "discounts": {"good_sam": True}}
        cs.apply_update(entry, {"hookups": {"electric": 50}})
        self.assertEqual(entry["discounts"], {"good_sam": True})

    def test_unrelated_top_level_fields_are_untouched(self):
        # The groups must not disturb the flat fields the old whitelist owns.
        entry = {"name": "X", "waterfront_evidence": "satellite at ...",
                 "hookups": {"electric": 30}}
        cs.apply_update(entry, {"hookups": {"water": True}})
        self.assertEqual(entry["waterfront_evidence"], "satellite at ...")
        self.assertEqual(entry["name"], "X")

    def test_nested_rule_objects_are_replaced_whole(self):
        # A rule is ONE value. Part-merging a waiver into it would yield a rule
        # nobody wrote — worse than either version.
        entry = {"fees": {"nonresident": {"type": "surcharge", "amount": 5,
                                          "per": "night"}}}
        cs.apply_update(entry, {"fees": {"nonresident": {"type": "multiplier",
                                                         "factor": 2.0}}})
        self.assertEqual(entry["fees"]["nonresident"],
                         {"type": "multiplier", "factor": 2.0})

    def test_a_rule_list_is_replaced_whole(self):
        entry = {"booking": {"min_stay": [{"nights": 2, "applies": "weekend"},
                                          {"nights": 3, "applies": "holiday"}]}}
        cs.apply_update(entry, {"booking": {"min_stay": [{"nights": 2}]}})
        self.assertEqual(entry["booking"]["min_stay"], [{"nights": 2}])

    def test_an_empty_rule_list_clears_rather_than_storing_it(self):
        # [] would read as "this agency has no minimum stay", which is a claim.
        entry = {"booking": {"min_stay": [{"nights": 2}]}}
        cs.apply_update(entry, {"booking": {"min_stay": []}})
        self.assertNotIn("booking", entry)


class TestAbsentMeansUnknown(unittest.TestCase):
    """Absent, False and 0 are three different claims and must stay distinct."""

    def test_false_is_stored_not_dropped(self):
        entry = {}
        cs.apply_update(entry, {"facilities": {"showers": False}})
        self.assertIs(entry["facilities"]["showers"], False)

    def test_zero_amps_is_stored_not_dropped(self):
        # electric: 0 is "somebody looked, there are no hookups" — a real datum
        # that must not collapse into "nobody looked".
        entry = {}
        cs.apply_update(entry, {"hookups": {"electric": 0}})
        self.assertEqual(entry["hookups"], {"electric": 0})

    def test_null_clears_a_subkey_back_to_unknown(self):
        entry = {"facilities": {"showers": False, "laundry": True}}
        cs.apply_update(entry, {"facilities": {"showers": None}})
        self.assertEqual(entry["facilities"], {"laundry": True})

    def test_empty_string_clears_too(self):
        # A tri-state select set to "unknown" may send "" rather than null.
        entry = {"facilities": {"showers": False, "laundry": True}}
        cs.apply_update(entry, {"facilities": {"showers": ""}})
        self.assertEqual(entry["facilities"], {"laundry": True})

    def test_emptied_group_is_removed_not_left_blank(self):
        # {} would read as "this entry has an amenities record", which is a
        # different claim from "nobody has looked".
        entry = {"facilities": {"showers": True}}
        cs.apply_update(entry, {"facilities": {"showers": None}})
        self.assertNotIn("facilities", entry)

    def test_whole_group_cleared_by_null(self):
        entry = {"hookups": {"electric": 30, "water": True}}
        cs.apply_update(entry, {"hookups": None})
        self.assertNotIn("hookups", entry)

    def test_nothing_is_invented_for_fields_not_sent(self):
        entry = {}
        cs.apply_update(entry, {"hookups": {"electric": 50}})
        self.assertEqual(entry, {"hookups": {"electric": 50}})


class TestUnknownFieldsAreRefused(unittest.TestCase):
    """Loud failure, because the flat whitelist's quiet one is a known trap."""

    def test_unknown_subkey_raises(self):
        with self.assertRaises(cs.SchemaError) as ctx:
            cs.apply_update({}, {"hookups": {"elektrik": 50}})
        self.assertIn("hookups.elektrik", str(ctx.exception))

    def test_unknown_nested_field_raises(self):
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"fees": {"nonresident": {"typo": 1}}})

    def test_a_refused_write_mutates_nothing(self):
        # Validation runs over the whole payload before anything is applied, so
        # a typo in the last group cannot leave the first one half-written.
        entry = {"hookups": {"electric": 30}}
        with self.assertRaises(cs.SchemaError):
            cs.apply_update(entry, {"hookups": {"electric": 50},
                                    "facilities": {"showerz": True}})
        self.assertEqual(entry, {"hookups": {"electric": 30}})

    def test_non_group_keys_are_left_to_the_flat_whitelist(self):
        entry = {}
        touched = cs.apply_update(entry, {"name": "Somewhere", "phone": "555"})
        self.assertEqual(touched, set())
        self.assertEqual(entry, {})


class TestCoercion(unittest.TestCase):
    """Forms send strings; the store must hold typed values or refuse."""

    def test_string_booleans_and_numbers(self):
        entry = {}
        cs.apply_update(entry, {"hookups": {"electric": "50", "water": "true",
                                            "sewer": "false"}})
        self.assertEqual(entry["hookups"],
                         {"electric": 50, "water": True, "sewer": False})

    def test_ambiguous_boolean_is_refused(self):
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"facilities": {"showers": "maybe"}})

    def test_bool_is_not_accepted_as_a_number(self):
        # bool subclasses int in Python; True must not become 1 amp-service.
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"sites": {"count": True}})

    def test_enum_is_enforced(self):
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"booking": {"fcfs": "sometimes"}})
        entry = {}
        cs.apply_update(entry, {"booking": {"fcfs": "after_cutoff"}})
        self.assertEqual(entry["booking"]["fcfs"], "after_cutoff")

    def test_restricted_int_is_enforced(self):
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"hookups": {"electric": 42}})

    def test_season_dates_are_mmdd(self):
        entry = {}
        cs.apply_update(entry, {"season": {"opens": "04-01", "closes": "10-31"}})
        self.assertEqual(entry["season"], {"opens": "04-01", "closes": "10-31"})
        for bad in ("2026-04-01", "4-1", "13-01", "04-32"):
            with self.assertRaises(cs.SchemaError, msg=bad):
                cs.apply_update({}, {"season": {"opens": bad}})


class TestWorkedCases(unittest.TestCase):
    """The six cases that drove the vocabulary must all still express."""

    def test_indiana_runs_two_minimum_stay_rules_at_once(self):
        # Verified 2026-09-14 against Indiana's CAMPING_BUSINESS_RULES.pdf: two
        # nights on weekends, waived for sites still unrented three days out —
        # but "Required holiday minimum stays are excluded from this relaxed
        # rule", and holiday weekends need three. One rule object cannot hold
        # both, which is why min_stay is a list.
        entry = {}
        cs.apply_update(entry, {"booking": {
            "reserve_until": {"relative_to": "arrival", "at": "23:00"},
            "min_stay": [
                {"nights": 2, "applies": "weekend",
                 "waived_if": {"booking_within_days": 3}},
                {"nights": 3, "applies": "holiday"}]}})
        rules = entry["booking"]["min_stay"]
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]["waived_if"], {"booking_within_days": 3})
        self.assertNotIn("waived_if", rules[1],
                         "the holiday minimum is explicitly NOT waivable")

    def test_an_entrance_fee_is_not_a_camping_surcharge(self):
        # Indiana charges every vehicle to enter and has no non-resident camping
        # rate; New York has the opposite. Conflating them misreports both.
        ind, ny = {}, {}
        cs.apply_update(ind, {"fees": {"entrance": {"resident": 7,
                                                    "nonresident": 15,
                                                    "per": "vehicle_day"}}})
        cs.apply_update(ny, {"fees": {"nonresident": {"type": "surcharge",
                                                      "amount": 5,
                                                      "per": "night"}}})
        self.assertNotIn("nonresident", ind["fees"])
        self.assertNotIn("entrance", ny["fees"])

    def test_iowa_and_maryland_differ_only_in_fcfs(self):
        ia, md = {}, {}
        cs.apply_update(ia, {"booking": {
            "reserve_until": {"relative_to": "arrival", "offset_hours": -48},
            "fcfs": "after_cutoff"}})
        cs.apply_update(md, {"booking": {
            "reserve_until": {"relative_to": "arrival", "at": "14:00"},
            "fcfs": "never"}})
        self.assertNotEqual(ia["booking"]["fcfs"], md["booking"]["fcfs"])

    def test_hither_hills_multiplier_and_indian_island_pass(self):
        hh, ii = {}, {}
        cs.apply_update(hh, {"fees": {"nonresident": {"type": "multiplier",
                                                      "factor": 2.0}}})
        cs.apply_update(ii, {"policy_ref": "local:suffolk-county-ny",
                             "fees": {"prereq_pass": {"name": "Green Key",
                                                      "price": 25,
                                                      "valid": "season"}}})
        self.assertEqual(hh["fees"]["nonresident"]["factor"], 2.0)
        self.assertEqual(ii["policy_ref"], "local:suffolk-county-ny")
        self.assertEqual(ii["fees"]["prereq_pass"]["valid"], "season")

    def test_good_sam_discount_flag(self):
        entry = {}
        cs.apply_update(entry, {"discounts": {"good_sam": True,
                                              "passport_america": False}})
        self.assertEqual(entry["discounts"],
                         {"good_sam": True, "passport_america": False})


class TestRegistryResolution(unittest.TestCase):
    """Inheritance happens on READ. Nothing is copied into an entry."""

    REGISTRY = {
        "state:NY": {"fees": {"nonresident": {"type": "surcharge", "amount": 5,
                                              "per": "stay"}},
                     "booking": {"reservable": True, "fcfs": "never"}},
        "state:IN": {"booking": {"min_stay": {"nights": 2, "applies": "weekend",
                                              "waived_if": {"booking_within_days": 3}}}},
    }

    def test_policy_ref_defaults_to_ownership_and_state(self):
        self.assertEqual(cs.policy_ref({"ownership": "state", "state": "NY"}),
                         "state:NY")

    def test_explicit_policy_ref_wins(self):
        entry = {"ownership": "local", "state": "NY",
                 "policy_ref": "local:suffolk-county-ny"}
        self.assertEqual(cs.policy_ref(entry), "local:suffolk-county-ny")

    def test_the_ref_chain_runs_most_specific_first(self):
        entry = {"ownership": "federal", "state": "VA"}
        self.assertEqual(cs.policy_refs(entry), ["federal:VA", "federal"])
        named = {"ownership": "federal", "state": "ID",
                 "policy_ref": "federal:usfs"}
        self.assertEqual(cs.policy_refs(named),
                         ["federal:usfs", "federal:ID", "federal"])

    def test_ownership_alone_is_what_makes_federal_reachable(self):
        # Federal policy is set per agency, not per state. Without this level a
        # single federal rule would need fifty identical `federal:XX` rows.
        reg = {"federal": {"booking": {"platform": "recreation.gov"}}}
        entry = {"ownership": "federal", "state": "WV"}
        got = cs.resolve(entry, reg)
        self.assertEqual(got["booking"]["values"]["platform"], "recreation.gov")
        self.assertEqual(got["booking"]["scope"], "agency")

    def test_chain_levels_compose_per_field(self):
        # A federal baseline and a named-agency override must merge, not replace
        # each other: usfs keeps the platform it never restated.
        reg = {"federal": {"booking": {"platform": "recreation.gov",
                                       "window_opens_days": 180}},
               "federal:usfs": {"booking": {"window_opens_days": 365}}}
        entry = {"ownership": "federal", "state": "ID",
                 "policy_ref": "federal:usfs"}
        vals = cs.resolve(entry, reg)["booking"]["values"]
        self.assertEqual(vals, {"platform": "recreation.gov",
                                "window_opens_days": 365})

    def test_a_plain_entry_inherits_and_is_marked_agency(self):
        entry = {"ownership": "state", "state": "NY"}
        got = cs.resolve(entry, self.REGISTRY)
        self.assertEqual(got["fees"]["scope"], "agency")
        self.assertEqual(got["fees"]["values"]["nonresident"]["amount"], 5)

    def test_hither_hills_overrides_its_agency_default(self):
        # The case the whole provenance model exists for: 102 NY entries all
        # reading "nominal non-resident fee" would be wrong exactly here.
        entry = {"ownership": "state", "state": "NY",
                 "fees": {"nonresident": {"type": "multiplier", "factor": 2.0}}}
        got = cs.resolve(entry, self.REGISTRY)
        self.assertEqual(got["fees"]["values"]["nonresident"]["type"],
                         "multiplier")
        self.assertEqual(got["fees"]["scope"], "entry")
        self.assertEqual(got["booking"]["scope"], "agency")

    def test_field_scope_distinguishes_verified_from_inherited(self):
        entry = {"ownership": "state", "state": "NY",
                 "fees": {"nightly_low": 20}}
        self.assertEqual(cs.field_scope(entry, "fees", "nightly_low",
                                        self.REGISTRY), "entry")
        self.assertEqual(cs.field_scope(entry, "fees", "nonresident",
                                        self.REGISTRY), "agency")
        self.assertIsNone(cs.field_scope(entry, "season", "opens",
                                         self.REGISTRY))

    def test_unknown_stays_absent_rather_than_defaulting(self):
        entry = {"ownership": "private", "state": "PA"}
        self.assertEqual(cs.resolve(entry, self.REGISTRY), {})

    def test_a_missing_registry_is_normal_not_an_error(self):
        entry = {"ownership": "state", "state": "NY", "hookups": {"electric": 30}}
        got = cs.resolve(entry)
        self.assertEqual(got["hookups"]["scope"], "entry")

    def test_resolution_does_not_mutate_the_entry(self):
        entry = {"ownership": "state", "state": "NY"}
        cs.resolve(entry, self.REGISTRY)
        self.assertEqual(entry, {"ownership": "state", "state": "NY"})


class TestProvenance(unittest.TestCase):
    def test_provenance_is_per_group_and_validated(self):
        entry = {}
        cs.apply_update(entry, {"provenance": {
            "fees": {"source": "https://parks.ny.gov/x", "checked": "2026-09-14"}}})
        self.assertEqual(entry["provenance"]["fees"]["checked"], "2026-09-14")

    def test_provenance_for_an_unknown_group_is_refused(self):
        with self.assertRaises(cs.SchemaError):
            cs.apply_update({}, {"provenance": {"nonsense": {"source": "x"}}})

    def test_derived_method_is_recordable(self):
        entry = {}
        cs.apply_update(entry, {"provenance": {
            "season": {"source": "recreation.gov calendar", "method": "derived"}}})
        self.assertEqual(entry["provenance"]["season"]["method"], "derived")


if __name__ == "__main__":
    unittest.main()


class TestManageFormPayload(unittest.TestCase):
    """The shape the manage form actually sends.

    It renders the WHOLE vocabulary and sends every control it drew, with blank
    meaning unknown -> null. That is only safe because null CLEARS rather than
    stores: a form that sent `false` for blank would, on one unrelated save,
    convert an entry's unknowns into twelve thousand confident negatives.
    """

    def _form_payload(self, **set_values):
        """Every field of every group, null unless named — what the form posts."""
        payload = {}
        for group, fields in cs.SCHEMA.items():
            payload[group] = {key: set_values.get(f"{group}.{key}")
                              for key in fields}
        return payload

    def test_a_blank_form_clears_rather_than_populating(self):
        entry = {"hookups": {"electric": 30}, "discounts": {"good_sam": True}}
        cs.apply_update(entry, self._form_payload())
        self.assertEqual(entry, {})

    def test_one_set_field_survives_and_the_rest_clear(self):
        entry = {}
        cs.apply_update(entry, self._form_payload(**{"hookups.electric": 50}))
        self.assertEqual(entry, {"hookups": {"electric": 50}})

    def test_an_unrendered_group_is_left_alone(self):
        # A stale tab whose schema predates a new group must not clear it.
        entry = {"discounts": {"good_sam": True}, "hookups": {"electric": 30}}
        payload = self._form_payload(**{"hookups.electric": 50})
        del payload["discounts"]
        cs.apply_update(entry, payload)
        self.assertEqual(entry["discounts"], {"good_sam": True})

    def test_explicit_no_is_preserved_through_a_full_form_save(self):
        entry = {}
        cs.apply_update(entry, self._form_payload(**{"facilities.showers": False,
                                                     "hookups.electric": 0}))
        self.assertEqual(entry, {"facilities": {"showers": False},
                                 "hookups": {"electric": 0}})


class TestShippedRegistry(unittest.TestCase):
    """The committed registry must parse against the vocabulary it claims.

    A malformed row is not a local error: inheritance is invisible in the
    entries themselves, so a bad `state:IN` row would hand a wrong booking rule
    to all 41 Indiana state parks with nothing on any entry to show for it.
    """

    def setUp(self):
        import json
        import os
        path = os.path.join(os.path.dirname(__file__), os.pardir,
                            "campground_policies.json")
        if not os.path.exists(path):
            self.skipTest("campground_policies.json not present")
        with open(path) as f:
            self.rows = json.load(f)

    def test_every_row_validates(self):
        for ref, row in self.rows.items():
            with self.subTest(ref=ref):
                cs.validate_row(row, ref)

    def test_no_row_invents_an_unconfirmed_cutoff(self):
        # Maryland publishes a 5pm same-day cutoff but only for "a limited
        # number of parks" and does not say which, so the agency row carries no
        # reserve_until: applying it to all of Maryland would claim same-day
        # booking at parks that do not offer it.
        md = self.rows.get("state:MD", {}).get("booking", {})
        self.assertNotIn("reserve_until", md)
        self.assertIn("note", md)

        # Iowa's two official pages contradict each other on the cutoff (2 days
        # prior vs up to the day of arrival). Unresolved stays unwritten.
        ia = self.rows.get("state:IA", {}).get("booking", {})
        self.assertNotIn("reserve_until", ia)
        self.assertNotIn("fcfs", ia,
                         "Iowa's post-cutoff FCFS is not confirmed by any "
                         "official source")

    def test_the_two_verified_entry_overrides_beat_their_agency_row(self):
        """Hither Hills and Indian Island, against the real files.

        These are the cases the inherited/verified split exists for. If either
        silently started inheriting its agency default, the failure would be
        invisible in the entry itself — which is exactly why it is pinned here.
        """
        import json
        import os
        cg = os.path.join(os.path.dirname(__file__), os.pardir,
                          "campgrounds.json")
        with open(cg) as f:
            by_id = {e["id"]: e for e in json.load(f)}

        # Hither Hills doubles the nightly rate for non-residents; the rest of
        # the NY system charges a flat $5/night. Inheriting would understate a
        # weekend night by $32.
        hh = by_id[291]
        self.assertEqual(cs.policy_ref(hh), "state:NY")
        fees = cs.resolve(hh, self.rows)["fees"]["values"]
        self.assertEqual(fees["nonresident"],
                         {"type": "multiplier", "factor": 2.0})
        self.assertEqual(cs.field_scope(hh, "fees", "nonresident", self.rows),
                         "entry")
        ny = self.rows["state:NY"]["fees"]["nonresident"]
        self.assertEqual(ny["type"], "surcharge",
                         "the agency default must still be the $5 surcharge")

        # Indian Island is a COUNTY park in a state whose default row is for
        # state parks, so it must not fall through to state:NY.
        ii = by_id[1448]
        self.assertEqual(cs.policy_ref(ii), "local:suffolk-county-ny")
        ii_fees = cs.resolve(ii, self.rows)["fees"]["values"]
        self.assertEqual(ii_fees["prereq_pass"]["price"], 50)
        self.assertEqual(ii_fees["prereq_pass"]["valid"], "year")

    def test_the_federal_row_withholds_what_varies_per_facility(self):
        # The most expensive possible default in the registry: 3,738 entries.
        # FCFS and minimum stay vary campground by campground on federal land,
        # so defaulting either would be wrong at scale and invisibly so.
        fed = self.rows["federal"]["booking"]
        self.assertNotIn("fcfs", fed)
        self.assertNotIn("min_stay", fed)

    def test_base_rates_are_the_resident_price(self):
        # nightly_low/high must be comparable between agencies, so they hold the
        # resident base and every modifier applies on top. Storing the
        # non-resident price would double-count against the multiplier.
        hh = self.rows.get("state:NY")
        suffolk = self.rows["local:suffolk-county-ny"]["fees"]
        self.assertEqual(suffolk["nightly_high"], 18,
                         "Suffolk's in-season RESIDENT rate, not the $36 "
                         "non-resident one")

    def test_entrance_fees_keep_their_period(self):
        """`per` matters as much as the amount, and they differ per agency."""
        ind = self.rows["state:IN"]["fees"]["entrance"]
        mich = self.rows["state:MI"]["fees"]["entrance"]
        # Indiana: once per camping stay (the hang-tag rule, confirmed
        # firsthand). Michigan: an annual vehicle passport. Same field, and a
        # cost estimate that ignored `per` would be wrong in both directions.
        self.assertEqual(ind["per"], "vehicle_stay")
        self.assertEqual(mich["per"], "vehicle_year")
        self.assertGreater(mich["nonresident"], mich["resident"])
        self.assertGreater(ind["nonresident"], ind["resident"])

    def test_secondary_sources_are_stamped_as_reported(self):
        """A row read off a search summary must not look hand-verified.

        Florida's site returns 403 to automated fetches, so its figures come
        from summaries of the page rather than the page. Without the `reported`
        method that row is indistinguishable from one nobody bothered to stamp.
        """
        fl = self.rows["state:FL"]["provenance"]["booking"]
        self.assertEqual(fl.get("method"), "reported")
        self.assertIn("403", fl["source"])

    def test_no_row_claims_a_minimum_stay_it_cannot_waive_correctly(self):
        # Indiana's waiver does NOT cover its holiday rule; North Carolina's
        # does, because the holiday rule is its only one. Both must survive.
        ind = self.rows["state:IN"]["booking"]["min_stay"]
        self.assertEqual(len(ind), 2)
        self.assertNotIn("waived_if", ind[1])
        nc = self.rows["state:NC"]["booking"]["min_stay"]
        self.assertEqual(nc[0]["applies"], "holiday")
        self.assertEqual(nc[0]["waived_if"]["booking_within_days"], 7)

    def test_verified_rows_cite_a_real_source_url(self):
        for ref, row in self.rows.items():
            for group, prov in (row.get("provenance") or {}).items():
                with self.subTest(ref=ref, group=group):
                    self.assertIn("http", prov.get("source", ""),
                                  "a verified row must cite the page it came from")

    def test_unverified_rows_say_so_in_provenance(self):
        for ref, row in self.rows.items():
            for group, prov in (row.get("provenance") or {}).items():
                with self.subTest(ref=ref, group=group):
                    self.assertTrue((prov.get("source") or "").strip(),
                                    "a registry row must name its source")
