import unittest

import helpers  # noqa: F401
import commands


class Keywords(unittest.TestCase):
    def test_every_keyword_has_a_mode_file_with_a_purpose(self):
        rows = commands.keywords()
        self.assertGreaterEqual(len(rows), 19)
        for keyword, purpose in rows:
            self.assertTrue(commands.mode_file(keyword).exists(), keyword)
            self.assertNotIn("no mode file", purpose, keyword)

    def test_every_mode_file_is_listed_in_agents_md(self):
        listed = {commands.mode_file(keyword).name for keyword, _ in commands.keywords()}
        on_disk = {path.name for path in commands.MODES.glob("*.md")}
        self.assertEqual(listed, on_disk)

    def test_every_script_flag_is_in_its_usage_text(self):
        for name, _, usage in commands.script_commands():
            source = (commands.SCRIPTS / name).read_text(encoding="utf-8")
            shown = " ".join(command for command, _ in usage)
            for flag in __import__("re").findall(r'add_argument\("(--[a-z-]+)"', source):
                self.assertIn(flag, shown, f"{name} {flag}")


if __name__ == "__main__":
    unittest.main()
