#!/usr/bin/env python3
"""Export a resume from Markdown to clean Markdown, HTML and PDF.

Usage:
  python3 scripts/resume.py                export profile/resume.md
  python3 scripts/resume.py acme           export applications/acme/resume.md
  python3 scripts/resume.py acme --open    export, then open the result
  python3 scripts/resume.py --paper a4     A4 instead of US Letter

Files are written to output/resume/general/ or output/resume/<company>/ and are
named after the first "# Heading" in the resume, e.g. Jane-Doe-Resume.pdf.

Needs Python 3.8+. The PDF step uses a Chromium-based browser that is already
installed (Chrome, Chromium, Edge or Brave). Without one, open the .html file
and use Print > Save as PDF.

Supported Markdown: headings, paragraphs, bullet lists (nested), **bold**,
*italic*, `code`, [links](https://example.com) and --- rules. No tables or images.
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "profile" / "resume.md"
APPLICATIONS = ROOT / "applications"
OUTPUT = ROOT / "output" / "resume"

BROWSER_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
BROWSER_COMMANDS = ["google-chrome", "google-chrome-stable", "chromium",
                    "chromium-browser", "microsoft-edge", "brave-browser"]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  @page { size: __PAPER__; margin: 0.55in 0.65in; }
  body { font: 10.5pt/1.4 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
         color: #111; background: #fff; max-width: 7.2in; margin: 0 auto; }
  @media screen { body { padding: 32px 16px; } }
  h1 { font-size: 20pt; line-height: 1.2; margin: 0 0 3pt; }
  h2 { font-size: 10.5pt; text-transform: uppercase; letter-spacing: .06em;
       border-bottom: 1px solid #999; padding-bottom: 2pt; margin: 12pt 0 5pt; }
  h3 { font-size: 10.5pt; margin: 8pt 0 1pt; }
  h4 { font-size: 10.5pt; font-weight: normal; font-style: italic; margin: 0 0 2pt; }
  p { margin: 0 0 4pt; }
  ul { margin: 2pt 0 6pt; padding-left: 14pt; }
  li { margin-bottom: 1.5pt; break-inside: avoid; }
  h2, h3, h4 { break-after: avoid; }
  a { color: inherit; text-decoration: none; }
  code { font-family: inherit; }
  hr { border: 0; border-top: 1px solid #999; margin: 8pt 0; }
</style>
</head>
<body>
__BODY__
</body>
</html>
"""


def clean_markdown(text):
    """Drop HTML comments, trailing spaces and runs of blank lines."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = [line.rstrip() if not line.endswith("  ") else line.rstrip() + "  "
             for line in text.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip() + "\n"


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: '<a href="%s">%s</a>' % (m.group(2).replace('"', "%22"), m.group(1)),
                  text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<em>\1</em>", text)
    return text


def to_html(markdown):
    """Convert the small Markdown subset a resume needs."""
    out, paragraph, depth = [], [], 0

    def flush():
        if paragraph:
            out.append("<p>" + "".join(paragraph).rstrip() + "</p>")
            paragraph.clear()

    def set_depth(target):
        nonlocal depth
        while depth < target:
            out.append("<ul>")
            depth += 1
        while depth > target:
            out.append("</ul>")
            depth -= 1

    for line in markdown.splitlines():
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        bullet = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if not line.strip():
            flush()
            set_depth(0)
        elif heading:
            flush()
            set_depth(0)
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2).strip())}</h{level}>")
        elif re.match(r"^\s*([-*_])\1{2,}\s*$", line):
            flush()
            set_depth(0)
            out.append("<hr>")
        elif bullet:
            flush()
            set_depth(len(bullet.group(1).expandtabs(4)) // 2 + 1)
            out.append("<li>" + inline(bullet.group(2).strip()))
        elif depth and line[:1].isspace():  # wrapped line of the bullet above
            out[-1] += " " + inline(line.strip())
        else:
            set_depth(0)
            hard_break = line.endswith("  ") or line.endswith("\\")
            paragraph.append(inline(line.rstrip("\\").strip()) + ("<br>" if hard_break else " "))
    flush()
    set_depth(0)
    return "\n".join(out)


def find_browser():
    for path in BROWSER_PATHS:
        if Path(path).exists():
            return path
    for command in BROWSER_COMMANDS:
        found = shutil.which(command)
        if found:
            return found
    return None


def make_pdf(html_path, pdf_path):
    """Print the HTML to PDF with a headless browser. Returns "" or the reason it failed."""
    browser = find_browser()
    if not browser:
        return "no Chrome, Chromium, Edge or Brave was found"
    if pdf_path.exists():
        pdf_path.unlink()
    with tempfile.TemporaryDirectory() as profile:  # own profile, so a running browser is not disturbed
        command = [browser, "--headless", "--disable-gpu", "--no-first-run",
                   f"--user-data-dir={profile}", "--no-pdf-header-footer",
                   "--print-to-pdf-no-header", f"--print-to-pdf={pdf_path}",
                   html_path.as_uri()]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
        except (OSError, subprocess.TimeoutExpired) as error:
            return f"{Path(browser).name} could not run ({type(error).__name__})"
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        return ""
    return f"{Path(browser).name} ran but produced no file"


class ExportError(Exception):
    """A problem the user can fix, such as a missing or placeholder resume."""


def pick_source(company):
    if not company:
        return BASE
    source = APPLICATIONS / company / "resume.md"
    if source.exists():
        return source
    available = sorted(p.parent.name for p in APPLICATIONS.glob("*/resume.md"))
    hint = "Folders with a resume: " + ", ".join(available) if available else \
        "No company folder has a resume.md yet. Create one with:  apply: [company]"
    raise ExportError(f"No tailored resume at {source.relative_to(ROOT)}\n{hint}")


def show(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def export_resume(company=None, paper="letter", file=None):
    """Write the .md, .html and .pdf. Returns their paths and any PDF failure reason."""
    source = file or pick_source(company)
    if not source.exists():
        raise ExportError(f"Resume not found: {show(source)}")
    raw = source.read_text(encoding="utf-8")
    if "Empty on purpose" in raw:
        raise ExportError(f"{show(source)} is still the placeholder. Run `setup` first.")

    markdown = clean_markdown(raw)
    title = re.search(r"^#\s+(.+)$", markdown, flags=re.M)
    name = re.sub(r"[^A-Za-z0-9]+", "-", title.group(1)).strip("-") if title else ""
    stem = f"{name}-Resume" if name and name.lower() != "resume" else "Resume"

    folder = OUTPUT / (company or "general")
    folder.mkdir(parents=True, exist_ok=True)
    md_path, html_path, pdf_path = (folder / f"{stem}{ext}" for ext in (".md", ".html", ".pdf"))

    md_path.write_text(markdown, encoding="utf-8")
    page = (PAGE.replace("__PAPER__", "A4" if paper == "a4" else "Letter")
                .replace("__TITLE__", html.escape(title.group(1) if title else "Resume"))
                .replace("__BODY__", to_html(markdown)))
    html_path.write_text(page, encoding="utf-8")
    failure = make_pdf(html_path, pdf_path)
    return {"source": show(source), "md": show(md_path), "html": show(html_path),
            "pdf": "" if failure else show(pdf_path), "failure": failure}


def main():
    parser = argparse.ArgumentParser(description="Export a resume to Markdown, HTML and PDF.")
    parser.add_argument("company", nargs="?", help="folder name under applications/ (omit for the base resume)")
    parser.add_argument("--paper", choices=["letter", "a4"], default="letter", help="page size (default: letter)")
    parser.add_argument("--open", action="store_true", help="open the PDF (or the HTML if no PDF was made)")
    parser.add_argument("--file", type=Path, help="export this Markdown file instead")
    args = parser.parse_args()

    try:
        result = export_resume(args.company, args.paper, args.file)
    except ExportError as error:
        sys.exit(str(error))
    print(f"Source:   {result['source']}")
    print(f"Markdown: {result['md']}")
    print(f"HTML:     {result['html']}")
    if result["pdf"]:
        print(f"PDF:      {result['pdf']}")
    else:
        print(f"PDF:      not created: {result['failure']}.")
        print("          Open the HTML file in any browser and use Print > Save as PDF.")
    if args.open:
        webbrowser.open((ROOT / (result["pdf"] or result["html"])).as_uri())


if __name__ == "__main__":
    main()
