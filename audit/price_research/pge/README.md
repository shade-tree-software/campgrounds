PG&E campground fees (2026-10-10).

The reservation site renders every site's card, with a "Use Fee", even when nothing is
bookable (reservations open Apr 15 each year; FCFS sites are listed too). POST the search
form directly:

    curl -s -c cj -b cj https://recreation.pge.com/reservation/camping/index.asp -o /dev/null
    curl -s -b cj -X POST https://recreation.pge.com/reservation/camping/index.asp \
      --data "reserve_type=camping&parent_idno=<ID>&camping_arrive_date=07/06/2027&camping_depart_date=07/08/2027&actiontype=search&hdreslength=2&max_consecutive_nights=14&min_consecutive_nights=2" \
      | grep -o 'Use Fee:&nbsp;\$[0-9.]*'

"Use Fee" is the STAY TOTAL, not nightly (Lake McCumber: $30 for 2 nights, $45 for 3).
Park ids are the options of the #parent_idno select on the index page.
use_fees_2027-07-06_2n.tsv is the digest of the 2-night search used for the fees.
