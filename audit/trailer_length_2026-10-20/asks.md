# Trailer-length pass: questions for AWH (2026-10-20)

Done without asking (`apply.py`, commit a1a4f1f5): 13 rec.gov campgrounds dropped because
every RV site in the catalog is rated under 23 ft and no agency page says otherwise.

## 1. Is a 22-ft limit "under ~23 ft"?

64 entries post a 22-ft limit and have no per-site lengths to check it against: 62 federal
(AZ 16, MT 16, CA 11, OR 7, WA 8, CO 1, NM 2, WY 2; Christopher Creek AZ is the one with
per-site data), plus Atsion NJ (state) and Navy Camp CA / Rifrafters WV (private). Most of
the notes already call it "borderline for a 23-ft rig".

The evidence that it is a standard line rather than a measurement: of the 17 campgrounds
with the same posted 22 ft that rec.gov DOES catalog per site, **16 have sites rated
23 ft or longer** (Rose Canyon 40, Spring Hill 47, Lost Johnny Point 49, Coy Flat 26, Frog
Lake 26, Sunset Falls 40 ...). They were kept. Only Christopher Creek rates every site at
exactly 22 ft (its driveways measure 23-67 ft).

- **(a) Keep the 22-ft class** (recommended): 22 is within the "~" of 23, and where we can
  check, the posted 22 almost never describes the actual sites. Notes already flag it.
- (b) Drop all 64: a posted 22 is under 23.
- (c) Keep, but drop Christopher Creek, where the 22 is the per-site rating.

List: `python3 -I audit/trailer_length_2026-10-20/note_scan.py` (22-ft lines), or the ids in
the session report.

## 2. A posted limit of 20-21 ft that firsthand reports contradict

The rule assumes a trailer limit applies to a motorhome "in the absence of any additional
information". These four have additional information, but from reviewers, not the agency:

- 10262 Seal Rock WA (Olympic NF): posted 21 ft; reviewers report 28-30 ft rigs in the
  larger waterfront sites.
- 13661 Idlewild OR (Malheur NF): FS says trailers 20 ft and under; reviewers find 4-5 sites
  taking 25-36 ft rigs (site 1 paved and roomy).
- 6419 Sinks Canyon WY (Shoshone NF): spurs ~20 ft; larger motorhomes have used the Sawmill
  portion.
- 8045 Grapevine NM (Gila NF): posted 20 ft for the steep entrance grade; reviewers report
  Class C rigs to ~29 ft.

Recommended: keep (the notes already carry the caveat). Alternative: drop, treating only an
agency source as able to override a posted limit.

## 3. Umtanum WA (10395, BLM Yakima River Canyon)

Every site carries rec.gov's "Max Vehicle Length 20" attribute, but the permitted-equipment
lengths are blank and the driveways measure 35-69 ft. The same flat-20 attribute was a
placeholder at the Lake Ouachita and New Hogan Corps campgrounds. The BLM page gives no length.
Its neighbor Roza (20-ft driveways) was dropped. Recommended: keep.

## Kept without asking (for the record)

- McClintic Point VA (447) and New Germany MD (63): your own notes say rigs fit past the
  posted 20-21 ft.
- Roan Creek TN (13392): the 20-ft limit is temporary bridge work, dated in the note.
- Crab Flats CA (12304): one FCFS site lists motorhomes to 26 ft (trailers 21 everywhere);
  note corrected. Horseshoe CO (2413): rec.gov says "fits RVs up to 25 feet"; note corrected.
- Many notes give a trailer figure beside a longer motorhome one (White River WA 18/27, Dog
  Lake WA 20/24, Caswell CA 21/24, Tohickon PA 18/25): the source distinguishes, so they stay.

## Answers (AWH 2026-10-20)

All three: **keep all.** The 22-ft class stays (22 is within the "~" of 23), the four
reviewer-contradicted 20-21 ft limits stay, and Umtanum stays. No data change.
