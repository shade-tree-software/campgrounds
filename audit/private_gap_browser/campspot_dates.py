# campspot_dates.py SLUG DATE [DATE ...] [--nights N]
# Campspot's availability answer for one park on extra dates, through the one driver browser and the API
# campspot_api.py uses: per site type the average nightly price (fees folded in), free/total sites and the failure
# reasons. Written 2026-10-13 to tell a standing minimum from a date's own rule ("There is a 2 night minimum" on one
# Tuesday in October but not on a Tuesday in November) and to see when a park's season opens.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from campspot_api import api, call, plus  # noqa: E402


def main():
    args = sys.argv[1:]
    nights = 1
    if "--nights" in args:
        i = args.index("--nights")
        nights = int(args[i + 1])
        del args[i:i + 2]
    slug, dates = args[0], args[1:]
    if 'campspot.com' not in call(cmd='url'):
        call(cmd='goto', url='https://www.campspot.com/', wait='6000')
    p = api('/api/gator-core/v2/parks/slug/%s' % slug)['park']
    cats = [c['name'] for c in sorted(p['ageCategories'], key=lambda c: c['parkAgeCategoryIndex'])]
    adult = next(i for i, c in enumerate(cats) if 'adult' in c.lower())
    guests = 'guests' + ','.join(['2' if i == adult else '0' for i in range(len(cats))] + ['0'])
    print(p['id'], p['name'], guests)
    for d in dates:
        lst = api('/api/gator-core/v2/availability/parks/%s?checkin=%s&checkout=%s&guests=%s'
                  '&useCustomParkData=true&includeUnavailable=true' % (p['id'], d, plus(d, nights), guests))
        print('==', d, '+%d' % nights, '' if lst else '(nothing listed)')
        for t in lst if isinstance(lst, list) else []:
            sites = t.get('campsites') or []
            fr = sorted({f.get('reason', '') for f in (t.get('failureReasons') or [])}
                        | {f.get('reason', '') for s in sites for f in (s.get('failureReasons') or [])})
            print('  %-6s %-8s %-46s free %d/%d  %s' % (t.get('campsiteCategoryCode'), t.get('averagePricePerNight'),
                                                       (t.get('name') or '')[:46],
                                                       sum(s.get('availability') == 'AVAILABLE' for s in sites),
                                                       len(sites), ' / '.join(fr)[:120]))


if __name__ == '__main__':
    main()
