"""AWH 2026-10-14 #7, second batch: the entries this pass reached whose operator claims water where our call
differs (decisions.WF). Same method and record format as audit/price_research/waterfront_reaudit_2026-10-14/:
Esri World Imagery through audit/sat_look.py (and audit/private_gap_browser/wb.py for older captures), the
operator's own per-site map where it has one, and the evidence gate of docs/campground-curation.md.

    python3 -I audit/price_research/roverpass_ops_2026-10-14/waterfront_reaudit.py   -> writes waterfront_reaudit.json
"""
import json
import os

R = []


def r(i, name, current, final, evidence, confidence, coord_fix=None, elevation_meters=None):
    R.append({"id": i, "name": name, "current": current, "final": final, "coord_fix": coord_fix,
              "elevation_meters": elevation_meters, "evidence": evidence, "confidence": confidence})


r(4476, "Crazy Horse Recreational Park", "riverview", "riverview", confidence="high",
  coord_fix="35.45684,-87.77581", elevation_meters=173.0,
  evidence="The park's own Google My Maps property map (embedded on crazyhorsecanoe.com/map; KML export read "
           "2026-10-14) marks every RV hookup: the South Campground's '30 amp electric and water' and '30/50 electric "
           "and water - no tents' runs by the office and 'All along the treeline' of the field, the North "
           "Campground's 30-amp sites by the riverside track, its sewer sites ('monthly sites') at the far field "
           "edge. Plotted on Esri imagery (z18/z19, leaf-off): the nearest RV markers are ~35-50 m from the Buffalo "
           "River's bank, behind a riparian grove that holds the primitive tent sites ('South Tents', 'North "
           "Tents' along the bank) - a wooded strip in use, so not on-water whatever the 'riverfront RV sites' copy "
           "says. The park's own RV-site panoramas (camp-rv-sites-pano.jpg and -2) show the river through the "
           "trunks beyond the gravel pads by the office, so riverview holds. The earlier 'main RV row set back "
           "~150m across field' read the outfitter's bus row. Pin moved ~280 m from the north bridgehead on Hwy 13 "
           "(35.45933,-87.77536) to the map's 'Office/Camp Store/Lodge' marker beside the South Campground's pads.")
r(7574, "Holly Park Marina", "lakeview", "lakefront", confidence="medium",
  evidence="The operator's rates page sells 'RV 30amp (Water-Front)' and 'RV 50amp (Water-Front)' at $55 against "
           "'(Water-View)' at $45 - a per-site class of its own. Esri 2019-04-27 (WV03) at z19 and Wayback "
           "2018-12-05 (release 32645, leaf-off): the marina is a small wooded point south of the Hwy 21 "
           "bridgehead on Toledo Bend; RVs stand under scattered pines and oaks 15-20 m from the point's east shore "
           "with open ground between and no road, building or continuous screen, and an open lawn runs to the water "
           "on the south-east. The earlier 'continuous treeline shore' read the canopy, not the gaps under it.")
r(7777, "Scenic View Motel & RV Park", "not waterfront", "lakefront", confidence="medium",
  evidence="The operator: 'bringing your own camper and hooking up right on the shore front!' and 'over 100 yards "
           "of shoreline' (scenicviewmarina.com). Esri 2023-08-24 (WV02) at z19: travel trailers in the paved lot "
           "beside the marina, the nearest at its north-west corner ~15 m from Lone Star Lake across an open mowed "
           "strip with a few trees; Wayback 2020-06-12 (release 12457): four RVs parked side by side along that "
           "lakeward edge, 10-15 m from the water. No road or developed strip between - the open-apron rule; the "
           "marina lawn and dock to the south are a used strip, but the RV row is north of them. The earlier 'not "
           "waterfront' read the marina's cabins and docks, not the RV row.")
r(8133, "Angel Nest RV Retreat", "not waterfront", "not waterfront", confidence="high",
  coord_fix="36.54093,-105.27525", elevation_meters=2513.0,
  evidence="Our pin (36.5328,-105.2746) sat on a cluster of houses ~900 m south of the park, which is what the "
           "earlier evidence described. The park's own site (schema.org geo 36.5403685,-105.2774199 for 28418 US "
           "64) and its RoverPass listing (36.540846,-105.277433) both put it at the compound north of the "
           "cross-road ~1 km south-west of Eagle Nest village: red-roofed cabins and buildings with a large open "
           "gravel RV lot east of them (Esri z17/z18). WestLake RV (28378 US-64, Google 36.53635,-105.27529) is the "
           "separate lot further south. The nearest open water of Eagle Nest Lake is ~700-800 m east across a "
           "residential subdivision and the state park's marina complex, so the operator's 'mountain and lake "
           "views' are a distant vista, not lakeview. Pin moved ~900 m north onto the RV lot.")
r(4295, "Stony Fork Creek RV Park", "not waterfront", "not waterfront", confidence="medium",
  coord_fix="35.46019,-82.73712", elevation_meters=794.0,
  evidence="The operator's 'Creekside spaces' (stonyforkrv.com home page) didn't hold up. Its own pages give 10 "
           "full-hookup sites at 2149 Pisgah Hwy and the email okelleyfarm@gmail.com; Google pins the park on the "
           "O'Kelley farm west of NC-151 (35.46019,-82.73712). The 2023-02-18 NC911 ortho (Wayback release 20512, "
           "0.15 m, leaf-off, z19) shows a handful of RVs parked around the farm buildings there, 80 m or more from "
           "the nearest channel. The 18-site loop just north (Pisgah View RV Park, 2138 Pisgah Hwy, same phone), "
           "which the operator's photos also show, keeps its south row behind the loop's own gravel track and a "
           "shrub line along a small side stream. East of the highway, a lane of trailers runs toward the main "
           "creek, but nothing ties it to this park. No RV pad fronts a creek across open ground, so it defaults "
           "down. The old pin (35.4628,-82.7368) sat among houses north of the loop and is moved to the farm.")
r(14429, "K-Park", "not waterfront", "creekside", confidence="high",
  evidence="The operator says 'We provide full hook ups and have waterfront lots & private docks' (k-parkswfl.com), "
           "and its own aerial photo (home page, '36-Aerial Photo 003.jpg', read 2026-10-14) shows them. RVs stand on "
           "open gravel pads at the north bank of Henderson Creek, about 25 m wide and tidal with Gulf access. The "
           "bank is riprap planted with a few palms and has small dock shelters at the water's edge; there is no "
           "road, building or continuous screen between pads and water. Esri z19 (0.27 m/px) agrees: a gravel "
           "drive of RV pads runs south from Henderson Creek Dr, and the southernmost RVs are about 10-15 m from "
           "the water. The earlier call came from a 900 m frame that couldn't resolve the pads under the trees. "
           "It's a creek rather than a river, so creekside.")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "waterfront_reaudit.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(R, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(out, len(R))
