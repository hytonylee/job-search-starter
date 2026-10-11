#!/usr/bin/env python3
"""Export a resume from Markdown to clean Markdown, HTML and PDF.

Usage:
  python3 scripts/resume.py                 export the master resume, profile/resume.md
  python3 scripts/resume.py acme            export applications/acme/resume.md
  python3 scripts/resume.py --role frontend-engineer   export profile/resumes/frontend-engineer.md
  python3 scripts/resume.py acme --open     export, then open the result
  python3 scripts/resume.py --paper a4      A4 instead of US Letter
  python3 scripts/resume.py --file x.md     export any Markdown file

Files are written under output/resume/ to general/, roles/<role>/,
companies/<company>/ or custom/, and are named after the first "# Heading" in
the resume, e.g. Jane-Doe-Resume.pdf.

Needs Python 3.8+. The PDF step uses a Chromium-based browser that is already
installed (Chrome, Chromium, Edge or Brave). Without one, open the .html file
and use Print > Save as PDF.

Supported in an exported resume: headings, paragraphs, bullet and numbered
lists (nested), **bold**, *italic*, `code`, [links](https://example.com) and
--- rules. Tables and images are not laid out for print.
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

from common import RESUME_PLACEHOLDER, ROOT
from render import clean_markdown, to_html

MASTER = ROOT / "profile" / "resume.md"
APPLICATIONS = ROOT / "applications"
ROLE_RESUMES = ROOT / "profile" / "resumes"
RESUME_OUTPUT = ROOT / "output" / "resume"

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

PAGE_TEMPLATE = """<!doctype html>
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
  ul, ol { margin: 2pt 0 6pt; padding-left: 14pt; }
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


class ExportError(Exception):
    """A problem the user can fix, such as a missing or placeholder resume."""


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
    """Print the HTML to PDF with a headless browser. Returns None on success, or why it failed."""
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
        return None
    return f"{Path(browser).name} ran but produced no file"


def role_versions(folder=None):
    """Names of the per-role resume versions in profile/resumes/."""
    return sorted(p.stem for p in (folder or ROLE_RESUMES).glob("*.md") if p.name != "README.md")


def source_and_folder(company, role, file):
    """Which Markdown file to export, and the folder under output/resume/ it goes to."""
    if sum(bool(choice) for choice in (company, role, file)) > 1:
        raise ExportError("Choose one: a company, --role or --file.")
    if file:
        return file, "custom"
    if role:
        if role not in role_versions():
            available = ", ".join(role_versions()) or "none yet. Create one with:  role resume: [role]"
            raise ExportError(f"No resume version named '{role}'. Available: {available}")
        return ROLE_RESUMES / f"{role}.md", f"roles/{role}"
    if company:
        source = APPLICATIONS / company / "resume.md"
        if not source.exists():
            available = sorted(p.parent.name for p in APPLICATIONS.glob("*/resume.md"))
            hint = "Folders with a resume: " + ", ".join(available) if available else \
                "No company folder has a resume.md yet. Create one with:  apply: [company]"
            raise ExportError(f"No tailored resume at {display_path(source)}\n{hint}")
        return source, f"companies/{company}"
    return MASTER, "general"


def display_path(path):
    """The path relative to the repo, with forward slashes on every platform."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def file_stem(markdown):
    """The export file name, from the resume's first heading. Keeps accented and non-Latin letters."""
    title = re.search(r"^#\s+(.+)$", markdown, flags=re.M)
    name = re.sub(r"[^\w]+", "-", title.group(1)).strip("-_") if title else ""
    return f"{name}-Resume" if name and name.lower() != "resume" else "Resume"


def export_resume(company=None, paper="letter", file=None, role=None):
    """Write the .md, .html and .pdf. Returns their paths and, if no PDF was made, why."""
    source, subfolder = source_and_folder(company, role, file)
    if not source.exists():
        raise ExportError(f"Resume not found: {display_path(source)}")
    raw = source.read_text(encoding="utf-8", errors="replace")
    if RESUME_PLACEHOLDER in raw:
        raise ExportError(f"{display_path(source)} is still the empty template. Type `setup` in your AI tool first.")

    markdown = clean_markdown(raw)
    title = re.search(r"^#\s+(.+)$", markdown, flags=re.M)
    stem = file_stem(markdown)
    folder = RESUME_OUTPUT / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    md_path, html_path, pdf_path = (folder / f"{stem}{ext}" for ext in (".md", ".html", ".pdf"))

    md_path.write_text(markdown, encoding="utf-8")
    page = (PAGE_TEMPLATE.replace("__PAPER__", "A4" if paper == "a4" else "Letter")
            .replace("__TITLE__", html.escape(title.group(1) if title else "Resume"))
            .replace("__BODY__", to_html(markdown)))
    html_path.write_text(page, encoding="utf-8")
    failure = make_pdf(html_path, pdf_path)
    return {"source": display_path(source), "md": display_path(md_path), "html": display_path(html_path),
            "pdf": "" if failure else display_path(pdf_path), "failure": failure or ""}


def main():
    parser = argparse.ArgumentParser(description="Export a resume to Markdown, HTML and PDF.")
    parser.add_argument("company", nargs="?", help="folder name under applications/ (omit for the master resume)")
    parser.add_argument("--role", help="export the version in profile/resumes/ with this name")
    parser.add_argument("--paper", choices=["letter", "a4"], default="letter", help="page size (default: letter)")
    parser.add_argument("--open", action="store_true", help="open the PDF (or the HTML if no PDF was made)")
    parser.add_argument("--file", type=Path, help="export this Markdown file instead")
    args = parser.parse_args()

    try:
        result = export_resume(args.company, args.paper, args.file, args.role)
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
