import unittest

import helpers  # noqa: F401  (adds scripts/ to the import path)
import render


class Links(unittest.TestCase):
    def test_unsafe_schemes_become_plain_text(self):
        for url in ("javascript:alert(1)", "JaVaScRiPt:alert(1)", "data:text/html,x", "vbscript:x"):
            self.assertNotIn("href", render.inline(f"[label]({url})"), url)

    def test_safe_links_are_kept(self):
        self.assertIn('href="https://a.example/x?b=1&amp;c=2"', render.inline("[t](https://a.example/x?b=1&c=2)"))
        self.assertIn('href="mailto:a@example.com"', render.inline("[t](mailto:a@example.com)"))

    def test_control_characters_cannot_hide_a_scheme(self):
        for url in ("\x01javascript:alert(1)", "java\x00script:alert(1)", "\x1fjavascript:x"):
            self.assertNotIn("href", render.inline(f"[label]({url})"), repr(url))

    def test_bare_domain_gets_https(self):
        self.assertIn('href="https://linkedin.com/in/x"', render.inline("[t](linkedin.com/in/x)"))

    def test_html_is_escaped(self):
        self.assertNotIn("<script>", render.render_md("<script>alert(1)</script>"))
        self.assertNotIn("<script>", render.render_md("| a |\n|---|\n| <script>x</script> |"))


class Lists(unittest.TestCase):
    def test_numbered_list(self):
        html = render.to_html("1. one\n2. two")
        self.assertEqual(html.count("<li>"), 2)
        self.assertIn("<ol>", html)

    def test_a_year_inside_a_paragraph_is_not_a_list(self):
        html = render.to_html("I worked there until\n2019. Then I left.")
        self.assertNotIn("<ol", html)
        self.assertIn("2019. Then I left.", html)

    def test_a_year_on_its_own_line_is_not_a_list(self):
        self.assertNotIn("<ol", render.to_html("2019. Joined the company."))

    def test_four_space_nesting_keeps_items_inside_the_list(self):
        html = render.to_html("- a\n    - b\n- c").replace("\n", "")
        self.assertEqual(html, "<ul><li>a<ul><li>b</ul><li>c</ul>")

    def test_bold_italic_nests_correctly(self):
        self.assertEqual(render.inline("***x***"), "<strong><em>x</em></strong>")
        self.assertEqual(render.inline("**a *b***"), "<strong>a <em>b</em></strong>")

    def test_a_wrapped_item_does_not_lose_the_items_after_it(self):
        self.assertEqual(render.to_html("1. one\ncontinued\n2. two").replace("\n", ""), "<ol><li>one continued<li>two</ol>")

    def test_a_paragraph_inside_an_item_keeps_the_list_going(self):
        html = render.to_html("1. a\n\n   more\n2. b").replace("\n", "")
        self.assertEqual(html, "<ol><li>a<br><br>more<li>b</ol>")

    def test_text_after_a_blank_line_ends_the_list(self):
        self.assertEqual(render.to_html("- a\n\nAfter").replace("\n", ""), "<ul><li>a</ul><p>After</p>")


if __name__ == "__main__":
    unittest.main()
