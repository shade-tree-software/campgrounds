// SEPAQ booking search, run INSIDE a sepaq.com reservation page through the one-browser driver (2026-10-12):
//   substitute __JOBS__ with qc_sepaq_jobs.py's output, `drv.py eval js=...`, poll window.__sqState, then read
//   window.__sqRes with `eval js=JSON.stringify(window.__sqRes) max=50000000`. One POST /en/reservation/search per
//   loop, night and results page (10 sites a page). The referrer MUST be the loop's own URL: the server pages through
//   whatever sector the Referer names, so page 2+ otherwise comes back for the page the browser is on.
(function(){
  const JOBS = __JOBS__;
  const DATES = ['2027-06-08', '2027-07-13', '2027-07-17', '2027-09-07'];
  const csrf = document.querySelector('input[name=_csrf]').value;
  window.__sqRes = []; window.__sqState = {done: false, step: 0, total: JOBS.reduce((a, j) => a + j.leaves.length, 0) * DATES.length, errors: []};
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  function next(d) { const x = new Date(d + 'T12:00:00Z'); x.setUTCDate(x.getUTCDate() + 1); return x.toISOString().slice(0, 10); }
  async function search(where, leaf, arr, page) {
    const fd = new URLSearchParams();
    const base = {'booking.arrivalDate': arr, 'booking.departureDate': next(arr), 'booking.adults': '2', 'booking.children': '0',
      'priceRange.from': '0', 'priceRange.to': '650', 'requestedPage': String(page), 'requestedSort': 'PRICE',
      'sectorId': leaf.sectorId, 'groupSectorId': leaf.groupSectorId, 'where': where, 'viewType': 'liste',
      'capaciteExacte': 'false', 'flexibilite': '0', '_csrf': csrf};
    for (const k in base) fd.append(k, base[k]);
    const r = await fetch('/en/reservation/search', {method: 'POST', body: fd, credentials: 'same-origin', referrer: 'https://www.sepaq.com/en/reservation/camping/' + leaf.path});
    const doc = new DOMParser().parseFromString(await r.text(), 'text/html');
    return {status: r.status, url: r.url, items: Array.from(doc.querySelectorAll('.resultat')).map(d => ({
      type: ((d.querySelector('.resultat-surnom') || {}).textContent || '').trim(),
      name: ((d.querySelector('.resultat-nom') || {}).textContent || '').trim(),
      price: ((d.querySelector('.resultat-prix strong') || {}).textContent || '').trim(),
      dispo: ((d.querySelector('.resultat-dispo') || {}).textContent || '').replace(/\s+/g, ' ').trim(),
      href: ((d.querySelector('.resultat-nom a') || {getAttribute: () => ''}).getAttribute('href')) || ''}))};
  }
  (async function(){
    for (const j of JOBS) for (const leaf of j.leaves) for (const d of DATES) {
      const seen = new Set();
      for (let page = 0; page < 60; page++) {
        let res;
        try { res = await search(j.where, leaf, d, page); } catch (e) { window.__sqState.errors.push([j.eid, leaf.path, d, page, String(e)]); break; }
        const fresh = res.items.filter(it => !seen.has(it.href));
        if (!fresh.length) break;
        for (const it of fresh) { seen.add(it.href); window.__sqRes.push(Object.assign({eid: j.eid, leaf: leaf.path, date: d, page: page, url: res.url}, it)); }
        if (res.items.length < 10) break;
        await sleep(250);
      }
      window.__sqState.step++;
      await sleep(250);
    }
    window.__sqState.done = true;
  })();
  return 'started ' + window.__sqState.total;
})()
