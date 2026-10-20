#!/usr/bin/env python3
"""Wisconsin DNR state parks and forests: season from the camping pages (2026-10-20).

    python3 -I audit/season_dates/wi.py [--apply]

dnr.wisconsin.gov/topic/<park>/recreation/camping says, campground by campground, when it
is open ("open April 30 to Columbus Day"), or that some sites are plowed for winter camping.
A plowed winter campground is year-round. Holiday-anchored edges take the widest date
(common.py): the Thursday before Memorial Day is May 21, Labor Day Sept 7, Columbus Day
Oct 14, the Monday after the second weekend of October Oct 16; the note quotes the DNR.

Not written, because the page names no season: Amnicon Falls, Brunet Island, Lake Wissota,
Merrick, Nelson Dewey, New Glarus Woods, Pattison, Wyalusing, Yellowstone Lake, Willow River,
Richard Bong, Lake Kegonsa, High Cliff, Wildcat Mountain, Buckhorn, Governor Thompson,
Potawatomi, Point Beach, Brule River, Governor Knowles, the Peninsula campgrounds other
than Tennison Bay, and Governor Dodge (39 winter sites, but the page doesn't say which
campground).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run  # noqa: E402

D = "https://dnr.wisconsin.gov/topic/{}"
R = " ('{}'), read 2026-10-20"
NHAL_M = D.format("StateForests/nhal/recreation/camping/modern")
NHAL_R = D.format("StateForests/nhal/recreation/camping/rustic")


def src(path, head):
    return (path if path.startswith("http") else D.format(path)) + R.format(head)


def sea(opens, closes, note=None):
    d = {"year_round": False, "opens": opens, "closes": closes}
    if note:
        d["note"] = note
    return d


MEM_LAB = "Approximate: the DNR says the Thursday before Memorial Day to Labor Day."
MEM_OCT = "Approximate: the DNR says the Thursday before Memorial Day to Oct. 1."
APR_COL = "Approximate: the DNR says April 30 to Columbus Day."

DECISIONS = {
    293: ({"year_round": True, "note": "Quartzite campground is open year-round; Northern Lights and Ice Age typically close in October and reopen around April."},
          src("parks/devilslake/recreation/camping", "Devil's Lake campgrounds")),
    450: ({"year_round": True, "note": "Winter camping by reservation, with electric hookups; water at the well house. The dump station is open May through October."},
          src("parks/peninsula/recreation/camping", "Winter Camping")),
    573: ({"year_round": True, "note": "Showers, flush toilets and laundry in the warm-weather season only."},
          src("parks/kohlerandrae/recreation/camping", "Family campground")),
    3263: ({"year_round": True, "note": "Part of the campground is open year-round."},
           src("parks/bluemound/recreation/camping", "Winter camping")),
    3298: ({"year_round": True, "note": "In winter, five plowed electric sites (26-30) by reservation only."},
           src("parks/bigbay/recreation/camping", "Winter Camping")),
    3299: ({"year_round": True, "note": "In winter, six plowed sites (1-6) by reservation only."},
           src("parks/copperfalls/recreation/camping", "Winter camping")),
    3279: ({"year_round": True}, src("parks/kmn/recreation/camping", "Mauthe Lake campground")),
    3280: (sea("05-01", "10-15", "Approximate: the DNR says the first weekend in May through mid-October."),
           src("parks/kmn/recreation/camping", "Long Lake campground")),
    3322: (sea("05-01", "10-16", "Approximate: the DNR says May 1 through the Monday after the second weekend of October."),
           src("StateForests/blackriver/recreation/camping", "East Fork campground")),
    3318: (sea("05-01", "10-31", "Approximate: the DNR says May to October."),
           src("StateForests/flambeauriver/recreation/camping", "Connors Lake Campground")),
    14022: (sea("04-27", "11-30"), src("StateForests/govearl/recreation/camping", "Old Veteran's Lake")),
    3314: ({"year_round": True, "note": "Winter access is limited: the road to sites 701-724 is plowed as staffing allows, and only the driveways of sites 701-703."},
           src(NHAL_M, "Clear Lake Campground")),
    3302: (sea("04-01", "12-01", "Snow conditions permitting."), src(NHAL_M, "Crystal Lake Campground")),
    3300: (sea("04-30", "10-14", APR_COL), src(NHAL_M, "Firefly Lake Campground")),
    3309: (sea("05-21", "10-01", MEM_OCT), src(NHAL_M, "Musky Lake Campground")),
    14020: (sea("04-30", "10-14", APR_COL), src(NHAL_R, "Buffalo Lake Campground")),
    3315: (sea("05-21", "09-07", MEM_LAB), src(NHAL_R, "Carrol Lake Campground")),
    3305: (sea("05-21", "09-07", MEM_LAB), src(NHAL_R, "Cunard Lake Campground")),
    14021: (sea("05-21", "09-07", MEM_LAB), src(NHAL_R, "East Star Lake Campground")),
    3306: (sea("04-30", "10-14", APR_COL), src(NHAL_R, "Indian Mounds Campground")),
    3301: (sea("04-30", "11-01"), src(NHAL_R, "North Trout Lake Campground")),
    3310: (sea("05-21", "09-07", MEM_LAB), src(NHAL_R, "Plum Lake Campground")),
    3303: (sea("05-21", "09-07", MEM_LAB), src(NHAL_R, "South Trout Campground")),
    3312: (sea("04-30", "10-14", APR_COL), src(NHAL_R, "Starrett Lake Campground")),
    3304: (sea("05-21", "10-01", MEM_OCT), src(NHAL_R, "Upper Gresham Lake Campground")),
    3313: (sea("04-30", "11-01"), src(NHAL_R, "West Star Lake Campground")),
}

if __name__ == "__main__":
    run(DECISIONS)
