import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401
import app

PIPELINE = """| Company | Role | Stage | Furthest | Applied | Last contact | Next action | Due | Source |
|---|---|---|---|---|---|---|---|---|
| Acme Inc. | PM | Screen | | 2026-03-01 | | | | x |
| Acme Inc. | Designer | Applied | | 2026-03-01 | | | | x |
| Gone | PM | Rejected | Interview | 2026-02-01 | | | | x |
| Won | PM | Withdrawn | Offer | 2026-02-01 | | | | x |
| Draft | PM | Drafted | | | | | | x |
| Odd | PM | whatever | | | | | | x |
"""


def project(files):
    folder = tempfile.TemporaryDirectory()
    root = Path(folder.name)
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return folder, root


class Progress(unittest.TestCase):
    def test_counts_are_per_application_and_survive_closing(self):
        folder, root = project({"applications/PIPELINE.md": PIPELINE,
                                "applications/acme/interview-notes.md": "notes",
                                "applications/elsewhere/interview-notes.md": "notes"})
        with folder:
            # Acme (Screen), Gone (reached Interview), Won (reached Offer), plus the "elsewhere" folder with no row
            self.assertEqual(app.progress_stats(root), {"applied": 4, "interviews": 4, "offers": 1})


class Roles(unittest.TestCase):
    def save(self, before, roles):
        folder, root = project({"profile/roles.md": before})
        with folder:
            app.save_roles(roles, root / "profile" / "roles.md")
            return (root / "profile" / "roles.md").read_text(encoding="utf-8"), app.target_roles(root)

    def test_only_the_list_between_the_markers_changes(self):
        before = ("# Target Roles\n\nRules:\n- one per line\n\n<!-- roles:start -->\n- Old\n  a note under Old\n- Kept\n"
                  "  a note under Kept\n<!-- roles:end -->\n\n## Later\n- not a role\n")
        after, roles = self.save(before, ["Kept", "New"])
        self.assertEqual(roles, ["Kept", "New"])
        self.assertEqual(after, before.replace("- Old\n  a note under Old\n- Kept\n  a note under Kept\n",
                                               "- Kept\n  a note under Kept\n- New\n"))

    def test_a_hand_written_file_gets_markers_around_its_list(self):
        after, roles = self.save("# Roles\n\nIntro.\n\n- A\n- B\n\nFooter.\n", ["B"])
        self.assertEqual(roles, ["B"])
        self.assertEqual(after, "# Roles\n\nIntro.\n\n<!-- roles:start -->\n- B\n<!-- roles:end -->\n\nFooter.\n")

    def test_empty_list_and_limits(self):
        after, roles = self.save(app.ROLES_TEMPLATE, [])
        self.assertEqual(roles, [])
        self.assertIn(app.NO_ROLE_YET, after)
        with self.assertRaises(ValueError):
            app.save_roles([str(i) for i in range(9)], Path(tempfile.gettempdir()) / "never-written-roles.md")


class Reading(unittest.TestCase):
    def test_only_markdown_inside_the_allowed_folders_is_readable(self):
        folder, root = project({"profile/a.md": "x", "scripts/b.md": "x", "profile/c.txt": "x"})
        with folder:
            self.assertIsNotNone(app.safe_md(root, "profile/a.md"))
            for path in ("scripts/b.md", "profile/c.txt", "../outside.md", "profile/../../etc/passwd"):
                self.assertIsNone(app.safe_md(root, path), path)

    def test_a_badly_encoded_file_does_not_crash(self):
        folder, root = project({})
        with folder:
            (root / "profile").mkdir()
            (root / "profile" / "resume.md").write_bytes(b"# Name\n\n\xff\xfe broken")
            self.assertIn("# Name", app.read(root, "profile/resume.md"))

    def test_the_shipped_template_and_example_load(self):
        self.assertFalse(app.state(app.ROOT)["example"])
        example = app.state(app.EXAMPLE)
        self.assertTrue(example["example"])
        self.assertEqual(example["pipeline"]["problems"], [])
        self.assertTrue(all(step["done"] for step in example["setup"]))


if __name__ == "__main__":
    unittest.main()
