"""SEPAQ search jobs: each entry's destination id and the loops (leaf sectors) its campground covers.
    python3 -I qc_sepaq_jobs.py qc_sepaq_tree_2026-10-12.json OUT_JOBS.json
The tree (every destination's 'where' id and its sector radio list) was read in the page from each
/en/reservation/camping/<destination> page (2026-10-12). A park-level entry takes every loop of its park."""
import json, sys
tree = {p["slug"].split("/")[-1]: p for p in json.load(open(sys.argv[1]))}
MAP = {
 12479: ["parc-national-de-plaisance"], 12480: ["reserve-faunique-la-verendrye/de-la-vieille"],
 12485: ["reserve-faunique-la-verendrye/lac-rapide"], 12486: ["reserve-faunique-la-verendrye/savary"],
 12481: ["reserve-faunique-de-papineau-labelle/lac-echo"], 12482: ["parc-national-du-mont-tremblant/lac-chat"],
 12483: ["parc-national-du-mont-tremblant/lac-des-sables"], 12487: ["parc-national-du-mont-tremblant/lac-escalier"],
 12488: ["parc-national-du-mont-tremblant/la-voliere-lac-provost"],
 12498: ["parc-national-du-mont-tremblant/l-assomption/grand-pin"],
 12484: ["reserve-faunique-rouge-matawin/la-macaza/lac-des-sucreries"], 12489: ["parc-national-d-oka"],
 12490: ["parc-national-des-iles-de-boucherville/molson-espace-vr"], 12491: ["parc-national-du-mont-orford/lac-stukely"],
 12494: ["parc-national-du-mont-orford/lac-fraser"], 12492: ["parc-national-de-la-jacques-cartier"],
 12493: ["parc-national-de-la-yamaska"], 12495: ["reserve-faunique-du-saint-maurice/lac-dunbar"],
 12496: ["reserve-faunique-du-saint-maurice/lac-normand"], 12497: ["reserve-faunique-mastigouche/camping-st-bernard"],
 12499: ["parc-national-de-frontenac/saint-daniel/riviere-aux-bluets-d", "parc-national-de-frontenac/saint-daniel/riviere-aux-bluets-f"],
 12500: ["parc-national-de-frontenac/secteur-sud/camping-baie-sauvage"],
 12501: ["parc-national-de-frontenac/saint-daniel/rats-musques"],
 12502: ["parc-national-du-mont-megantic/de-franceville"], 12503: ["parc-national-d-aiguebelle/abijevis"],
 12504: ["parc-national-de-la-pointe-taillon/camp-de-touage"], 12505: ["reserve-faunique-ashuapmushuan/lac-chigoubiche"],
 12506: ["parc-national-du-bic"], 12507: ["parc-national-du-fjord-du-saguenay/baie-eternite"],
 12508: ["parc-national-du-fjord-du-saguenay/baie-sainte-marguerite/le-bleuvet"],
 12509: ["parc-national-des-grands-jardins/du-pied-des-monts"], 12512: ["parc-national-des-grands-jardins/arthabaska"],
 12510: ["reserve-faunique-des-laurentides/l-etape"],
 12511: ["parc-national-des-hautes-gorges-de-la-riviere-malbaie/le-cran"],
 12513: ["parc-national-de-la-gaspesie/camping-de-la-riviere"], 12514: ["parc-national-de-la-gaspesie/camping-mont-albert"],
 12518: ["parc-national-de-la-gaspesie/camping-lac-cascapedia"],
 12515: ["reserve-faunique-de-matane/etang-a-la-truite"], 12516: ["reserve-faunique-de-matane/camping-john"],
 12517: ["reserve-faunique-de-rimouski/camping-lac-rimouski"], 12519: ["reserve-faunique-de-port-daniel"],
 12522: ["reserve-faunique-de-port-cartier-sept-iles/lac-walker"], 12523: ["reserve-faunique-de-port-cartier-sept-iles/lac-arthur"],
 12576: ["centre-touristique-du-lac-simon"], 12596: ["camping-des-voltigeurs"],
}
jobs = []
for eid, prefixes in MAP.items():
    dest = prefixes[0].split("/")[0]
    secs = [(s["id"], s["path"].split("/reservation/camping/")[1]) for s in tree[dest]["sectors"] if s["id"]]
    paths = {p for _, p in secs}
    ids = {p: i for i, p in secs}
    leaves = []
    for i, p in secs:
        if any(q.startswith(p + "/") for q in paths):
            continue                                  # has children: not a leaf
        if not any(p == pre or p.startswith(pre + "/") for pre in prefixes):
            continue
        parts = p.split("/")
        group = ids.get("/".join(parts[:2])) if len(parts) == 3 else ""
        leaves.append({"sectorId": i, "groupSectorId": group or "", "path": p})
    if not leaves:
        print("NO LEAVES", eid, prefixes, file=sys.stderr)
    jobs.append({"eid": eid, "where": tree[dest]["where"], "leaves": leaves})
json.dump(jobs, open(sys.argv[2], "w"), ensure_ascii=False)
print(len(jobs), "jobs,", sum(len(j["leaves"]) for j in jobs), "leaves")
for j in jobs:
    print(j["eid"], len(j["leaves"]), [l["path"].split("/", 1)[1] for l in j["leaves"]][:6])
