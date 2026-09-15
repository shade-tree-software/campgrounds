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
function sfMoney(n) {
  return '$' + (Number.isInteger(n) ? n : Number(n).toFixed(2));
}

// A chip run reads as prose, so "showers · flush toilets" wants lower case —
// but "America the Beautiful Senior/Access" is a proper noun and lowercasing it
// looks like a typo rather than a style. An internal capital is what separates
// the two.
function sfLower(label) {
  return /[A-Z]/.test(label.slice(1)) ? label : label.toLowerCase();
}

function sfChip(groupKey, field, value) {
  const k0 = groupKey + '.' + field.key;
  // "reservable" is true on almost every row and would spend one of the three
  // summary slots saying nothing. Its FALSE is worth a slot.
  if (k0 === 'booking.reservable') return value ? null : 'not reservable';
  if (value === true) return sfLower(field.label);
  if (value === false) return 'no ' + sfLower(field.label);
  if (value === null || value === undefined) return null;
  const k = groupKey + '.' + field.key;
  if (k === 'rating.stars') return value + '\u2605';
  if (k === 'rating.price_tier') return value > 0 ? '$'.repeat(value) : 'free';
  if (k === 'hookups.electric') return value > 0 ? value + 'A' : 'no electric';
  if (k === 'sites.count') return value + ' sites';
  if (k === 'sites.max_rig_ft') return 'to ' + value + ' ft';
  if (k === 'booking.window_opens_days') return value + 'd ahead';
  if (k === 'booking.max_stay_nights') return 'max ' + value + 'n';
  // nightly_high is skipped and folded in here, so a rate reads "$33-37"
  // rather than "$33 · $37" — two numbers that look like unrelated facts.
  if (k === 'fees.nightly_low') return sfMoney(value);
  if (k === 'fees.reservation_fee') return '+' + sfMoney(value) + ' res';
  // Raw enum values are meaningless alone: a Booking section reading "always"
  // tells you nothing about what is always true.
  if (k === 'booking.fcfs') {
    return {never: 'no walk-ups', always: 'walk-ups',
            after_cutoff: 'walk-ups after cutoff',
            some_sites: 'some walk-ups'}[value] || value;
  }
  // The generic array fallback renders this as "2 minimum stays", which reads
  // as a minimum of two stays and tells the reader nothing about when either
  // rule applies — and WHEN is the whole reason this field is a list rather
  // than a number (doc §4.1). The waiver that can lift a rule is deliberately
  // left to the section's note: a chip that promised one would have to explain
  // it, and a half-explained waiver is worse than an unmentioned one.
  if (k === 'booking.min_stay') {
    if (!Array.isArray(value) || !value.length) return null;
    const when = { weekend: ' weekends', holiday: ' holidays',
                   summer: ' in summer', always: '' };
    return 'min ' + value.map(r => {
      const applies = when[r.applies] !== undefined ? when[r.applies]
                    : (r.applies ? ' ' + r.applies : '');
      return (r.nights != null ? r.nights + 'n' : '?') + applies;
    }).join(', ');
  }
  if (k === 'booking.reserve_until') {
    if (value && value.at) return 'closes ' + value.at;
    if (value && value.offset_hours) return 'closes ' + (-value.offset_hours) + 'h before';
    return 'has a cutoff';
  }
  // The two fee shapes that matter most read as bare labels otherwise.
  if (k === 'fees.nonresident') {
    if (value && value.type === 'multiplier') return 'non-res \u00d7' + value.factor;
    if (value && value.amount != null) {
      return 'non-res +' + sfMoney(value.amount) + (value.per === 'night' ? '/night' : '');
    }
    return 'non-res extra';
  }
  if (k === 'fees.entrance') {
    const r = value && value.resident, n = value && value.nonresident;
    if (r != null && n != null) {
      return r === n ? 'entry ' + sfMoney(r) : 'entry ' + sfMoney(r) + '/' + sfMoney(n);
    }
    return 'entry fee';
  }
  if (k === 'fees.prereq_pass') {
    return 'pass ' + (value && value.price != null ? sfMoney(value.price) : '$?');
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
  group.fields.forEach(f => {
    if (SF_SUMMARY_SKIP.has(f.key) || !(f.key in values)) return;
    if (keys && !keys.has(f.key)) return;
    let chip = sfChip(group.key, f, values[f.key]);
    if (chip && f.key === 'nightly_low' && values.nightly_high != null
        && values.nightly_high !== values.nightly_low) {
      chip += '-' + values.nightly_high;
    }
    // A season is one span, not two dates that happen to sit next to each other.
    if (chip && f.key === 'opens' && values.closes) {
      chip += ' to ' + values.closes;
    }
    if (chip) parts.push(chip);
  });
  return parts;
}

function sfSummary(group, values, limit = 3) {
  const parts = sfChips(group, values);
  if (!parts.length) return null;
  const shown = parts.slice(0, limit).join(' \u00b7 ');
  return parts.length > limit ? `${shown} +${parts.length - limit}` : shown;
}
