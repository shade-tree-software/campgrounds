# mkbrief_mo.py SCRATCH BATCH PARAGRAPH_FILE: write SCRATCH/<BATCH>_prompt.txt from brief_mo.txt,
# the Missouri phase-7 brief as p3-321 ran it (2026-11-07). PARAGRAPH_FILE holds this batch's
# "The twelve are all MISSOURI - ..." paragraph: name each entry with what to look hard at, then one
# sentence on what the previous batch found. Build the batch first: queue.py --batch BATCH --limit 12.
import os, sys
K = os.path.dirname(os.path.abspath(__file__))
S, b, pf = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(os.path.join(K, 'brief_mo.txt')).read()
t = t.replace('__SCRATCH__', S).replace('__BATCH__', b).replace('__PARAGRAPH__', open(pf).read().strip())
os.makedirs(os.path.join(S, b), exist_ok=True)
open(os.path.join(S, b + '_prompt.txt'), 'w').write(t)
print(os.path.join(S, b + '_prompt.txt'))
