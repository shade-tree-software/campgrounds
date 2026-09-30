"""Campspot arrival times, and the Arrived at / Back at / Departed rows.

The campspot card stays the LAST card of its day and carries the time they got
back to it for the night; every other coming and going becomes a one-line row
in its own slot (AWH 2026-09-30). The rules pinned here are the ones the real
trips forced:

  - a return is shown only when something on the timeline happened while
    away, and an outing timed a few minutes before the phone left still counts
    (trip 91's paddle starts 18:25, the phone leaves camp at 18:30);
  - only the FINAL departure gets a row, because an earlier one is the start
    of an outing the next card already describes, and it is where overnight
    GPS silence bites (trip 96's "left camp" would be the previous evening);
  - a time bounded by a long silence is left blank, never printed as if it
    were the answer (trip 92 got back to the Svendsens during a 2h46m gap).

Synthetic trips throughout, so nothing depends on a host's track cache.

    python -m unittest tests.test_campspot_rows -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402
from trips import event_time_rank  # noqa: E402

TZ = "America/New_York"
CAMP = (40.0, -75.0)
AWAY = (40.1, -75.3)       # ~27 km off: somewhere the outings happen


def T(day, clock):
    return A._trip_local_to_tst(day, clock, TZ)


def _stay(start, end, cid=1, place="Test Camp", coords=CAMP):
    return {"start": start, "end": end, "campground_id": cid, "place": place,
            "lat": coords[0], "lng": coords[1]}


def _card(idx, day):
    return {"type": "stay", "idx": idx, "sort_date": day, "_order": 1,
            "_rank": event_time_rank(day, "23:59", "", TZ)}


def _event(day, clock, name="Outing"):
    return {"type": "event", "date": day, "time": clock, "tz": TZ,
            "name": name, "sort_date": day, "_order": 0,
            "_rank": event_time_rank(day, clock, TZ, TZ)}


def _trip(stays, cards, events):
    return {"stays": stays, "timeline": cards + events}


def _visits(*spans, quiet=60):
    """`spans` as (day_a, clock_a, day_b, clock_b); both silences `quiet` s."""
    return {"0": {"tz": TZ, "visits": [
        [T(da, ca), T(db, cb), quiet, quiet] for da, ca, db, cb in spans]}}


def _rows(trip):
    return [(i["camp_kind"], i["sort_date"], i["time"], i["duration"])
            for i in trip["timeline"] if i["type"] == "camp"]


def _card_time(trip, day):
    return next(i for i in trip["timeline"]
                if i["type"] == "stay" and i["sort_date"] == day).get("arrive_time")


def _returns(trip):
    """The rows other than the final departure, for tests about returns."""
    return [r for r in _rows(trip) if r[0] != "departed"]


class TestTheDaysShape(unittest.TestCase):
    """Trip 92's first two days, reduced to their bones."""

    def setUp(self):
        self.trip = _trip(
            [_stay("2026-07-03", "2026-07-05")],
            [_card(0, "2026-07-03"), _card(0, "2026-07-04")],
            [_event("2026-07-03", "21:03", "Fireworks"),
             _event("2026-07-04", "10:28", "Parade"),
             _event("2026-07-04", "17:54", "Concert")])
        A._add_campspot_rows(self.trip, _visits(
            ("2026-07-03", "17:53", "2026-07-03", "20:25"),
            ("2026-07-03", "21:55", "2026-07-04", "10:02"),
            ("2026-07-04", "14:33", "2026-07-04", "16:51"),
            ("2026-07-04", "22:10", "2026-07-05", "11:31")), TZ)

    def test_first_arrival_then_return_then_departure(self):
        self.assertEqual(_rows(self.trip), [
            ("arrived", "2026-07-03", "17:53", "2h 32m"),
            ("back", "2026-07-04", "14:33", "2h 18m"),
            ("departed", "2026-07-05", "11:31", ""),
        ])

    def test_each_card_carries_the_nights_return(self):
        cards = [i for i in self.trip["timeline"] if i["type"] == "stay"]
        self.assertEqual([c.get("arrive_time") for c in cards],
                         ["21:55", "22:10"])

    def test_the_card_is_the_last_thing_in_its_day(self):
        for day in ("2026-07-03", "2026-07-04"):
            items = [i for i in self.trip["timeline"] if i["sort_date"] == day]
            self.assertEqual(items[-1]["type"], "stay", day)

    def test_rows_sit_between_the_outings(self):
        order = [(i["type"], i.get("camp_kind") or i.get("name"))
                 for i in self.trip["timeline"]
                 if i["sort_date"] == "2026-07-04"]
        self.assertEqual(order, [("event", "Parade"), ("camp", "back"),
                                 ("event", "Concert"), ("stay", None)])


class TestRowNotes(unittest.TestCase):
    """Notes typed on Arrived / Back at rows, keyed per campspot and day."""

    def _run(self, notes=None):
        trip = _trip(
            [_stay("2026-07-03", "2026-07-05")],
            [_card(0, "2026-07-03"), _card(0, "2026-07-04")],
            [_event("2026-07-03", "21:03", "Fireworks"),
             _event("2026-07-04", "10:28", "Parade"),
             _event("2026-07-04", "15:30", "Pool"),
             _event("2026-07-04", "19:54", "Concert")])
        A._add_campspot_rows(trip, _visits(
            ("2026-07-03", "17:53", "2026-07-03", "20:25"),
            ("2026-07-03", "21:55", "2026-07-04", "10:02"),
            ("2026-07-04", "14:33", "2026-07-04", "15:00"),
            ("2026-07-04", "16:00", "2026-07-04", "19:00"),
            ("2026-07-04", "22:10", "2026-07-05", "11:31")), TZ, notes)
        return [i for i in trip["timeline"] if i["type"] == "camp"]

    def test_keys_count_rows_per_day(self):
        rows = self._run()
        self.assertEqual([(r["camp_kind"], r.get("note_key")) for r in rows], [
            ("arrived", "2026-07-03#1"),
            ("back", "2026-07-04#1"),
            ("back", "2026-07-04#2"),
            ("departed", None),
        ])
        self.assertTrue(all(r.get("note_stay") == 0 for r in rows[:3]))

    def test_note_lands_on_its_row(self):
        rows = self._run({0: {"2026-07-04#2": "Dinner and showers"}})
        self.assertEqual([r.get("note") for r in rows[:3]],
                         ["", "", "Dinner and showers"])


class TestWhatCountsAsAnOuting(unittest.TestCase):
    def _run(self, events):
        trip = _trip([_stay("2026-06-26", "2026-06-28")],
                     [_card(0, "2026-06-26"), _card(0, "2026-06-27")], events)
        A._add_campspot_rows(trip, _visits(
            ("2026-06-26", "20:41", "2026-06-27", "13:00"),
            ("2026-06-27", "13:40", "2026-06-27", "18:30"),
            ("2026-06-27", "18:57", "2026-06-28", "07:29")), TZ)
        return trip

    def test_an_empty_absence_is_merged_away(self):
        # A walk to the bathhouse, a GPS flicker: nothing to come back from.
        trip = self._run([])
        self.assertEqual(_returns(trip), [])
        self.assertEqual(_card_time(trip, "2026-06-26"), "20:41")
        # The merged visit spans the whole day, so the night card on the 27th
        # has no return of its own to show.
        self.assertIsNone(_card_time(trip, "2026-06-27"))

    def test_an_outing_logged_just_before_the_phone_left_counts(self):
        trip = self._run([_event("2026-06-27", "13:05"),   # during absence
                          _event("2026-06-27", "18:25")])  # 5 min early
        self.assertEqual([r[0] for r in _returns(trip)], ["back"])
        self.assertEqual(_card_time(trip, "2026-06-27"), "18:57")

    def test_but_not_one_long_before(self):
        trip = self._run([_event("2026-06-27", "13:05"),
                          _event("2026-06-27", "17:00")])  # 90 min early
        self.assertEqual(_returns(trip), [])


class TestDepartures(unittest.TestCase):
    def _trip(self, events=()):
        return _trip([_stay("2026-07-05", "2026-07-06")],
                     [_card(0, "2026-07-05")], list(events))

    def test_only_the_final_departure_gets_a_row(self):
        # Kayak from camp in the morning, back, then leave for good.
        trip = self._trip([_event("2026-07-06", "08:58", "Kayak")])
        A._add_campspot_rows(trip, _visits(
            ("2026-07-05", "18:32", "2026-07-06", "07:28"),
            ("2026-07-06", "09:17", "2026-07-06", "11:45")), TZ)
        # And the return carries no duration: the Departed row says it.
        self.assertEqual(_rows(trip), [
            ("back", "2026-07-06", "09:17", ""),
            ("departed", "2026-07-06", "11:45", ""),
        ])

    def test_a_departure_bounded_by_silence_is_left_out(self):
        trip = self._trip()
        visits = _visits(("2026-07-05", "18:32", "2026-07-06", "09:20"))
        visits["0"]["visits"][0][3] = 108 * 60     # next ping 108 min later
        A._add_campspot_rows(trip, visits, TZ)
        self.assertEqual(_rows(trip), [])

    def test_a_departure_on_the_wrong_day_is_left_out(self):
        # Last ping at camp the night BEFORE check-out (then silence).
        trip = self._trip()
        A._add_campspot_rows(trip, _visits(
            ("2026-07-05", "18:32", "2026-07-05", "21:31")), TZ)
        self.assertNotIn("departed", [r[0] for r in _rows(trip)])


class TestSilence(unittest.TestCase):
    def test_an_arrival_after_a_long_silence_has_no_time(self):
        trip = _trip([_stay("2026-07-03", "2026-07-04")],
                     [_card(0, "2026-07-03")],
                     [_event("2026-07-03", "21:03")])
        visits = _visits(("2026-07-03", "17:53", "2026-07-03", "20:25"),
                         ("2026-07-03", "23:52", "2026-07-04", "10:02"))
        visits["0"]["visits"][1][2] = 166 * 60
        A._add_campspot_rows(trip, visits, TZ)
        card = next(i for i in trip["timeline"] if i["type"] == "stay")
        self.assertIsNone(card.get("arrive_time"))

    def test_a_row_after_a_long_silence_keeps_its_place_without_a_time(self):
        trip = _trip([_stay("2026-06-26", "2026-06-28")],
                     [_card(0, "2026-06-26"), _card(0, "2026-06-27")],
                     [_event("2026-06-27", "08:22"),
                      _event("2026-06-27", "10:35")])
        visits = _visits(("2026-06-26", "20:41", "2026-06-27", "08:22"),
                         ("2026-06-27", "10:06", "2026-06-27", "10:34"),
                         ("2026-06-27", "13:08", "2026-06-28", "07:29"))
        visits["0"]["visits"][1][2] = 73 * 60      # quiet on the lake
        A._add_campspot_rows(trip, visits, TZ)
        self.assertEqual(_returns(trip), [("back", "2026-06-27", "", "")])
        order = [i.get("time") for i in trip["timeline"]
                 if i["sort_date"] == "2026-06-27" and i["type"] != "stay"]
        self.assertEqual(order, ["08:22", "", "10:35"])


class TestSameMinute(unittest.TestCase):
    def test_arriving_comes_before_what_was_done_on_arrival(self):
        trip = _trip([_stay("2023-08-25", "2023-08-26")],
                     [_card(0, "2023-08-25")],
                     [_event("2023-08-25", "15:26", "Check-in"),
                      _event("2023-08-25", "18:00", "Dinner out")])
        A._add_campspot_rows(trip, _visits(
            ("2023-08-25", "15:26", "2023-08-25", "17:39"),
            ("2023-08-25", "19:10", "2023-08-26", "09:00")), TZ)
        names = [i.get("camp_kind") or i.get("name")
                 for i in trip["timeline"] if i["type"] != "stay"]
        self.assertEqual(names[:2], ["arrived", "Check-in"])


class TestVisitsAreCountedPerVisitNotPerRecord(unittest.TestCase):
    def test_a_site_move_does_not_report_every_return_twice(self):
        # Two records, one campground, sites ~150 m apart (trip 96's move).
        site_b = (CAMP[0] + 0.00135, CAMP[1])
        trip = {"stays": [_stay("2026-09-11", "2026-09-12"),
                          _stay("2026-09-12", "2026-09-13", coords=site_b)],
                "events": []}
        day = "2026-09-12"
        pings = ([{"tst": T(day, "08:00") + 60 * m, "lat": CAMP[0],
                   "lon": CAMP[1]} for m in range(0, 30, 5)]
                 + [{"tst": T(day, "09:00") + 60 * m, "lat": AWAY[0],
                     "lon": AWAY[1]} for m in range(0, 60, 5)]
                 + [{"tst": T(day, "10:30") + 60 * m, "lat": CAMP[0],
                     "lon": CAMP[1]} for m in range(0, 30, 5)])
        out = A._campspot_visits(trip, pings)
        self.assertEqual(list(out), ["0"])
        visits = out["0"]["visits"]
        self.assertEqual(len(visits), 2)
        # Silence before the return: last away ping 09:55, back at 10:30.
        self.assertEqual(visits[1][2], 35 * 60)


if __name__ == "__main__":
    unittest.main()
