# Fee-registry add-on research (step 2 of the trip-cost plan, 2026-11-07)

Goal: for each policy-registry row you are given, settle the **add-on charges** a camper pays on
top of the nightly site rate, so a stay's price can be computed from the fields alone. You are
researching an AGENCY (a state park system, a provincial park system, a federal agency), not one
campground: a value goes on the row only if it holds for the agency's campgrounds generally.

Read first: `docs/campground-schema.md` §4.2 (the fee mechanics, and the new paragraphs on
seasonal/tax and "a zero is a recorded none"), and the row's current `fees` block and `fees.note`
in `campground_policies.json` — the note often already holds leads. Do NOT edit any repo file;
write only your output file.

## The keys to settle, per row

| key | settle as |
|---|---|
| `entrance` | park entry/day-use/vehicle-permit charge campers must pay on top of the site fee: `{resident, nonresident, per, name?, annual?, departure_day?, waived_by?}`. **Campers exempt / no entrance fee → `{"resident": 0, "nonresident": 0}`**. Varies park by park → leave unset and say so in `unsettled` (give the range). |
| `reservation_fee` | per-reservation booking/transaction fee (online; note phone differences in `note_add`). None charged → `0`. |
| `tax` | `{"included": true}` (posted rates include tax) · `{"percent": N}` (added on top, one statewide/provincial figure; for Canada GST/HST/PST combined if all apply on top) · `{"percent": 0}` (no tax charged) · `{"included": false, "name": "..."}` (taxed on top, rate varies by locality). |
| `nonresident` | a non-resident CAMPING rate (not entrance). None → `{"type": "surcharge", "amount": 0}`. |
| `extra_person` | agency-wide rule for people beyond what the site fee covers: `{included, amount, per, child, child_max_age, max_people}`. No charge for extra people → `{"amount": 0}` (+ `max_people` if a cap is agency-wide). |
| `extra_vehicle` | agency-wide rule for vehicles beyond the site fee's: `{included, amount, per, max_vehicles}`. Extra vehicles free → `{"amount": 0}`. |
| `surcharges.weekend` / `surcharges.holiday` | only if the agency charges a flat weekend/holiday premium on every park. Do NOT replace the row's other surcharges — return the full `surcharges` object you want (existing keys included). |

Also **verify the values already on the row** for these keys; correct any that are out of date.

## Evidence rules (non-negotiable)

- **Primary sources only**: the agency's own fee/rates/reservation-policy pages, its booking site's
  posted rules, its fee schedule in statute or administrative code. Aggregators, blogs, review sites
  and search-result snippets never count. A page that blocks automated fetch may be read via a
  search summary ONLY if you mark that key `"method": "reported"` and say so.
- **Every key you set carries a verbatim quote** from the source (in `sources`), short but exact.
- **A zero needs positive evidence**: an explicit statement ("no entrance fee for registered
  campers", "no reservation fee", "rates include tax"), OR the agency's complete official fee
  schedule (statute, admin code, or a page that says it is the full fee list) in which the charge
  does not appear — quote the heading that shows it is complete. A rates page that simply doesn't
  mention a charge is NOT evidence of none; leave the key unset and list it in `unsettled`.
- **Absent is unknown.** Never fill a placeholder. If you can't settle a key, put it in `unsettled`
  with what you found (e.g. "entrance varies by park, $0-10").
- Agency-wide only. A rule stated for "most parks" with named exceptions may go on the row with
  the exceptions written into `note_add`. A rule that is truly per park stays off the row.
- Amounts in the row's currency (USD for US, CAD for Canada). Include tax where the agency's own
  figure includes it, and say which.

## Output

Write a JSON array to the output path you are given, one object per row:

```json
{
  "ref": "state:IN",
  "set": {"tax": {"percent": 7}, "extra_vehicle": {"included": 1, "amount": 0}, "reservation_fee": 6},
  "remove": [],
  "note_add": "Tax: 7% Indiana sales tax is added to camping fees (... ). Extra vehicles ...",
  "sources": [{"key": "tax", "url": "https://...", "quote": "verbatim text"}],
  "method": "manual",
  "method_by_key": {"tax": "reported"},
  "unsettled": {"extra_person": "rates page says nothing; no fee schedule found"},
  "summary": "one line"
}
```

`set` holds only keys you are adding or changing (an unchanged verified value may be included;
it costs nothing). `remove` lists keys you found to be WRONG with no replacement (quote why).
`note_add` is plain prose appended to the row's `fees.note`: terms the fields can't hold
(phone-booking fee difference, park exceptions, local tax add-ons). No URLs in `note_add`; they go
in `sources`. Keep it short. Finish with a one-paragraph report of what you settled and what you
couldn't.
