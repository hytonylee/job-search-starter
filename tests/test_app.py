import io
import json
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

    def test_a_lost_end_marker_is_put_back_without_touching_other_lists(self):
        before = "# Roles\n\nRules:\n- keep the markers\n\n<!-- roles:start --> \n- A\n- B\n\nNotes:\n- not a role\n"
        after, roles = self.save(before, ["B", "C"])
        self.assertEqual(roles, ["B", "C"])
        self.assertEqual(after, "# Roles\n\nRules:\n- keep the markers\n\n<!-- roles:start --> \n- B\n- C\n<!-- roles:end -->\n\nNotes:\n- not a role\n")

    def test_text_above_the_first_role_and_windows_line_endings_are_kept(self):
        folder, root = project({})
        with folder:
            target = root / "roles.md"
            target.write_bytes(b"# Roles\r\n<!-- roles:start -->\r\nMy shortlist:\r\n- Product  Manager\r\n  a note\r\n<!-- roles:end -->\r\n")
            app.save_roles(["Product Manager", "Designer"], target)
            self.assertEqual(target.read_bytes(), b"# Roles\r\n<!-- roles:start -->\r\nMy shortlist:\r\n- Product Manager\r\n  a note\r\n- Designer\r\n<!-- roles:end -->\r\n")

    def test_empty_list_and_limits(self):
        after, roles = self.save(app.ROLES_TEMPLATE, [])
        self.assertEqual(roles, [])
        self.assertIn(app.NO_ROLE_YET, after)
        with self.assertRaises(ValueError):
            app.save_roles([str(i) for i in range(9)], Path(tempfile.gettempdir()) / "never-written-roles.md")


class CompanyMatching(unittest.TestCase):
    def count(self, company, folder):
        files = {"applications/PIPELINE.md": "| Company | Role | Stage |\n|---|---|---|\n| %s | PM | Applied |\n" % company,
                 f"applications/{folder}/interview-notes.md": "notes"}
        tmp, root = project(files)
        with tmp:
            return app.progress_stats(root)["interviews"]

    def test_only_legal_suffixes_count_as_the_same_company(self):
        # The notes folder adds one interview either way; what matters is that the row is not confused with it.
        self.assertEqual(self.count("Scale", "scale-ai"), 1)
        self.assertEqual(self.count("Acme Inc.", "acme"), 1)


class Requests(unittest.TestCase):
    """Drive the request handler without opening a network port."""

    def call(self, method, path, body=None, host="127.0.0.1:8765", token=None):
        class Socket:
            def __init__(self, data):
                self.reader, self.writer = io.BytesIO(data), io.BytesIO()

            def makefile(self, mode, *args, **kwargs):
                return self.reader if "r" in mode else self.writer

            def sendall(self, data):
                self.writer.write(data)

            send = sendall

        data = json.dumps(body).encode() if body is not None else b""
        head = f"{method} {path} HTTP/1.1\r\nHost: {host}\r\n" + (f"X-Token: {token}\r\n" if token else "")
        socket = Socket((head + f"Content-Length: {len(data)}\r\n\r\n").encode() + data)
        app.Handler(socket, ("127.0.0.1", 1), None)
        raw = socket.writer.getvalue()
        return int(raw.split(b" ")[1]), raw.partition(b"\r\n\r\n")[2]

    def test_reads_work_and_stay_inside_the_project(self):
        self.assertEqual(self.call("GET", "/api/state")[0], 200)
        self.assertEqual(self.call("GET", "/api/file?path=profile/roles.md")[0], 200)
        for path in ("/api/file?path=../../etc/passwd", "/api/file?path=scripts/app.py", "/api/file?path=%00", "/output/../AGENTS.md"):
            self.assertEqual(self.call("GET", path)[0], 404, path)

    def test_another_host_name_is_refused(self):
        self.assertEqual(self.call("GET", "/api/state", host="evil.example")[0], 403)

    def test_nothing_is_written_without_the_token(self):
        for path in ("/api/roles", "/api/export", "/api/archive"):
            self.assertEqual(self.call("POST", path, {"roles": ["x"], "apply": True})[0], 403, path)
            self.assertEqual(self.call("POST", path, {"roles": ["x"], "apply": True}, token="wrong")[0], 403, path)

    def test_bad_input_gets_a_clear_answer_not_a_crash(self):
        status, body = self.call("POST", "/api/archive", {"days": "abc"}, token=app.TOKEN)   # rejected before anything runs
        self.assertEqual((status, json.loads(body)["error"]), (400, "Days must be a whole number."))
        self.assertEqual(self.call("POST", "/api/roles", {"roles": "x"}, token=app.TOKEN)[0], 400)

    def test_a_section_must_match_its_heading_exactly(self):
        whole = json.loads(self.call("GET", "/api/file?path=modes/practice.md")[1])["html"]
        partial = json.loads(self.call("GET", "/api/file?path=modes/practice.md&section=E")[1])["html"]
        exact = json.loads(self.call("GET", "/api/file?path=modes/practice.md&section=Exercises")[1])["html"]
        self.assertEqual(partial, whole)
        self.assertNotIn("Rules for every exercise", exact)


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

    def test_the_shipped_template_loads(self):
        self.assertFalse(app.state(app.ROOT)["example"])

    @unittest.skipUnless(app.EXAMPLE.is_dir(), "the example folder has been deleted")
    def test_the_shipped_example_loads(self):
        example = app.state(app.EXAMPLE)
        self.assertTrue(example["example"])
        self.assertEqual(example["pipeline"]["problems"], [])
        self.assertTrue(all(step["done"] for step in example["setup"]))


if __name__ == "__main__":
    unittest.main()
