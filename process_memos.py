#!/usr/bin/env python3
"""Transcribe voice memos with a local Whisper model.

Fills in `transcript` on each record in trip_data/memos.json. Step 2 of the
memo-to-rollup pipeline: step 1 files a recording against the right trip and
day, this turns it into text, and the rollup that eventually reads that text is
step 3.

This is an OFFLINE batch tool and the web app never imports faster_whisper —
same contract as detect_people.py and cv2, for the same reason: the model costs
hundreds of MB resident, which a one-shot process pays for seconds and a web
worker would pay for its whole life. The app does *trigger* this script on
upload (see _queue_memo_transcribe in ekko_trips_app.py), but it never does the
work itself.

    python process_memos.py                  # transcribe anything without text
    python process_memos.py --force          # redo them all
    python process_memos.py --only ID [ID]   # just these memo ids
    python process_memos.py --model small.en # trade speed for accuracy

Transcription stays LOCAL rather than going to a hosted speech API: it is free,
it works offline, and a family's unguarded speech never leaves the host. The
Claude API has no audio input, so the split between this and the rollup step
isn't a preference — it's the shape of what's available.

**A hand-edited transcript is never overwritten.** The app sets
`transcript_edited` when someone corrects the text, and even --force respects
it (--force-edited is the explicit override). A transcript is the input to the
rollup, so a correction you made is worth more than anything a re-run produces.

Incremental by design: a memo that already has text is skipped, so re-running
after new uploads only does the new ones. Results are merged into the JSON at
write time — re-read, then apply just this run's deltas — because the web app
edits the same file (filing a memo, deleting one) and, since it also triggers
this script, the two really can overlap.

Needs: pip install -r tools_requirements.txt (which also installs the app's
own requirements). faster_whisper is deliberately NOT in
ekko_trips_requirements.txt — the web app never imports it.
"""
import argparse
import json
import os
import sys
import time

_DIR = os.path.dirname(os.path.abspath(__file__))
MEMO_DIR = os.path.join(_DIR, "memo_uploads")
MEMOS_FILE = os.path.join(_DIR, "trip_data", "memos.json")
# Alongside detect_people.py's YuNet model, so one directory holds every
# downloaded model weight and backup.sh can keep ignoring all of it.
MODEL_DIR = os.path.join(_DIR, "trip_data", "models")

# base.en is the default because these are short, close-mic, English recordings
# of one person talking — the case the small models are already good at — and
# it runs several times faster than realtime on a CPU. Pass --model small.en if
# wind noise or road noise is costing you words.
DEFAULT_MODEL = "base.en"


def _load_memos():
    if not os.path.exists(MEMOS_FILE):
        return {}
    with open(MEMOS_FILE) as f:
        return json.load(f)


def _merge_and_write(updates):
    """Apply this run's deltas to the file on disk and return the result.

    Re-reads at write time rather than dumping the dict loaded at startup. The
    web app edits the same file — filing a memo, editing a note, deleting one —
    and it also triggers this script on upload, so the two genuinely overlap.
    Deltas are merged per-record rather than per-file so a memo re-filed while
    this ran keeps its new trip.
    """
    current = _load_memos()
    for memo_id, fields in updates.items():
        if memo_id not in current:
            continue          # deleted while we were transcribing; let it go
        current[memo_id].update(fields)
    tmp = MEMOS_FILE + f".{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2, ensure_ascii=False)
    os.replace(tmp, MEMOS_FILE)
    return current


def _memo_path(rec):
    return os.path.join(MEMO_DIR, rec.get("year", ""), rec.get("filename", ""))


def _needs_transcript(rec, force, force_edited):
    """Whether this memo should be (re)transcribed.

    A hand-corrected transcript outranks anything a re-run would produce, so it
    survives --force; only --force-edited overrides it.
    """
    if rec.get("transcript_edited") and not force_edited:
        return False
    if force or force_edited:
        return True
    return not (rec.get("transcript") or "").strip()


def _transcribe(model, path):
    """Return (text, detected_language, audio_seconds) for one recording."""
    segments, info = model.transcribe(path, beam_size=5, vad_filter=True)
    # faster-whisper yields segments lazily — the work happens on iteration.
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text, getattr(info, "language", ""), getattr(info, "duration", None)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true",
                    help="re-transcribe memos that already have text "
                         "(hand-edited ones are still skipped)")
    ap.add_argument("--force-edited", action="store_true",
                    help="also overwrite transcripts a human has corrected")
    ap.add_argument("--only", nargs="+", metavar="ID",
                    help="transcribe exactly these memo ids (the path the web "
                         "app uses after an upload)")
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help=f"Whisper model name (default {DEFAULT_MODEL})")
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="list what would be transcribed and stop")
    args = ap.parse_args()

    memos = _load_memos()
    if not memos:
        print("No memos to transcribe.")
        return 0

    if args.only:
        unknown = [m for m in args.only if m not in memos]
        if unknown:
            print(f"unknown memo id(s): {', '.join(unknown)}", file=sys.stderr)
        ids = [m for m in args.only if m in memos]
    else:
        ids = sorted(memos, key=lambda m: memos[m].get("recorded_at") or 0)

    todo = [m for m in ids
            if _needs_transcript(memos[m], args.force, args.force_edited)]
    if not todo:
        print(f"Nothing to do — {len(ids)} memo(s) already transcribed.")
        return 0

    print(f"{len(todo)} memo(s) to transcribe with {args.model}.")
    if args.dry_run:
        for memo_id in todo:
            print(f"  {memo_id}  {_memo_path(memos[memo_id])}")
        return 0

    # Imported after argparse so --help and --dry-run work without the model
    # installed — the same courtesy detect_people.py extends for cv2.
    from faster_whisper import WhisperModel
    os.makedirs(MODEL_DIR, exist_ok=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8",
                         download_root=MODEL_DIR)

    updates, failed = {}, 0
    for memo_id in todo:
        rec = memos[memo_id]
        path = _memo_path(rec)
        if not os.path.isfile(path):
            print(f"  missing audio, skipping: {memo_id}", file=sys.stderr)
            failed += 1
            continue
        began = time.time()
        try:
            text, lang, audio_s = _transcribe(model, path)
        except Exception as e:
            print(f"  failed: {memo_id} ({e})", file=sys.stderr)
            failed += 1
            continue
        took = time.time() - began
        fields = {
            "transcript": text,
            # Names what produced the text, which is the audit trail: a
            # generated transcript and a corrected one are different facts and
            # the record should say which it holds.
            "transcript_model": f"faster-whisper {args.model}",
            "transcript_at": int(time.time()),
            "transcript_lang": lang,
            "transcript_edited": False,
        }
        # The file-upload path can't know a recording's length, so fill it in
        # from what the decoder measured rather than leaving the list blank.
        if audio_s and not rec.get("duration_s"):
            fields["duration_s"] = round(audio_s, 1)
        updates[memo_id] = fields
        preview = (text[:70] + "…") if len(text) > 70 else (text or "(silence)")
        print(f"  {memo_id}  {took:5.1f}s  {preview}")

        # Written after every memo, not once at the end: a long batch that is
        # interrupted (a PA CPU limit, a closed console) keeps everything it
        # already did instead of starting over.
        _merge_and_write({memo_id: fields})

    done = len(updates)
    print(f"\nTranscribed {done} memo(s)"
          + (f", {failed} failed." if failed else "."))
    return 1 if failed and not done else 0


if __name__ == "__main__":
    sys.exit(main())
