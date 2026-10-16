"""CA3 local findings from the browser pass (follow-up: agency fee pages read in the driver browser 2026-10-16, after the crawl), USD.
python3 -I build_ca3.py > findings_ca3.json. low/high = RV (powered/hookup) sites, or the site rate where a park has
no power; unserviced/tent in the note. Source = first page of the record whose captured lines contain KEY."""
import json
ROWS = [
(11746, 41, 41, 10, "https://parks.sonomacounty.gov/play/camping/tent-trailer-and-rv-campsites", "Sonoma County Regional Parks: $41 a night, $13 more for sites with electric hookups; Sonoma County residents $2 off (not at Spring Lake); tax and a $10 non-refundable reservation fee apply."),
 (11760, 41, 41, 10, "https://parks.sonomacounty.gov/play/camping/tent-trailer-and-rv-campsites", "Sonoma County Regional Parks: $41 a night, $13 more for sites with electric hookups; Sonoma County residents $2 off (not at Spring Lake); tax and a $10 non-refundable reservation fee apply."),
 (11823, 41, 54, 10, "https://parks.sonomacounty.gov/play/camping/tent-trailer-and-rv-campsites", "Sonoma County Regional Parks: $41 a night, $13 more for sites with electric hookups; Sonoma County residents $2 off (not at Spring Lake); tax and a $10 non-refundable reservation fee apply."),
 (11821, 41, 41, 10, "https://parks.sonomacounty.gov/play/camping/tent-trailer-and-rv-campsites", "Sonoma County Regional Parks: $41 a night, $13 more for sites with electric hookups; Sonoma County residents $2 off (not at Spring Lake); tax and a $10 non-refundable reservation fee apply."),
 (11780, 35, 50, None, "https://rivcoparks.org/regional-parks-campgrounds/lake-skinner-recreation-area", "Riverside County Parks: camping $35-50 a night (fees effective August 1, 2024); day use $6 a person."),
 (11764, 30, 35, None, "https://rivcoparks.org/regional-parks-campgrounds/hurkey-creek-regional-park", "Riverside County Parks: camping $30-35 a night (fees effective August 1, 2024); day use $6 a person."),
 (11808, 45, 55, None, "https://rivcoparks.org/regional-parks-campgrounds/rancho-jurupa-regional-park", "Riverside County Parks: camping $45-55 a night (fees effective August 1, 2024); day use $6 a person."),
 (11773, 30, 50, None, "https://rivcoparks.org/regional-parks-campgrounds/lake-cahuilla-veterans-regional-park", "Riverside County Parks: camping $30-50 a night (fees effective August 1, 2024); day use $6 a person."),
 (11765, 30, 35, None, "https://rivcoparks.org/regional-parks-campgrounds/idyllwild-regional-park", "Riverside County Parks: camping $30-35 a night (fees effective August 1, 2024); day use $6 a person."),
 (11797, 20, 26, None, "https://parks.oc.gov/about-us/oc-parks-fees/camping-fees", "OC Parks: individual campsites $20 a night, utility hookups $6 more; seniors and persons with disabilities $15."),
 (11812, 20, 26, None, "https://parks.oc.gov/about-us/oc-parks-fees/camping-fees", "OC Parks: individual campsites $20 a night, utility hookups $6 more; seniors and persons with disabilities $15."),
]
recs = {}
for l in open("browser.jsonl"):
    x = json.loads(l); recs[x["id"]] = x
out = []
for i, lo, hi, rf, key, note in ROWS:
    urls = [key] if key.startswith("http") else [p["url"] for p in recs[i]["pages"] if key in p.get("lines", "")]
    assert urls, (i, key)
    f = {"nightly_low": lo, "nightly_high": hi, "currency": "USD"}
    if rf:
        f["reservation_fee"] = rf
    f.update({"checked": "2026", "note": note + " Read 2026-10-16."})
    out.append({"id": i, "fees": f, "source": urls[0] + " (driver browser follow-up after the crawl), read 2026-10-16"})
print(json.dumps(out, ensure_ascii=False, indent=1))
