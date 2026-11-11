# Alberta notes from p3-386 (2026-11-10)
- Westlock (Mountie Park): page moved to westlock.ca/visit-explore/mountie-park-campground/; books on Checkfront mountiepark.checkfront.com/reserve/ (403 to curl, bw.py lists sites + prices; "POWER ONLY" duplicates at C$25).
- Nature's Hideaway books on PitchCamp (campground_name=natuhidefamicam2503101031); bwnet2.py body text lists every free site with type, 'Fits: Max N ft', amps and price even in November (2027 Apr 15 default search).
- Red Rock Sawmills (redrocksawmill.com) runs North Ghost / Fallen Timber South / Waiparous: single sites by phone 587-830-2198 or email, reservations open March 1; only group camps on the AB shop.
- Raymond (Perrett Park): town page says FCFS but raymond.activityreg.com/selectfacility_t2.wcs?parks=51 has 'Check Availability & Reserve' (needs a browser; curl gets an empty shell).
- Pierre Grey's: tear sheet map names loops (W=Wanyandie by McDonald L, M=Moberly, D=Delorme, J=Joachim); stored pin = McDonald Day Use; page destination point is in Delorme.
- Visit Sylvan Lake (Pogadl): Cloudflare 403 to curl; browser loads it, but accordion text needs document.body.textContent (bwtext.py), links via bwlinks.py. Rates/contacts are on /camping/, not the places page.
- ap.sh = fetch an Alberta Parks camping page + print advisories/table/destination point/tear-sheet link.
- Esri export 500s come in runs; wait a few seconds and retry, or crop.py the wider frame.
- Oldman Dam Castleview sits below the dam: judge it against the tailwater river only (DEM 1085 m sites vs 1050 m river).
