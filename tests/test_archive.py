import tempfile
import unittest
from datetime import date
from pathlib import Path

import helpers  # noqa: F401
import archive

LOG = """# Daily Log

Intro text.

<!-- Entry format:
## YYYY-MM-DD
-->

## 2026-03-19

recent entry

## 2026-01-05

old entry

## Running notes

- stays at the bottom
"""


class ArchiveLog(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        (root / "progress").mkdir()
        self.saved = (archive.ROOT, archive.LOG, archive.LOG_ARCHIVE)
        archive.ROOT, archive.LOG, archive.LOG_ARCHIVE = root, root / "progress" / "daily-log.md", root / "progress" / "_archive"
        archive.LOG.write_text(LOG, encoding="utf-8")

    def tearDown(self):
        archive.ROOT, archive.LOG, archive.LOG_ARCHIVE = self.saved
        self.folder.cleanup()

    def test_dry_run_changes_nothing(self):
        report, moved = archive.archive_log(date(2026, 2, 18), apply=False)
        self.assertEqual(moved, 1)
        self.assertEqual(archive.LOG.read_text(encoding="utf-8"), LOG)

    def test_only_the_old_entry_moves_and_order_is_kept(self):
        archive.archive_log(date(2026, 2, 18), apply=True)
        self.assertEqual(archive.LOG.read_text(encoding="utf-8"), LOG.replace("## 2026-01-05\n\nold entry\n\n", ""))
        archived = (archive.LOG_ARCHIVE / "daily-log-2026.md").read_text(encoding="utf-8")
        self.assertIn("old entry", archived)
        self.assertNotIn("stays at the bottom", archived)

    def test_second_run_is_a_no_op(self):
        archive.archive_log(date(2026, 2, 18), apply=True)
        once = archive.LOG.read_text(encoding="utf-8")
        report, moved = archive.archive_log(date(2026, 2, 18), apply=True)
        self.assertEqual(moved, 0)
        self.assertEqual(archive.LOG.read_text(encoding="utf-8"), once)


if __name__ == "__main__":
    unittest.main()
