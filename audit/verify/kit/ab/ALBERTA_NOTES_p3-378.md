# Alberta notes, batch p3-378 (2026-11-10)

## Tooling that worked
- `kq.sh SLUG MM/DD/YYYY MM/DD/YYYY ...` (in this folder) starts drv_server.py, runs koa.py per date, quits the driver.
  Run it as `timeout 900 flock /tmp/ekko-headless-browser.lock ./kq.sh ...`.
  **DRV_SOCK must be a short path** (/tmp/claude-1000/p378drv.sock). Under the long scratch dir, AF_UNIX fails with "path too long".
- koa.com answers 403 to curl. For page text (season, max length, phone), use Wayback `web/2026id_/https://koa.com/campgrounds/<slug>/`.
- Campspot: `cs1.py SLUG CI CO ...` gives the park record and type list. `cs2.py SLUG PID guests0,2,0 TID:CI:CO` gives quotes, read with `csq.py`.
  The list price can be base + booking fee (Irricana: list 38 = base 35 + C$3 fee).
  Check `rvInfo.rvTypes` for Motorhome: Irricana's power-only sites exclude motorhomes.
- Alberta Parks shop: `ralist.py <slug> <parkId> out.json`, then `rasum.py out.json '.'`, gives per-site max vehicle length and pull-throughs.
- WordPress town sites: `/wp-json/wp/v2/posts?search=campground` finds the season posts fast (Irricana).
- Let's Camp API (`/api/camps/<slug>`, header `X-Tenant-Type: camp`) works plainly (Grande Cache).
- Medicine Hat books on PerfectMind. Its PDFs moved to media-002-ca.cdn.govstack.com.
- goldsprings.ca had a DNS failure (lame delegation). Wayback id_ captures worked.

## Facts worth remembering
- Grande Prairie Rotary: the stored pin sits in Bear Creek. Its booking link is campspot.com/book/grande-prairie-rotary.
- Happy Trails (Grande Prairie): the wooded RV loops ~600 m east along Bear Creek are Country Roads RV Park (9124), not Happy Trails.
- Jarvis Bay: Facility Operator is "KR Campground Maintenance" (no phone). There is no seniors-discount line. The lookout near site 129 has been closed since 2025-08-27.
- Irricana: owned and managed by the town. The campground phone is (403) 827-1869, not the stored 403-371-7376.
- Granum (Granview): visitgranum.com now says Granum is "Formerly the Smallest Town in Alberta". Ownership needs a reviewer's call.
