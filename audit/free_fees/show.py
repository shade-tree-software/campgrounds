# show.py CAND.json START COUNT: print the price-bearing sentences of each candidate note, for reading.
import json, re, sys
c = json.load(open(sys.argv[1])); a = int(sys.argv[2]); n = int(sys.argv[3])
key = re.compile(r'free|fee|\$|charge|donation|cost|pay|per night|/night|nightly', re.I)
for e in c[a:a+n]:
    sents = re.split(r'(?<=[.;!])\s+', e['note'].replace('\n', ' '))
    keep = [s for s in sents if key.search(s)]
    print(f"{e['id']} [{e['own']}] {e['name']} :: " + ' | '.join(keep)[:420])
