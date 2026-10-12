// Site detail pages (eligible equipment, lot size, services, access) for a list of hrefs, run inside a sepaq.com page:
//   substitute __HREFS__, eval, poll window.__sqDetState, read window.__sqDet. qc_sepaq_more_reads.py picks the hrefs.
(function(){
  const HREFS = __HREFS__;
  window.__sqDet = {}; window.__sqDetState = {done: false, i: 0, n: HREFS.length, errors: []};
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  (async function(){
    for (const href of HREFS) {
      try {
        const r = await fetch(href, {credentials: 'same-origin'});
        const doc = new DOMParser().parseFromString(await r.text(), 'text/html');
        const out = {};
        doc.querySelectorAll('h4').forEach(h => {
          const k = h.textContent.trim();
          if (['Eligible Equipment', 'Site', 'Services', 'Access'].includes(k))
            out[k] = Array.from(h.parentElement.querySelectorAll('li')).map(li => li.textContent.replace(/\s+/g, ' ').trim());
        });
        window.__sqDet[href] = out;
      } catch (e) { window.__sqDetState.errors.push([href, String(e)]); }
      window.__sqDetState.i++;
      await sleep(200);
    }
    window.__sqDetState.done = true;
  })();
  return 'started ' + HREFS.length;
})()
