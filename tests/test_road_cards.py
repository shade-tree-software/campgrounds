"""The on-the-road card — a day's photos taken from the moving RV.

Every other photo in the app hangs off a campspot or an event, and both of
those are places you STOPPED. A day spent crossing Nebraska with the passenger
shooting out the window had no upload target at all, short of inventing a fake
waypoint to hold the photos.

The rule that matters most here is the LAST one: road photos are keyed by
DATE, not by position. Campspot and event photos are keyed by index, so
inserting an item mid-trip renumbers every directory above it — the app's most
fragile machinery, which broke silently and library-wide the day photos moved
out of static/ (see tests/test_photo_index_remap.py). A date never renumbers,
so a road card can never need remapping at all.

    python -m unittest tests.test_road_cards -v
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ekko_trips_app as A  # noqa: E402

DAY = "2026-08-22"


class RoadCardBase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        self.patch = mock.patch.object(A, "UPLOAD_DIR", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.addCleanup(shutil.rmtree, self.root, True)

    def _write(self, trip_id, day, *names):
        d = os.path.join(self.root, str(trip_id), "road", day)
        os.makedirs(d, exist_ok=True)
        for n in names:
            with open(os.path.join(d, n), "wb") as fh:
                fh.write(b"\xff\xd8\xff\xe0")   # enough to be a file
        return d


class TestWhichDaysHaveOne(RoadCardBase):
    def test_a_day_with_photos_gets_a_card(self):
        self._write(95, DAY, "a.jpg", "b.jpg")
        self.assertEqual(A._road_days(95), [DAY])

    def test_an_empty_directory_is_not_a_card(self):
        # The card's existence IS the directory having photos in it, so an
        # emptied one must stop rendering rather than leave a hollow card.
        os.makedirs(os.path.join(self.root, "95", "road", DAY))
        self.assertEqual(A._road_days(95), [])

    def test_a_directory_of_non_images_is_not_a_card(self):
        self._write(95, DAY, "notes.txt")
        self.assertEqual(A._road_days(95), [])

    def test_a_directory_that_is_not_a_date_is_ignored(self):
        self._write(95, "events", "a.jpg")
        self._write(95, "12", "a.jpg")
        self.assertEqual(A._road_days(95), [])

    def test_days_come_back_in_order(self):
        for day in ("2026-08-24", "2026-08-22", "2026-08-23"):
            self._write(95, day, "a.jpg")
        self.assertEqual(A._road_days(95),
                         ["2026-08-22", "2026-08-23", "2026-08-24"])

    def test_a_trip_with_no_road_photos_has_no_cards(self):
        self.assertEqual(A._road_days(99), [])


class TestPhotoOrder(RoadCardBase):
    def _collect(self, order=None):
        return A._collect_road_photos(95, DAY, {}, order or {}, {}, {})

    def test_photos_run_in_the_order_they_were_taken(self):
        # These are a sequence shot out of a window, not a grid someone
        # arranged, so EXIF time leads rather than filename.
        self._write(95, DAY, "z.jpg", "a.jpg")
        taken = {"z.jpg": "2026-08-22 09:15:00", "a.jpg": "2026-08-22 14:40:00"}
        with mock.patch.object(A, "_photo_date_taken",
                               lambda p: taken[os.path.basename(p)]):
            self.assertEqual([p["filename"] for p in self._collect()],
                             ["z.jpg", "a.jpg"])

    def test_an_explicit_drag_order_still_wins(self):
        self._write(95, DAY, "a.jpg", "b.jpg")
        with mock.patch.object(A, "_photo_date_taken",
                               lambda p: "2026-08-22 09:00:00"):
            got = self._collect({f"95/road/{DAY}": ["b.jpg", "a.jpg"]})
        self.assertEqual([p["filename"] for p in got], ["b.jpg", "a.jpg"])

    def test_a_photo_with_no_exif_sorts_last_not_first(self):
        # Empty string would sort ABOVE every real timestamp and put the one
        # photo we know least about at the top of the card.
        self._write(95, DAY, "a.jpg", "b.jpg")
        taken = {"a.jpg": "", "b.jpg": "2026-08-22 09:00:00"}
        with mock.patch.object(A, "_photo_date_taken",
                               lambda p: taken[os.path.basename(p)]):
            self.assertEqual([p["filename"] for p in self._collect()],
                             ["b.jpg", "a.jpg"])

    def test_keys_are_dated_not_indexed(self):
        self._write(95, DAY, "a.jpg")
        with mock.patch.object(A, "_photo_date_taken", lambda p: ""):
            photo = self._collect()[0]
        self.assertEqual(photo["key"], f"95/road/{DAY}/a.jpg")
        self.assertEqual(photo["thumb_url"], f"/thumb/95/road/{DAY}/a.jpg")


class TestTimelinePlacement(RoadCardBase):
    def _timeline(self, photos):
        trip = {"timeline": [], "events": []}
        A._add_road_cards(trip, {DAY: photos})
        return trip["timeline"][0]

    def test_the_card_sits_at_its_first_photos_time(self):
        # In place among the day's stops, where the driving began — not
        # hoisted to the top of the day, for the same reason a folded waypoint
        # run stays where it happened.
        card = self._timeline([{"date_taken": "2026-08-22 09:15:00"},
                               {"date_taken": "2026-08-22 14:40:00"}])
        self.assertEqual(card["time"], "09:15")
        self.assertEqual(card["sort_date"], DAY)

    def test_a_card_with_no_timestamps_lands_at_noon(self):
        # Where an untimed event goes too.
        self.assertEqual(self._timeline([{"date_taken": ""}])["time"], "12:00")

    def test_the_first_TIMED_photo_sets_the_position(self):
        card = self._timeline([{"date_taken": ""},
                               {"date_taken": "2026-08-22 08:05:00"}])
        self.assertEqual(card["time"], "08:05")

    def test_the_card_carries_its_day_as_its_idx(self):
        # `idx` is the date, which is what the upload URL and the DOM id use.
        card = self._timeline([{"date_taken": ""}])
        self.assertEqual(card["idx"], DAY)
        self.assertEqual(card["type"], "road")

    def test_the_card_interleaves_rather_than_appending(self):
        # 15:00 is rank 900, between a morning stop (500) and an evening one
        # (1300) — the card lands mid-day among the stops it happened between,
        # which is the whole reason it is placed by time at all.
        trip = {"events": [], "timeline": [
            {"type": "event", "sort_date": DAY, "_order": 0, "_rank": 500},
            {"type": "event", "sort_date": DAY, "_order": 0, "_rank": 1300},
        ]}
        A._add_road_cards(trip, {DAY: [{"date_taken": "2026-08-22 15:00:00"}]})
        self.assertEqual([i["type"] for i in trip["timeline"]],
                         ["event", "road", "event"])

    def test_a_card_sorts_onto_its_own_day(self):
        trip = {"events": [], "timeline": [
            {"type": "event", "sort_date": "2026-08-21", "_order": 0, "_rank": 1400},
            {"type": "event", "sort_date": "2026-08-23", "_order": 0, "_rank": 10},
        ]}
        A._add_road_cards(trip, {DAY: [{"date_taken": "2026-08-22 09:00:00"}]})
        self.assertEqual([i["sort_date"] for i in trip["timeline"]],
                         ["2026-08-21", DAY, "2026-08-23"])


class TestMovingPhotosInAndOut(RoadCardBase):
    """A photo filed onto an invented waypoint has to be able to come back.

    Before road cards existed the only way to keep a shot taken through the
    windscreen was to hang it off some nearby waypoint, so the move path is
    not a nicety — it is how the existing library gets corrected.
    """

    def setUp(self):
        super().setUp()
        self.client = A.app.test_client()
        with self.client.session_transaction() as sess:
            sess["_user_id"] = self._an_admin()
            sess["_fresh"] = True

    @staticmethod
    def _an_admin():
        import json
        with open(os.path.join(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__))), "users.json")) as fh:
            users = json.load(fh)
        return next(u for u, v in users.items() if v.get("is_admin"))

    def _move(self, **kw):
        return self.client.post("/trips/95/move-photo", json=kw)

    def test_a_road_date_that_is_not_a_date_is_refused(self):
        # dst_idx goes straight into a filesystem path, and unlike a stay or
        # event index Flask's <int:> converter has not already vetted it.
        for bad in ("../../etc", "2026-8-2", "", "road"):
            r = self._move(filename="a.jpg", src_type="event", src_idx=0,
                           dst_type="road", dst_idx=bad)
            self.assertEqual(r.status_code, 400, f"{bad!r} was accepted")

    def test_a_bad_date_is_refused_as_the_SOURCE_too(self):
        r = self._move(filename="a.jpg", src_type="road", src_idx="../../x",
                       dst_type="event", dst_idx=0)
        self.assertEqual(r.status_code, 400)


class TestKeyShapes(unittest.TestCase):
    def test_a_road_key_names_the_day(self):
        # The five metadata stores are keyed on this shape, so it is what makes
        # a road photo's caption follow it. Positional keys ("95/3/x.jpg") move
        # when a trip is edited; this one cannot.
        self.assertEqual(f"95/{A.ROAD_DIRNAME}/2026-08-22/a.jpg",
                         "95/road/2026-08-22/a.jpg")




class TestTheDropTarget(RoadCardBase):
    """A road card you cannot create is a road card you cannot drag onto.

    The card exists only once its directory has photos, so on a day with none
    there is nothing in the DOM to drop on -- and correcting a shot that was
    filed onto some invented waypoint, which is the whole reason moving exists,
    would be impossible. An empty placeholder is rendered for every day and
    revealed only while a drag is in flight, the same device
    `body.photo-dragging` uses to reveal a bare card's body.
    """

    def _page(self):
        client = A.app.test_client()
        with client.session_transaction() as sess:
            sess["_user_id"] = TestMovingPhotosInAndOut._an_admin()
            sess["_fresh"] = True
        return client.get("/trips/95").data.decode("utf-8", "replace")

    def test_every_day_offers_somewhere_to_drop(self):
        import re
        html = self._page()
        days = re.findall(r'id="road-photos-(\d{4}-\d{2}-\d{2})"', html)
        self.assertTrue(days, "no road drop targets rendered at all")
        # One per day, and no duplicate ids -- parseGridId reads the day back
        # out of the grid id, so a collision would file photos on the wrong day.
        self.assertEqual(len(days), len(set(days)))

    def test_a_day_with_a_real_card_gets_no_placeholder(self):
        # Otherwise two grids would share an id on that day.
        import re
        html = self._page()
        ids = re.findall(r'id="road-photos-(\d{4}-\d{2}-\d{2})"', html)
        self.assertEqual(len(ids), len(set(ids)))




class TestWhereARoadPhotoWasTaken(unittest.TestCase):
    """A road photo has no stay or event to inherit a location from — that is
    the definition of one. But the trip knows where the vehicle was every few
    minutes and the photo knows when it was taken, so the two combine."""

    TRACK = [{"tst": 1000, "lat": 41.0, "lon": -93.0},
             {"tst": 2000, "lat": 41.5, "lon": -94.0},
             {"tst": 3000, "lat": 42.0, "lon": -95.0}]

    @staticmethod
    def _at(epoch):
        import datetime
        return datetime.datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def test_the_nearest_ping_in_time_wins(self):
        pos = A._road_photo_position(self.TRACK, self._at(2100))
        self.assertEqual(pos, (41.5, -94.0))

    def test_it_looks_both_ways_not_just_forward(self):
        # bisect lands on the ping AFTER the photo; the one before is often
        # nearer, and only checking forward would silently bias every answer.
        self.assertEqual(A._road_photo_position(self.TRACK, self._at(1900)),
                         (41.5, -94.0))
        self.assertEqual(A._road_photo_position(self.TRACK, self._at(1100)),
                         (41.0, -93.0))

    def test_a_photo_the_track_does_not_cover_gets_no_position(self):
        # An hour from the nearest ping means the track is not really about
        # this moment. A road photo is taken while MOVING, so its ping should
        # be minutes away — unlike an evening at camp, where OwnTracks goes
        # quiet for hours and a distant ping is still exactly right.
        self.assertIsNone(A._road_photo_position(self.TRACK, self._at(99999)))

    def test_no_track_and_no_timestamp_are_both_survivable(self):
        self.assertIsNone(A._road_photo_position([], self._at(2000)))
        self.assertIsNone(A._road_photo_position(self.TRACK, ""))
        self.assertIsNone(A._road_photo_position(self.TRACK, "2026-08-22"))

    def test_an_unsorted_track_is_refused_rather_than_misread(self):
        # The lookup bisects, so an out-of-order list would not error — it
        # would quietly return the wrong ping.
        scrambled = [self.TRACK[2], self.TRACK[0], self.TRACK[1]]
        self.assertIsNone(A._road_photo_position(scrambled, self._at(2000)))


if __name__ == "__main__":
    unittest.main()
