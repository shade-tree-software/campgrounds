---
name: feedback-attribute-note-edits
description: "When editing a campground note already tagged with initials, attribute your own additions distinctly"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c8ea6a71-08f2-45a1-8ff8-4a363d1ac421
---

When updating an existing campground `note` in `campgrounds.json` that already carries someone's name or initials (e.g. `--AWH`), do NOT fold your changes into their tagged text. Keep their original note (and tag) intact and append your update as a distinct, separately-attributed segment — e.g. `... --AWH  [Correction/Update: ... --Claude]`.

**Why:** notes are a shared record; attribution lets the team see who wrote/changed what. A prior edit rewrote an `--AWH` note in place (Grindstone, id 525) and left the `--AWH` tag on the whole thing, making a Claude correction look like AWH's words.

**How to apply:** leave existing tagged text verbatim; add new content with your own marker (`--Claude`). Use a bracketed segment when correcting/contradicting the original so the change is obvious.
