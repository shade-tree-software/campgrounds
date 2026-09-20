// Shared formatters for the structured campground fields (docs/campground-schema.md).
//
// The manage page and the campground-map popup speak about the same eight
// groups, and a second copy of this vocabulary in the other template would
// drift the first time a field was phrased on one side only — the same
// argument that makes the form render from the server's `to_client()`
// projection rather than a hand-kept list in JavaScript. The field METADATA
// still comes from the server; what lives here is only how a value is spoken.
//
// Everything here is pure: no DOM, no page globals, no escaping. A chip is
// plain text and the caller escapes it wherever it lands.

function sfDisplay(v) {
  if (v === true) return 'yes';
  if (v === false) return 'no';
  if (v && typeof v === 'object') {
    return Object.keys(v).map(k => k + ' ' + sfDisplay(v[k])).join(', ');
  }
  return String(v);
}

// Fields that say nothing useful in a one-line collapsed summary — provenance,
// prose, and plumbing. They still render inside the open section.
const SF_SUMMARY_SKIP = new Set(['source', 'checked', 'note', 'url', 'platform',
                                 'currency', 'nightly_high', 'closes']);

// A collapsed section shows its VALUES, not a count of them. It used to read
// "4 set", which on the Rating section is worse than useless: Prophetstown is a
// 5-star park whose chip said "4 set", and a bare number beside the word Rating
// reads as a score. The count also answered a question nobody asks.
function sfMoney(n, currency) {
  const sym = currency === 'CAD' ? 'C$' : '$';
  return sym + (Number.isInteger(n) ? n : Number(n).toFixed(2));
}

// "05-01" is how a recurring date has to be STORED (no year — doc §4), and it
// is not how anyone reads one. A popup saying "05-01 to 10-01" makes the reader
// decode two numbers before learning the season runs May to October.
const SF_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

function sfDate(mmdd) {
  const m = /^(\d{2})-(\d{2})$/.exec(String(mmdd || ''));
  if (!m) return String(mmdd);
  const name = SF_MONTHS[Number(m[1]) - 1];
  return name ? name + ' ' + Number(m[2]) : String(mmdd);
}

// What an entrance fee is charged PER changes what the number means: Indiana's
// $7 is once per camping stay and Michigan's $15 is a year's vehicle pass, and
// a chip printing only the amount reports them as the same kind of charge.
const SF_FEE_PER = {
  vehicle_day: ' per vehicle/day',
  vehicle_stay: ' per vehicle/stay',
  vehicle_year: ' per vehicle/year',
  person_day: ' per person/day',
};

const SF_SURCHARGE_LABELS = {
  electric: 'electric', water: 'water', sewer: 'sewer', full_hookup: 'full hookup',
  waterfront: 'waterfront', oceanfront: 'oceanfront', weekend: 'weekend',
  premium_site: 'premium site', pet: 'pet',
};

// A chip run reads as prose, so "showers · flush toilets" wants lower case —
// but "America the Beautiful Senior/Access" is a proper noun and lowercasing it
// looks like a typo rather than a style. An internal capital is what separates
// the two.
function sfLower(label) {
  return /[A-Z]/.test(label.slice(1)) ? label : label.toLowerCase();
}

// `cur` is the group's stored currency, which is skipped as a chip of its own
// and would otherwise make a Canadian park's "$27" read as US dollars.
function sfChip(groupKey, field, value, cur) {
  const k0 = groupKey + '.' + field.key;
  // "reservable" is true on almost every row and would spend one of the three
  // summary slots saying nothing. Its FALSE is worth a slot.
  if (k0 === 'booking.reservable') return value ? null : 'not reservable';
  // Booleans whose LABEL cannot carry the negative. "Open year-round" negates
  // to "no open year-round", which is not English; a season that isn't
  // year-round is a seasonal one, and that is the word a camper uses.
  if (k0 === 'season.year_round') return value ? 'open year-round' : 'seasonal';
  // Not "pull-through sites": the chip beside it is "110 sites", and the row is
  // headed Sites, so the noun is already said twice before this one lands.
  if (k0 === 'sites.pull_through') {
    return value ? 'pull-throughs' : 'no pull-throughs';
  }
  // A discount's label names the CLUB, not what it buys you, so the bare label
  // is a chip reading "good sam" next to "showers" — a reader who has never
  // heard of the club learns nothing, and one who has cannot tell whether it
  // means a discount, a rating or a listing (doc §8.7). The noun is what the
  // chip is for.
  if (groupKey === 'discounts' && field.key !== 'note') {
    const name = field.key === 'interagency_senior_access'
      ? 'America the Beautiful senior/access' : field.label;
    return (value ? '' : 'no ') + sfLower(name) + ' discount';
  }
  if (value === true) return sfLower(field.label);
  if (value === false) return 'no ' + sfLower(field.label);
  if (value === null || value === undefined) return null;
  const k = groupKey + '.' + field.key;
  if (k === 'rating.stars') return value + '\u2605';
  if (k === 'rating.price_tier') return value > 0 ? '$'.repeat(value) : 'free';
  if (k === 'hookups.electric') return value > 0 ? value + 'A' : 'no electric';
  if (k === 'sites.count') return value + ' sites';
  if (k === 'sites.max_rig_ft') return 'rigs to ' + value + ' ft';
  // Alone this is a date the gates open, not a span: "open May 15" reads as if
  // May 15 were the season. The span form is built in sfChips, where `closes`
  // is in hand.
  if (k === 'season.opens') return 'opens ' + sfDate(value);
  if (k === 'season.closes') return 'closes ' + sfDate(value);
  // Units spelled out. "180d ahead" and "max 14n" are the kind of shorthand
  // that reads as a typo to anyone who didn't write it, and both of these sit
  // in the agency half, where the reader is already being told something
  // indirect ("typical for ... , not checked here").
  if (k === 'booking.window_opens_days') return 'books ' + value + ' days ahead';
  if (k === 'booking.max_stay_nights') return 'max stay ' + value + ' nights';
  // nightly_high is skipped and folded in here, so a rate reads "$33-37"
  // rather than "$33 · $37" — two numbers that look like unrelated facts.
  if (k === 'fees.nightly_low') return sfMoney(value, cur);
  // NOT "res". The same Fees row can carry a non-resident surcharge, so "+$5
  // res" sat one chip away from "non-res +$5/night" meaning something entirely
  // different — Virginia prints both. A booking fee is what this is.
  if (k === 'fees.reservation_fee') {
    return '+' + sfMoney(value, cur) + ' booking fee';
  }
  // Raw enum values are meaningless alone: a Booking section reading "always"
  // tells you nothing about what is always true.
  if (k === 'booking.fcfs') {
    return {never: 'no walk-up sites', always: 'walk-ups welcome',
            after_cutoff: 'walk-ups after the booking cutoff',
            some_sites: 'some walk-up sites'}[value] || value;
  }
  // The generic array fallback renders this as "2 minimum stays", which reads
  // as a minimum of two stays and tells the reader nothing about when either
  // rule applies — and WHEN is the whole reason this field is a list rather
  // than a number (doc §4.1). The waiver that can lift a rule is deliberately
  // left to the section's note: a chip that promised one would have to explain
  // it, and a half-explained waiver is worse than an unmentioned one.
  if (k === 'booking.min_stay') {
    if (!Array.isArray(value) || !value.length) return null;
    const when = { weekend: ' on weekends', holiday: ' on holidays',
                   summer: ' in summer', always: '' };
    // "nights" is spelled on the first rule only: "min stay 2 nights on
    // weekends, 3 nights on holidays" says the unit twice for one fact.
    return 'min stay ' + value.map((r, i) => {
      const applies = when[r.applies] !== undefined ? when[r.applies]
                    : (r.applies ? ' ' + r.applies : '');
      const nights = r.nights != null ? r.nights + (i === 0 ? ' nights' : '') : '?';
      // `season` BOUNDS the rule, so dropping it states a summer-only minimum
      // as a year-round one — which is the stricter, wrong direction, and the
      // question a reader actually asks of Maryland and Pennsylvania (both run
      // their weekend minimum Memorial Day to Labor Day and neither has one
      // outside it). Verbatim, however long: these strings are prose because
      // the rule is ("July 4 when it falls Fri-Mon"), and paraphrasing a date
      // range is how a bound stops being true.
      const season = r.season ? ' (' + r.season + ')' : '';
      return nights + applies + season;
    }).join(', ');
  }
  // "closes 21:00" left the reader two questions \u2014 what closes, and 21:00 of
  // which day. It is the reservation window, and it shuts relative to ARRIVAL.
  if (k === 'booking.reserve_until') {
    if (value && value.at) return 'book by ' + value.at + ' on arrival day';
    if (value && value.offset_hours) {
      return 'book by ' + (-value.offset_hours) + 'h before arrival';
    }
    return 'has a booking cutoff';
  }
  // The two fee shapes that matter most read as bare labels otherwise.
  if (k === 'fees.nonresident') {
    if (value && value.type === 'multiplier') {
      return 'non-resident rate \u00d7' + value.factor;
    }
    if (value && value.amount != null) {
      return 'non-resident +' + sfMoney(value.amount, cur)
             + (value.per === 'night' ? '/night' : '/stay');
    }
    return 'non-resident surcharge';
  }
  // An entrance fee is charged per vehicle-day, per stay or per YEAR, and the
  // amount alone cannot be compared across those. Michigan's $15/$40 is an
  // annual pass and was reading as a gate fee charged on arrival.
  if (k === 'fees.entrance') {
    const r = value && value.resident, n = value && value.nonresident;
    const per = SF_FEE_PER[value && value.per] || '';
    const head = (value && value.per) === 'vehicle_year'
      ? 'annual park pass ' : 'park entry ';
    // Parenthesised so the basis doesn't run into the amounts: "$7 resident,
    // $15 non-resident per vehicle/stay" reads as if the $15 alone were per
    // vehicle. The year case says its basis in the head instead.
    const tail = (value && value.per) === 'vehicle_year' || !per
      ? '' : ' (' + per.trim() + ')';
    if (r != null && n != null) {
      return head + (r === n
        ? sfMoney(r, cur)
        : sfMoney(r, cur) + ' resident, ' + sfMoney(n, cur) + ' non-resident')
        + tail;
    }
    return head.trim() + ' fee' + tail;
  }
  // The name is what the reader has to go and get ("WMA camping authorization",
  // "Green Key"); a price alone read as an anonymous surcharge. A free pass
  // says free, and one with no stored price just names itself.
  if (k === 'fees.prereq_pass') {
    const name = value && value.name;
    const price = value && value.price != null
      ? (value.price === 0 ? 'free' : sfMoney(value.price, cur)
         + (value.valid ? '/' + value.valid : ''))
      : null;
    if (name) return 'requires ' + name + (price ? ' (' + price + ')' : '');
    return price ? 'requires ' + price + ' pass' : 'pass required';
  }
  if (Array.isArray(value)) {
    return value.length + ' ' + field.label.toLowerCase()
           + (value.length === 1 ? '' : 's');
  }
  if (value && typeof value === 'object') return field.label.toLowerCase();
  return String(value);
}

// Every chip a group's values yield, in the schema's own field order. Returned
// as an array rather than a joined string because the two callers cap it
// differently: a collapsed manage section is a teaser for the open section
// right below it, while a map popup is the only place a reader will ever see
// these values.
//
// `keys`, when given, restricts the chips to those field keys. That is how the
// popup separates what was verified for THIS campground from what its agency
// supplies, without having to format the two halves differently.
function sfChips(group, values, keys) {
  const parts = [];
  const has = k => (!keys || keys.has(k)) && k in values;
  const cur = values.currency;
  // Folds: a set of keys one chip already speaks for, so the run doesn't say
  // the same thing twice in different words.
  const folded = new Set();
  // "50A \u00b7 water \u00b7 sewer" is three chips for the thing every RV park advertises
  // as one. Dump stays its own chip \u2014 a site with full hookups may or may not
  // have one, so it is a separate fact, not part of this one.
  if (has('electric') && has('water') && has('sewer')) {
    if (values.electric > 0 && values.water === true && values.sewer === true) {
      parts.push('full hookups (' + values.electric + 'A)');
      folded.add('electric'); folded.add('water'); folded.add('sewer');
    } else if (values.electric === 0 && values.water === false
               && values.sewer === false) {
      // The same fold from the other end: "no electric · no water · no sewer"
      // is three chips to say the one thing a dry campground is.
      parts.push('no hookups');
      folded.add('electric'); folded.add('water'); folded.add('sewer');
    }
  }
  // A dated season already says it is seasonal; printing both gives
  // "seasonal \u00b7 open May 1 \u2013 Oct 1", where the first half is the second's
  // preamble. The bare flag still speaks when no dates are known.
  if (has('year_round') && values.year_round === false
      && (has('opens') || has('closes'))) {
    folded.add('year_round');
  }
  group.fields.forEach(f => {
    if (folded.has(f.key) || !(f.key in values)) return;
    if (keys && !keys.has(f.key)) return;
    // `closes` is skipped as a chip because it normally folds into `opens`
    // below \u2014 but a campground that recorded only a closing date would then
    // say nothing at all about its season.
    if (SF_SUMMARY_SKIP.has(f.key) && !(f.key === 'closes' && !has('opens'))) {
      return;
    }
    // Per-night add-ons are the fee a traveller actually pays on top, and one
    // chip reading "per-night amenity surcharges" told them only that some
    // exist. Each becomes its own chip so the run's cap trims the tail.
    if (f.key === 'surcharges' && values[f.key] && typeof values[f.key] === 'object') {
      Object.keys(values[f.key]).forEach(sk => {
        const amt = values[f.key][sk];
        if (amt == null) return;
        parts.push((SF_SURCHARGE_LABELS[sk] || sk.replace(/_/g, ' '))
                   + ' +' + sfMoney(amt, cur) + '/night');
      });
      return;
    }
    let chip = sfChip(group.key, f, values[f.key], cur);
    if (chip && f.key === 'nightly_low') {
      if (values.nightly_high != null && values.nightly_high !== values.nightly_low) {
        chip += '\u2013' + values.nightly_high;
      }
      chip += '/night';
    }
    // A season is one span, not two dates that happen to sit next to each other.
    if (chip && f.key === 'opens' && values.closes) {
      chip = 'open ' + sfDate(values[f.key]) + ' \u2013 ' + sfDate(values.closes);
    }
    if (chip) parts.push(chip);
  });
  return parts;
}

function sfSummary(group, values, limit = 3) {
  const parts = sfChips(group, values);
  if (!parts.length) return null;
  const shown = parts.slice(0, limit).join(' \u00b7 ');
  return parts.length > limit ? `${shown} +${parts.length - limit} more` : shown;
}
