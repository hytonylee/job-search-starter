"""Markdown to HTML for resumes and the dashboard. This file is not a command.

Supports headings, paragraphs, bullet and numbered lists (nested), **bold**,
*italic*, `code`, [links](https://example.com), --- rules and tables.
"""

import html
import re

from common import is_separator, split_cells

SAFE_SCHEMES = ("http", "https", "mailto", "tel")
SCHEME = re.compile(r"^([a-zA-Z][a-zA-Z0-9+.-]*):")
BARE_DOMAIN = re.compile(r"^[\w-]+(\.[\w-]+)+(/|$)")


def clean_markdown(text):
    """Drop HTML comments, trailing spaces and runs of blank lines."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = [line.rstrip() if not line.endswith("  ") else line.rstrip() + "  "
             for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def link(match):
    """Render [text](url). A url with a scheme outside SAFE_SCHEMES, such as javascript:, becomes plain text."""
    label = match.group(1)
    url = re.sub(r"[\x00-\x20\x7f]", "", match.group(2)).replace('"', "%22")  # browsers ignore control characters in a scheme
    scheme = SCHEME.match(url)
    if scheme and scheme.group(1).lower() not in SAFE_SCHEMES:
        return label
    if not scheme and BARE_DOMAIN.match(url):
        url = "https://" + url  # resumes often write linkedin.com/in/name without the scheme
    return f'<a href="{url}" rel="noopener noreferrer">{label}</a>'


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(((?:[^()\s]|\([^()\s]*\))+)\)", link, text)  # url may hold one level of ( )
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*(?!\*)", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    return text


def to_html(markdown):
    """Convert prose Markdown (everything except tables)."""
    out, paragraph, open_lists = [], [], []  # open_lists: stack of (indent, tag)
    after_blank = False                      # a blank line was seen while a list was still open

    def flush():
        if paragraph:
            out.append("<p>" + "".join(paragraph).rstrip() + "</p>")
            paragraph.clear()

    def close_lists(deeper_than=-1):
        while open_lists and open_lists[-1][0] > deeper_than:
            out.append(f"</{open_lists.pop()[1]}>")

    for line in markdown.splitlines():
        if not line.strip():
            flush()
            after_blank = bool(open_lists)  # the list stays open: the next line decides whether it continues
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        rule = re.match(r"^\s*([-*_])(\s?\1){2,}\s*$", line)
        item = None if rule else re.match(r"^(\s*)([-*+]|(\d{1,3})[.)])\s+(.*)$", line)  # 1-3 digits, so "2019. " is prose
        if item and item.group(3) and item.group(3) != "1" and paragraph:
            item = None  # only "1." may interrupt a paragraph, as in standard Markdown
        if open_lists and not (heading or rule or item) and (line[:1].isspace() or not after_blank):
            # Still inside the item above: a wrapped line, or a further paragraph indented under it.
            out[-1] += ("<br><br>" if after_blank else " ") + inline(line.strip())
            after_blank = False
            continue
        after_blank = False
        if heading:
            flush()
            close_lists()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2).strip())}</h{level}>")
        elif rule:
            flush()
            close_lists()
            out.append("<hr>")
        elif item:
            flush()
            indent = len(item.group(1).expandtabs(4))
            tag = "ol" if item.group(3) else "ul"
            close_lists(indent)
            if open_lists and open_lists[-1] == (indent, "ul" if tag == "ol" else "ol"):
                out.append(f"</{open_lists.pop()[1]}>")  # same depth, list type changed
            if not open_lists or open_lists[-1][0] < indent:
                open_lists.append((indent, tag))
                start = f' start="{item.group(3)}"' if tag == "ol" and item.group(3) != "1" else ""
                out.append(f"<{tag}{start}>")
            out.append("<li>" + inline(item.group(4).strip()))
        else:
            close_lists()
            hard_break = line.endswith("  ") or line.endswith("\\")
            paragraph.append(inline(line.rstrip("\\").strip()) + ("<br>" if hard_break else " "))
    flush()
    close_lists()
    return "\n".join(out)


def table_html(lines):
    rows = [cells for cells in map(split_cells, lines) if not is_separator(cells)]
    if not rows:
        return ""
    head = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
    return f'<div class="wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_md(text):
    """Convert a whole document, tables included, for the dashboard."""
    blocks, table, prose = [], [], []

    def flush_prose():
        if prose:
            blocks.append(to_html("\n".join(prose)))
            prose.clear()

    def flush_table():
        if table:
            blocks.append(table_html(table))
            table.clear()

    for line in clean_markdown(text).splitlines():
        if line.strip().startswith("|"):
            flush_prose()
            table.append(line)
        else:
            flush_table()
            prose.append(line)
    flush_prose()
    flush_table()
    return "\n".join(block for block in blocks if block)
