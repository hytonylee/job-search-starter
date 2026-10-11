#!/usr/bin/env python3
"""Open the local dashboard in your browser.

Usage:
  python3 scripts/app.py              start the dashboard and open it
  python3 scripts/app.py --port 9000  use a specific port
  python3 scripts/app.py --no-open    start it without opening a browser

It runs on this computer only (127.0.0.1) and sends nothing anywhere.
Stop it with Ctrl+C. If it is already running for this folder, it opens that
one instead of starting a second copy. Needs Python 3.8+ and nothing else.
"""

import argparse
import hashlib
import json
import mimetypes
import re
import secrets
import sys
import urllib.request
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import archive
import commands
import pipeline
import resume
import stories
from common import RESUME_PLACEHOLDER, ROOT, UNFILLED, parse_date, read_table, slug
from render import clean_markdown, render_md

EXAMPLE = ROOT / "example"  # a fictional candidate, shown read-only by the "See an example" button
PAGE_FILE = ROOT / "ui" / "index.html"
OUTPUT = ROOT / "output"
READABLE = ("applications", "profile", "progress", "notes", "modes")  # folders the page may read .md from
TOKEN = secrets.token_urlsafe(16)  # the page must send this back to change anything
INSTANCE = hashlib.sha1(str(ROOT).encode()).hexdigest()[:12]  # tells two repos' dashboards apart
DEFAULT_PORT = 8765
EXERCISES_HEADING = "## Exercises"  # in modes/practice.md; the `roles` keyword writes below it

ROLES_TEMPLATE = """# Target Roles

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


# ---------- reading: every function takes the data root, so the example reuses the same code ----------

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


def today_for(root):
    """Today, unless the root pins a date in today.txt (the example does, so its flags never go stale)."""
    return parse_date(read(root, "today.txt")) or date.today()


def pipeline_rows(root, relative="applications/PIPELINE.md"):
    """Enriched rows of a pipeline file, or raise pipeline.PipelineError."""
    return pipeline.enrich(pipeline.read_rows(root / relative), today_for(root))


def pipeline_state(root):
    try:
        rows = pipeline_rows(root)
    except pipeline.PipelineError as error:
        return {"rows": [], "counts": [], "problems": [str(error)]}
    keys = ("company", "role", "stage", "applied", "last contact", "next action", "due", "source", "flag", "closed")
    return {"rows": [{k: r.get(k, "") for k in keys} for r in rows],
            "counts": pipeline.stage_counts(rows),
            "problems": pipeline.problems(rows)}


def progress_stats(root):
    """Totals for the Progress tab, counted over current and archived applications."""
    rows = []
    for relative in ("applications/PIPELINE.md", "applications/_archive/PIPELINE-ARCHIVE.md"):
        try:
            rows += pipeline_rows(root, relative)
        except pipeline.PipelineError:
            pass
    # An interview was reached if the row is at an interview stage now, or interview notes exist.
    # The notes survive a later rejection and archiving, so the count never goes down.
    interviewed = {slug(r["company"]) for r in rows if r["stage"] in pipeline.INTERVIEW_STAGES}
    interviewed |= {slug(f.name) for f in company_folders(root) if (f / "interview-notes.md").exists()}
    return {"applied": sum(1 for r in rows if r["stage"] != "Drafted"),
            "interviews": len(interviewed),
            "offers": sum(1 for r in rows if r["stage"] == "Offer")}


def section(text, heading):
    """The body of one "## Heading" section of a Markdown document."""
    match = re.search(r"^## " + re.escape(heading) + r"[^\n]*\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return match.group(1) if match else ""


def setup_checklist(root):
    """The onboarding steps. The page refers to them by id, so the wording here can change freely."""
    profile = clean_markdown(read(root, "profile/profile.md"))
    rubric = read(root, "applications/SCREENING-RUBRIC.md")
    master = read(root, "profile/resume.md")
    has_resume = bool(master) and RESUME_PLACEHOLDER not in master
    header = profile.split("## Verified experience")[0]
    audited_claims = [line for line in section(profile, "Claims I must never inflate").splitlines()
                      if line.startswith("- ") and not line[2:].startswith("[")]
    exercises = clean_markdown(read(root, "modes/practice.md")).split(EXERCISES_HEADING)[-1]
    return [
        {"id": "roles", "done": bool(target_roles(root)),
         "text": "Enter the roles you are applying for",
         "hint": "Use the box above, or let onboarding ask you. Several roles are fine"},
        {"id": "source", "done": (root / "profile" / "linkedin-export.pdf").exists() or has_resume,
         "text": "Provide your LinkedIn export, or paste your resume",
         "hint": "On LinkedIn: your profile, Resources, Save to PDF. Put it in profile/ as linkedin-export.pdf"},
        {"id": "resume", "done": has_resume,
         "text": "Create your master resume from it", "hint": "Type setup in your AI tool"},
        {"id": "tailored", "done": "###" in exercises,
         "text": "Tailor the profile, practice and rubric to your roles",
         "hint": "setup does this. If you change your roles later, type roles in your AI tool"},
        {"id": "audit", "done": bool(profile) and UNFILLED not in header and bool(audited_claims),
         "text": "Fill in and audit your profile",
         "hint": "Type audit in your AI tool. This ticks once the audit has recorded the claims you must not inflate"},
        {"id": "rubric", "done": bool(rubric) and "[amount]" not in rubric and UNFILLED not in rubric,
         "text": "Set your hard stops in the screening rubric",
         "hint": "Edit applications/SCREENING-RUBRIC.md, or ask your AI tool to interview you for it"},
        {"id": "applied", "done": bool(pipeline_state(root)["rows"]),
         "text": "Apply to your first posting", "hint": "Type apply: [company] in your AI tool and paste the posting"},
    ]


def practice_log(root):
    """Rows of progress/practice-log.md as dicts, newest first."""
    header, rows = read_table(read(root, "progress/practice-log.md"))
    entries = [dict(zip(header, cells)) for cells in rows if cells[0]] if header else []
    return sorted(entries, key=lambda r: r.get("date", ""), reverse=True)


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
    is_example = root == EXAMPLE
    versions = resume.role_versions(root / "profile" / "resumes")
    apps = []
    for folder in company_folders(root):
        exported = [] if is_example else sorted((OUTPUT / "resume" / "companies" / folder.name).glob("*.pdf"))
        apps.append({"name": folder.name,
                     "files": sorted(p.name for p in folder.glob("*.md")),
                     "pdf": f"output/resume/companies/{folder.name}/{exported[-1].name}" if exported else ""})
    _, entries = archive.split_log(read(root, "progress/daily-log.md"))
    entries.sort(key=lambda e: e[0], reverse=True)
    questions = [{"company": f.name, "html": render_md(read(root, f"applications/{f.name}/interview-notes.md"))}
                 for f in company_folders(root) if (f / "interview-notes.md").exists()]
    return {
        "version": fingerprint(root),
        "example": is_example,
        "as_of": today_for(root).isoformat(),
        "has_example": EXAMPLE.is_dir(),
        "folder": "" if is_example else str(ROOT),
        "roles": target_roles(root),
        "versions": versions,
        "setup": setup_checklist(root),
        "pipeline": pipeline_state(root),
        "progress": progress_stats(root),
        "applications": apps,
        "prep": [{"title": title, "path": path} for title, path in PREP_DOCS if (root / path).exists()]
                + [{"title": f"Resume: {name}", "path": f"profile/resumes/{name}.md"} for name in versions],
        "questions": questions,
        "stories": stories_state(root),
        "practice": practice_log(root),
        "log": [{"date": d.isoformat(), "html": render_md(body)} for d, body in entries[:7]],
        "keywords": commands.keywords(),
        "scripts": [{"name": name, "summary": summary, "commands": usage}
                    for name, summary, usage in commands.script_commands()],
    }


# ---------- writing: always the user's own files, never the example ----------

def save_roles(roles):
    """Replace the role list in profile/roles.md, keeping any other text in the file.

    Returns the cleaned list, or raises ValueError.
    """
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

    target = ROOT / "profile" / "roles.md"
    lines = (target.read_text(encoding="utf-8") if target.exists() else ROLES_TEMPLATE).splitlines()
    listed = [i for i, line in enumerate(lines) if line.startswith("- ")]
    if listed:
        before, after = lines[:listed[0]], lines[listed[-1] + 1:]
        after = [line for line in lines[listed[0]:listed[-1]] if line.strip() and not line.startswith("- ")] + after
    else:
        before, after = lines, []
    while before and not before[-1].strip():
        before.pop()
    items = [f"- {role}" for role in cleaned] or ["- [add a role, e.g. Frontend Engineer]"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(before + [""] + items + after).rstrip() + "\n", encoding="utf-8")
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
        try:
            return 200, resume.export_resume(company, "a4" if body.get("paper") == "a4" else "letter",
                                             role=body.get("role") or None)
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

    def send_body(self, status, body, content_type):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, status, payload):
        self.send_body(status, json.dumps(payload), "application/json; charset=utf-8")

    def local_only(self):
        """Refuse requests that reach this server under any other host name."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        if host in ("127.0.0.1", "localhost"):
            return True
        self.send_json(403, {"error": "Forbidden"})
        return False

    def do_GET(self):
        if not self.local_only():
            return
        url = urlparse(self.path)
        query = parse_qs(url.query)
        root = EXAMPLE if query.get("example") == ["1"] and EXAMPLE.is_dir() else ROOT
        if url.path == "/":
            page = PAGE_FILE.read_text(encoding="utf-8").replace("__TOKEN__", TOKEN)
            self.send_body(200, page, "text/html; charset=utf-8")
        elif url.path == "/api/ping":
            self.send_json(200, {"instance": INSTANCE})
        elif url.path == "/api/state":
            self.send_json(200, state(root))
        elif url.path == "/api/version":
            self.send_json(200, {"version": fingerprint(root)})
        elif url.path == "/api/file":
            path = safe_md(root, query.get("path", [""])[0])
            if path:
                self.send_json(200, {"path": path.relative_to(root.resolve()).as_posix(),
                                     "html": render_md(path.read_text(encoding="utf-8"))})
            else:
                self.send_json(404, {"error": "File not found"})
        elif url.path.startswith("/output/"):
            path = (ROOT / unquote(url.path).lstrip("/")).resolve()
            if OUTPUT.resolve() in path.parents and path.is_file():
                kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                self.send_body(200, path.read_bytes(), kind + ("; charset=utf-8" if kind.startswith("text/") else ""))
            else:
                self.send_json(404, {"error": "File not found"})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if not self.local_only():
            return
        if self.headers.get("X-Token") != TOKEN:
            return self.send_json(403, {"error": "Reload the page and try again"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.send_json(400, {"error": "Bad request"})
        self.send_json(*do_action(urlparse(self.path).path, body if isinstance(body, dict) else {}))


def already_running(port):
    """True if a dashboard for this same folder is answering on the port."""
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/ping", timeout=1) as response:
            return json.loads(response.read()).get("instance") == INSTANCE
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description="Open the local dashboard.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port to use (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    # A second launch opens the dashboard that is already running rather than starting another.
    ports = [args.port] if args.port != DEFAULT_PORT else list(range(DEFAULT_PORT, DEFAULT_PORT + 10))
    for port in ports:
        if already_running(port):
            address = f"http://127.0.0.1:{port}/"
            print(f"The dashboard is already running at {address}")
            if not args.no_open:
                webbrowser.open(address)
            return

    server = None
    for port in ports:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"Could not start on port {args.port}. Try: python3 scripts/app.py --port 9000")

    port = server.server_address[1]
    address = f"http://127.0.0.1:{port}/"
    if port != args.port:
        print(f"Port {args.port} is in use by something else, so this is on {port} instead.")
    print(f"Dashboard running at {address}\nPress Ctrl+C to stop.")
    if not args.no_open:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
