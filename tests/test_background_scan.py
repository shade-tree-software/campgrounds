"""The catch-up sweep must heal a stuck item exactly once per process.

Work is normally triggered at upload time. That silently does nothing when the
dependency isn't installed yet or the worker recycles inside the debounce
window — and nothing ever revisited it, so a memo uploaded before
`faster-whisper` was installed said "Not transcribed yet" through every page
reload, forever. `queue_once` sweeps from the read path to fix that class of
problem rather than that instance.

The guard is the load-bearing half. Without it a key whose work genuinely
cannot succeed — audio deleted, or a host with no model — re-triggers a
subprocess and a several-hundred-MB model load on every single page view.

Run from the project root with the venv active:

    python -m unittest tests.test_background_scan -v
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ekko_trips_app import _BackgroundScan  # noqa: E402


def _scan(enabled=True):
    """A scan object that records what it would queue instead of spawning
    threads or subprocesses."""
    s = _BackgroundScan(name="test", script="/nonexistent.py",
                        probe_imports="json", debounce_s=0, max_batch=10,
                        timeout_s=1, enabled=enabled)
    s.queued = []
    s.queue = s.queued.append          # stand in for the real queue()
    return s


class TestQueueOnce(unittest.TestCase):
    def test_fresh_keys_are_queued(self):
        s = _scan()
        s.queue_once(["a", "b"])
        self.assertEqual(s.queued, [["a", "b"]])

    def test_a_key_is_never_queued_twice_in_one_process(self):
        # The stuck-forever fix must not become a treadmill: this is what keeps
        # a page refresh from starting a model load every time.
        s = _scan()
        s.queue_once(["a"])
        s.queue_once(["a"])
        s.queue_once(["a"])
        self.assertEqual(s.queued, [["a"]])

    def test_only_the_new_keys_of_a_mixed_batch_go_through(self):
        s = _scan()
        s.queue_once(["a", "b"])
        s.queue_once(["b", "c"])
        self.assertEqual(s.queued, [["a", "b"], ["c"]])

    def test_nothing_new_queues_nothing_at_all(self):
        # An empty call must not reach queue() — every page load makes one.
        s = _scan()
        s.queue_once(["a"])
        s.queue_once(["a"])
        self.assertEqual(len(s.queued), 1)

    def test_empty_input_is_a_no_op(self):
        s = _scan()
        s.queue_once([])
        self.assertEqual(s.queued, [])

    def test_disabled_scan_queues_nothing_and_marks_nothing(self):
        # EKKO_AUTO_TRANSCRIBE=0. Marking as tried while disabled would mean a
        # host that later enables it still skips everything already swept.
        s = _scan(enabled=False)
        s.queue_once(["a"])
        self.assertEqual(s.queued, [])
        s.enabled = True
        s.queue_once(["a"])
        self.assertEqual(s.queued, [["a"]])

    def test_the_guard_is_per_process_so_a_restart_retries(self):
        # A restart is precisely what follows installing the missing dependency,
        # so it must be what clears the guard.
        s1 = _scan()
        s1.queue_once(["a"])
        s2 = _scan()               # stands in for a fresh worker process
        s2.queue_once(["a"])
        self.assertEqual(s2.queued, [["a"]])


class TestConfiguration(unittest.TestCase):
    """Both real instances must stay pointed at their own script and deps —
    the refactor that merged this machinery is exactly where that could slip."""

    def test_both_scans_are_configured_independently(self):
        from ekko_trips_app import _people_scan, _memo_transcribe
        self.assertTrue(_people_scan.script.endswith("detect_people.py"))
        self.assertEqual(_people_scan.probe_imports, "cv2, numpy, PIL")
        self.assertTrue(_memo_transcribe.script.endswith("process_memos.py"))
        self.assertEqual(_memo_transcribe.probe_imports, "faster_whisper")
        self.assertIsNot(_people_scan._tried, _memo_transcribe._tried)


if __name__ == "__main__":
    unittest.main()
