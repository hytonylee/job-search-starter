import tempfile
import unittest
from datetime import date
from pathlib import Path

import helpers  # noqa: F401
import pipeline

TABLE = """# Pipeline

| Company | Role | Fit | Stage | Furthest | Applied | Last contact | Next action | Due | Source |
|---|---|---|---|---|---|---|---|---|---|
| Acme | PM | 4/5 | screen | | 2026-03-01 | 2026-03-10 | Prep | 2026-03-25 | x |
| Late | PM | 75% | Applied | | 2026-03-01 | | Follow up | 2026-03-15 | x |
| Quiet | PM | | Applied | | 2026-02-20 | | | | x |
| Gone | PM | 2 / 4 | Rejected | Technical | 2026-02-01 | 2026-02-20 | | | x |
| Won | PM | strong | Withdrawn | Offer | 2026-02-01 | 2026-02-25 | | | x |
|  | Orphan | 6/5 | Applied | | 2026-03-01 | | | | x |
| Odd | PM | 0/3 | interviewing | | Mar 3 | | | | x |
| | | | | | | | | | |
"""


def rows_from(text, today=date(2026, 3, 20)):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "PIPELINE.md"
        path.write_text(text, encoding="utf-8")
        return {row["company"]: row for row in pipeline.enrich(pipeline.read_rows(path), today)}


class Pipeline(unittest.TestCase):
    def setUp(self):
        self.rows = rows_from(TABLE)

    def test_blank_row_is_ignored_and_stage_is_normalised(self):
        self.assertEqual(len(self.rows), 7)
        self.assertEqual(self.rows["Acme"]["stage"], "Screen")

    def test_flags(self):
        self.assertEqual(self.rows["Late"]["flag"], "overdue 5d")
        self.assertEqual(self.rows["Quiet"]["flag"], "no reply 28d")
        self.assertEqual(self.rows["Acme"]["flag"], "")
        self.assertEqual(self.rows["Gone"]["flag"], "")

    def test_furthest_survives_a_closed_row(self):
        self.assertEqual(self.rows["Gone"]["furthest"], "Interview")  # "Technical" is the old name
        self.assertEqual(self.rows["Won"]["furthest"], "Offer")
        self.assertEqual(self.rows["Acme"]["furthest"], "Screen")

    def test_fit_score_is_read_as_a_percentage(self):
        percent = {name: row["fit_percent"] for name, row in self.rows.items()}
        self.assertEqual((percent["Acme"], percent["Late"], percent["Gone"], percent["Odd"]), (80, 75, 50, 0))
        self.assertIsNone(percent["Quiet"])            # blank is allowed
        self.assertIsNone(percent["Won"])              # not a score
        self.assertEqual(pipeline.fit_label(self.rows["Acme"]), "4/5 (80%)")
        self.assertEqual(pipeline.fit_label(self.rows["Gone"]), "2/4 (50%)")
        self.assertEqual(pipeline.fit_label(self.rows["Late"]), "75%")
        self.assertEqual(pipeline.fit_label(self.rows["Quiet"]), "")
        problems = " ".join(pipeline.problems(list(self.rows.values())))
        self.assertIn("fit 'strong' is not a score", problems)
        self.assertIn("fit '6/5' is not a score", problems)

    def test_funnel_counts_how_far_each_application_got_and_how_it_ended(self):
        result = pipeline.funnel(list(self.rows.values()))
        steps = {step["stage"]: step for step in result["steps"]}
        # Sent: Acme, Late, Quiet, Gone, Won and the orphan row. "Odd" has an unknown stage and is left out.
        self.assertEqual(result["sent"], 6)
        self.assertEqual([steps[s]["reached"] for s in ("Applied", "Screen", "Interview", "Final", "Offer")], [6, 3, 2, 1, 1])
        self.assertEqual([steps[s]["advanced"] for s in ("Applied", "Screen", "Interview", "Final", "Offer")], [3, 2, 1, 1, 0])
        self.assertEqual(steps["Applied"]["open"], 3)           # Late, Quiet, orphan: still waiting
        self.assertEqual(steps["Screen"]["open"], 1)            # Acme
        self.assertEqual(steps["Interview"]["rejected"], 1)     # Gone, rejected after an interview
        self.assertEqual(steps["Offer"]["withdrawn"], 1)        # Won, withdrew at the offer
        self.assertEqual(result["totals"], {"open": 4, "rejected": 1, "withdrawn": 1, "no_reply": 0})
        for step in result["steps"]:                             # every application is accounted for exactly once
            self.assertEqual(step["reached"], step["advanced"] + step["open"] + step["rejected"] + step["withdrawn"] + step["no_reply"])

    def test_funnel_leaves_out_drafts_and_flags_closed_rows_with_no_furthest(self):
        table = ("| Company | Role | Stage | Furthest |\n|---|---|---|---|\n| A | PM | Drafted | |\n| B | PM | Rejected | |\n"
                 "| C | PM | No reply | Applied |\n")
        result = pipeline.funnel(list(rows_from(table).values()))
        self.assertEqual((result["sent"], result["drafted"], result["assumed"]), (2, 1, 1))
        self.assertEqual(result["steps"][0]["rejected"], 1)
        self.assertEqual(result["steps"][0]["no_reply"], 1)
        self.assertEqual(pipeline.funnel([])["sent"], 0)

    def test_problems_are_reported_not_dropped(self):
        problems = " ".join(pipeline.problems(list(self.rows.values())))
        self.assertIn("has no company name", problems)
        self.assertIn("unknown stage 'interviewing'", problems)
        self.assertIn("is not YYYY-MM-DD", problems)

    def test_old_table_without_furthest_column_still_reads(self):
        old = "| Company | Role | Stage | Applied |\n|---|---|---|---|\n| Acme | PM | Final | 2026-03-01 |\n"
        self.assertEqual(rows_from(old)["Acme"]["furthest"], "Final")

    def test_a_badly_encoded_file_still_reads(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "PIPELINE.md"
            path.write_bytes(TABLE.encode("utf-8") + b"\n\xff\xfe stray bytes\n")
            self.assertEqual(len(pipeline.read_rows(path)), 7)

    def test_missing_table_raises(self):
        with self.assertRaises(pipeline.PipelineError):
            rows_from("# nothing here\n")


if __name__ == "__main__":
    unittest.main()
