#!/usr/bin/env python3
"""Open the local dashboard in your browser.

Usage:
  python3 scripts/app.py              start the dashboard and open it
  python3 scripts/app.py --port 9000  use a specific port
  python3 scripts/app.py --no-open    start it without opening a browser

It runs on this computer only (127.0.0.1) and sends nothing anywhere.
Stop it with Ctrl+C. Needs Python 3.8+ and nothing else.
"""

import argparse
import hashlib
import json
import mimetypes
import re
import secrets
import sys
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

import archive
import help as help_script
import pipeline
import resume
import stories

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "example"  # a fictional candidate, shown read-only by the "See an example" button
PAGE = ROOT / "ui" / "index.html"
OUTPUT = ROOT / "output"
READABLE = ("applications", "profile", "progress", "notes", "modes")  # folders the page may read .md from
TOKEN = secrets.token_urlsafe(16)  # the page must send this back to change anything

ROLES_HEADER = """# Target Roles

The job titles I am applying for, one per line. The first is my primary target.
Edit this list on the dashboard's Start tab or right here, then type `roles` in the AI tool.

"""

PREP_DOCS = [
    ("Profile", "profile/profile.md"),
    ("Master resume", "profile/resume.md"),
    ("Gaps", "progress/weak-spots.md"),
    ("Practice exercise", "modes/practice.md"),
    ("Screening rubric", "applications/SCREENING-RUBRIC.md"),
    ("LinkedIn text", "profile/linkedin-profile.md"),
]


# ---------- reading: every function takes the data root, so the example can reuse it ----------

def render_md(text):
    """Markdown to HTML: the resume subset plus tables."""
    blocks, table, prose = [], [], []

    def flush_prose():
        if prose:
            blocks.append(resume.to_html("\n".join(prose)))
            prose.clear()

    def flush_table():
        rows = [pipeline.split_cells(line) for line in table]
        rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]  # drop separators and blanks
        if rows:
            head = "".join(f"<th>{resume.inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{resume.inline(c)}</td>" for c in r) + "</tr>"
                           for r in rows[1:])
            blocks.append(f'<div class="wrap"><table><thead><tr>{head}</tr></thead>'
                          f"<tbody>{body}</tbody></table></div>")
        table.clear()

    for line in resume.clean_markdown(text).splitlines():
        if line.strip().startswith("|"):
            flush_prose()
            table.append(line)
        else:
            if table:
                flush_table()
            prose.append(line)
    flush_prose()
    if table:
        flush_table()
    return "\n".join(blocks)


def read(root, relative):
    path = root / relative
    return path.read_text(encoding="utf-8") if path.exists() else ""


def safe_md(root, relative):
    """Resolve a path the page asked for, or None if it is not an allowed .md file under root."""
    path = (root / relative).resolve()
    allowed = any((root / top).resolve() in path.parents for top in READABLE)
    return path if allowed and path.suffix == ".md" and path.is_file() else None


def company_folders(root):
    return sorted(p for p in (root / "applications").glob("*") if p.is_dir() and not p.name.startswith("_"))


def target_roles(root):
    """The roles listed in profile/roles.md, ignoring the placeholder line."""
    lines = [line[2:].strip() for line in read(root, "profile/roles.md").splitlines() if line.startswith("- ")]
    return [line for line in lines if line and not line.startswith("[")]


def roles_tailored(root):
    """True once the `roles` keyword has written at least one practice exercise."""
    exercises = resume.clean_markdown(read(root, "modes/practice.md")).split("## Exercises")[-1]
    return "###" in exercises


def today_for(root):
    """Today, or the fixed date in example/today.txt so the example's flags never go stale."""
    fixed = pipeline.parse_date(read(root, "today.txt")) if root == EXAMPLE else None
    return fixed or date.today()


def pipeline_state(root):
    try:
        rows = pipeline.enrich(pipeline.read_rows(root / "applications" / "PIPELINE.md"), today_for(root))
    except SystemExit as error:
        return {"rows": [], "counts": [], "problems": [str(error)]}
    keys = ("company", "role", "stage", "applied", "last contact", "next action", "due", "source", "flag", "closed")
    return {"rows": [{k: r.get(k, "") for k in keys} for r in rows],
            "counts": pipeline.stage_counts(rows),
            "problems": pipeline.problems(rows)}


def setup_checklist(root):
    profile, rubric = read(root, "profile/profile.md"), read(root, "applications/SCREENING-RUBRIC.md")
    header = profile.split("## Verified experience")[0]
    master = read(root, "profile/resume.md")
    return [
        {"done": bool(target_roles(root)), "text": "Enter the roles you are applying for",
         "hint": "Use the box above. Several roles are fine"},
        {"done": (root / "profile" / "linkedin-export.pdf").exists() or root == EXAMPLE,
         "text": "Save your LinkedIn profile as a PDF",
         "hint": "On LinkedIn: your profile, Resources, Save to PDF. Put it in profile/ as linkedin-export.pdf"},
        {"done": bool(master) and "Empty on purpose" not in master,
         "text": "Create your resume from it", "hint": "Type setup in your AI tool"},
        {"done": roles_tailored(root), "text": "Tailor the profile, practice and rubric to your roles",
         "hint": "setup does this. If you change your roles later, type roles in your AI tool"},
        {"done": bool(profile) and "[fill in]" not in header,
         "text": "Fill in and audit your profile", "hint": "Type audit in your AI tool"},
        {"done": bool(rubric) and "[amount]" not in rubric and "[fill in]" not in rubric,
         "text": "Set your hard stops in the screening rubric",
         "hint": "Edit applications/SCREENING-RUBRIC.md, or ask your AI tool to interview you for it"},
        {"done": bool(pipeline_state(root)["rows"]),
         "text": "Apply to your first posting", "hint": "Type apply: [company] in your AI tool and paste the posting"},
    ]


def practice_log(root):
    """Rows of progress/practice-log.md as dicts, newest first."""
    rows, header = [], None
    for line in read(root, "progress/practice-log.md").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = pipeline.split_cells(line)
        if header is None:
            header = [c.lower() for c in cells]
        elif not all(set(c) <= set("-: ") for c in cells) and cells[0]:
            rows.append(dict(zip(header, cells)))
    return sorted(rows, key=lambda r: r.get("date", ""), reverse=True)


def stories_state(root):
    items = stories.load_stories(root / "profile" / "stories")
    for item in items:
        item["html"] = render_md(read(root, f"profile/stories/{item['file']}"))
    return {"items": items,
            "coverage": [{"tag": tag, "question": question, "titles": titles}
                         for tag, question, titles in stories.coverage(items)]}


def fingerprint(root):
    """Changes whenever a file the dashboard shows is added, removed or edited."""
    files = [ROOT / "AGENTS.md", root / "profile" / "linkedin-export.pdf"]
    for top in READABLE:
        files += (root / top).rglob("*.md")
    files += (OUTPUT / "resume").rglob("*.pdf")
    digest = hashlib.sha1()
    for path in sorted(files):
        try:
            info = path.stat()
        except OSError:
            continue
        digest.update(f"{path.relative_to(ROOT).as_posix()}|{info.st_mtime_ns}|{info.st_size}\n".encode())
    return digest.hexdigest()[:16]


def state(root=ROOT):
    example = root == EXAMPLE
    versions = resume.role_versions(root / "profile" / "resumes")
    apps = []
    for folder in company_folders(root):
        exported = [] if example else sorted((OUTPUT / "resume" / folder.name).glob("*.pdf"))
        apps.append({"name": folder.name,
                     "files": sorted(p.name for p in folder.glob("*.md")),
                     "pdf": f"output/resume/{folder.name}/{exported[-1].name}" if exported else ""})
    _, entries = archive.split_log(read(root, "progress/daily-log.md"))
    entries.sort(key=lambda e: e[0], reverse=True)
    questions = [{"company": f.name, "html": render_md(read(root, f"applications/{f.name}/interview-notes.md"))}
                 for f in company_folders(root) if (f / "interview-notes.md").exists()]
    return {
        "version": fingerprint(root),
        "example": example,
        "as_of": today_for(root).isoformat(),
        "has_example": EXAMPLE.is_dir(),
        "roles": target_roles(root),
        "versions": versions,
        "setup": setup_checklist(root),
        "pipeline": pipeline_state(root),
        "applications": apps,
        "prep": [{"title": title, "path": path} for title, path in PREP_DOCS if (root / path).exists()]
                + [{"title": f"Resume: {name}", "path": f"profile/resumes/{name}.md"} for name in versions],
        "questions": questions,
        "stories": stories_state(root),
        "practice": practice_log(root),
        "log": [{"date": d.isoformat(), "html": render_md(body)} for d, body in entries[:7]],
        "keywords": help_script.keywords(),
        "scripts": [{"name": p.name, "summary": help_script.script_usage(p)[0],
                     "commands": help_script.script_usage(p)[1]}
                    for p in sorted((ROOT / "scripts").glob("*.py"))],
    }


# ---------- writing: always the user's own files, never the example ----------

def save_roles(roles):
    """Write the role list. Returns the cleaned list, or raises ValueError."""
    if not isinstance(roles, list):
        raise ValueError("roles must be a list")
    cleaned = []
    for item in roles:
        text = re.sub(r"[\r\n|`<>\[\]]", " ", str(item))
        text = re.sub(r"\s+", " ", text).strip(" -")[:60]
        if text and text.lower() not in [c.lower() for c in cleaned]:
            cleaned.append(text)
    if len(cleaned) > 8:
        raise ValueError("Keep it to 8 roles or fewer. A focused search works better.")
    body = "".join(f"- {role}\n" for role in cleaned) or "- [add a role, e.g. Frontend Engineer]\n"
    target = ROOT / "profile" / "roles.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(ROLES_HEADER + body, encoding="utf-8")
    return cleaned


def do_action(path, body):
    """Handle a POST. Returns (status, payload)."""
    if path == "/api/roles":
        try:
            return 200, {"roles": save_roles(body.get("roles"))}
        except ValueError as error:
            return 400, {"error": str(error)}
    if path == "/api/export":
        company = body.get("company") or None
        if company and company not in [f.name for f in company_folders(ROOT)]:
            return 400, {"error": "Unknown company folder"}
        version = body.get("role") or None
        try:
            return 200, resume.export_resume(company, "a4" if body.get("paper") == "a4" else "letter", role=version)
        except resume.ExportError as error:
            return 400, {"error": str(error)}
    if path == "/api/archive":
        try:
            days = max(1, int(body.get("days", 30)))
        except (TypeError, ValueError):
            return 400, {"error": "days must be a number"}
        cutoff, apply = date.today() - timedelta(days=days), bool(body.get("apply"))
        return 200, {"applied": apply,
                     "report": archive.archive_log(cutoff, apply) + archive.archive_pipeline(cutoff, apply)}
    return 404, {"error": "Not found"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the terminal quiet
        pass

    def send(self, status, body, content_type="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def json(self, status, payload):
        self.send(status, json.dumps(payload))

    def local_only(self):
        """Refuse requests that reach this server under any other host name."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        if host in ("127.0.0.1", "localhost"):
            return True
        self.json(403, {"error": "Forbidden"})
        return False

    def do_GET(self):
        if not self.local_only():
            return
        url = urlparse(self.path)
        query = parse_qs(url.query)
        root = EXAMPLE if query.get("example") == ["1"] and EXAMPLE.is_dir() else ROOT
        if url.path == "/":
            self.send(200, PAGE.read_text(encoding="utf-8").replace("__TOKEN__", TOKEN), "text/html; charset=utf-8")
        elif url.path == "/api/state":
            self.json(200, state(root))
        elif url.path == "/api/version":
            self.json(200, {"version": fingerprint(root)})
        elif url.path == "/api/file":
            path = safe_md(root, query.get("path", [""])[0])
            if path:
                self.json(200, {"path": path.relative_to(root.resolve()).as_posix(),
                                "html": render_md(path.read_text(encoding="utf-8"))})
            else:
                self.json(404, {"error": "File not found"})
        elif url.path.startswith("/output/"):
            path = (ROOT / unquote(url.path).lstrip("/")).resolve()
            if OUTPUT.resolve() in path.parents and path.is_file():
                kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                self.send(200, path.read_bytes(), kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
            else:
                self.json(404, {"error": "File not found"})
        else:
            self.json(404, {"error": "Not found"})

    def do_POST(self):
        if not self.local_only():
            return
        if self.headers.get("X-Token") != TOKEN:
            return self.json(403, {"error": "Reload the page and try again"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.json(400, {"error": "Bad request"})
        self.json(*do_action(urlparse(self.path).path, body if isinstance(body, dict) else {}))


def main():
    parser = argparse.ArgumentParser(description="Open the local dashboard.")
    parser.add_argument("--port", type=int, default=8765, help="port to use (default: 8765)")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    server = None
    for port in [args.port] + ([] if args.port != 8765 else list(range(8766, 8776))):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"Could not start on port {args.port}. Try: python3 scripts/app.py --port 9000")

    address = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Dashboard running at {address}\nPress Ctrl+C to stop.")
    if not args.no_open:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
