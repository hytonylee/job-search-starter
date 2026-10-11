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


OLD_ARCHIVE = """# Pipeline Archive

| Company | Role | Stage | Applied | Last contact | Next action | Due | Source |
|---|---|---|---|---|---|---|---|
| Earlier | PM | Rejected | 2025-11-01 | 2025-11-20 | | | x |
"""
PIPELINE = """# Pipeline

- a bullet above the table

| Company | Role | Stage | Furthest | Applied | Last contact | Next action | Due | Source |
|---|---|---|---|---|---|---|---|---|
| Open | PM | Screen | | 2026-03-01 | 2026-03-10 | Prep | | x |
| Lost | PM | Rejected | Interview | 2026-01-05 | 2026-01-20 | | | x |
| Won | PM | Withdrawn | Offer | 2026-01-05 | 2026-01-25 | | | x |
| Undated | PM | No reply | | | | | | x |
"""


class ArchiveMore(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        root = Path(self.folder.name)
        for name in ("progress", "applications/_archive"):
            (root / name).mkdir(parents=True)
        self.saved = {name: getattr(archive, name) for name in ("ROOT", "LOG", "LOG_ARCHIVE", "PIPELINE", "PIPELINE_ARCHIVE")}
        archive.ROOT, archive.LOG, archive.LOG_ARCHIVE = root, root / "progress" / "daily-log.md", root / "progress" / "_archive"
        archive.PIPELINE = root / "applications" / "PIPELINE.md"
        archive.PIPELINE_ARCHIVE = root / "applications" / "_archive" / "PIPELINE-ARCHIVE.md"
        self.root = root

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(archive, name, value)
        self.folder.cleanup()

    def test_a_top_level_heading_after_an_entry_stays_in_the_log(self):
        archive.LOG.write_text("# Log\n\n## 2026-01-05\n\nold\n\n# Reference\n\nkeep this\n", encoding="utf-8")
        archive.archive_log(date(2026, 2, 18), apply=True)
        self.assertEqual(archive.LOG.read_text(encoding="utf-8"), "# Log\n\n# Reference\n\nkeep this\n")

    def test_closed_rows_move_and_totals_survive_an_older_archive_file(self):
        import app
        archive.PIPELINE.write_text(PIPELINE, encoding="utf-8")
        archive.PIPELINE_ARCHIVE.write_text(OLD_ARCHIVE, encoding="utf-8")  # written before the Furthest column existed
        before = app.progress_stats(self.root)
        report, moved = archive.archive_pipeline(date(2026, 2, 18), apply=True)
        self.assertEqual(moved, 2)
        remaining = archive.PIPELINE.read_text(encoding="utf-8")
        self.assertIn("| Open |", remaining)
        self.assertIn("| Undated |", remaining)       # closed but undated: left in place
        self.assertIn("- a bullet above the table", remaining)
        self.assertNotIn("| Lost |", remaining)
        rows = app.pipeline_rows(self.root, "applications/_archive/PIPELINE-ARCHIVE.md")
        self.assertEqual([r["company"] for r in rows if r["issues"]], [])   # one header, every row fits it
        self.assertEqual(len(rows), 3)
        self.assertEqual(app.progress_stats(self.root), before)
        self.assertEqual(before, {"applied": 5, "interviews": 3, "offers": 1})

    def test_run_keeps_days_in_range(self):
        archive.LOG.write_text("# Log\n", encoding="utf-8")
        archive.PIPELINE.write_text(PIPELINE, encoding="utf-8")
        self.assertEqual(archive.run(-5, False)["days"], 1)
        self.assertEqual(archive.run(10 ** 9, False)["days"], archive.MAX_DAYS)
        self.assertEqual(archive.PIPELINE.read_text(encoding="utf-8"), PIPELINE)   # a dry run changes nothing


if __name__ == "__main__":
    unittest.main()
