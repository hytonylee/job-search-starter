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
import os
import re
import secrets
import sys
import urllib.request
import webbrowser
from datetime import date
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

# The role list sits between two marker lines, so saving it never touches anything else in the file.
ROLES_START, ROLES_END = "<!-- roles:start -->", "<!-- roles:end -->"
START_MARKER = re.compile(r"^\s*<!--\s*roles:start\s*-->\s*$")  # forgiving about spacing a hand edit may add
END_MARKER = re.compile(r"^\s*<!--\s*roles:end\s*-->\s*$")
LEGAL_SUFFIXES = {"inc", "incorporated", "ltd", "limited", "llc", "corp", "corporation", "co", "company", "gmbh", "plc"}
ROLES_TEMPLATE = f"""# Target Roles

The job titles I am applying for, one per line. The first is my primary target.
Edit this list on the dashboard's Start tab or right here, then type `roles` in the AI tool.
Keep the two marker lines. Anything outside them is yours and is never changed.

{ROLES_START}
{ROLES_END}
"""
NO_ROLE_YET = "- [add a role, e.g. Frontend Engineer]"


# ---------- reading: every function takes the data root, so the example reuses the same code ----------

def read(root, relative):
    """A file's text, or "" if it is missing. Bytes that are not valid UTF-8 are shown as \ufffd."""
    path = root / relative
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def safe_md(root, relative):
    """Resolve a path the page asked for, or None if it is not an allowed .md file under root."""
    try:
        path = (root / relative).resolve()
    except (OSError, ValueError):  # for example a null byte in the path
        return None
    allowed = any((root / top).resolve() in path.parents for top in READABLE)
    return path if allowed and path.suffix == ".md" and path.is_file() else None


def company_folders(root):
    return sorted(p for p in (root / "applications").glob("*") if p.is_dir() and not p.name.startswith("_"))


def is_note(line):
    """An indented, non-blank line: a note under the role above it."""
    return line[:1] in (" ", "\t") and bool(line.strip())


def roles_block(lines):
    """Where the role list is: (first, last, has_start, has_end) as line indexes, last exclusive.

    Normally the lines between the two markers. If the end marker was lost, the list runs to the
    last bullet after the start marker. With no markers at all, it is the first run of bullets.
    """
    start = next((i for i, line in enumerate(lines) if START_MARKER.match(line)), None)
    if start is not None:
        end = next((i for i in range(start + 1, len(lines)) if END_MARKER.match(lines[i])), None)
        if end is not None:
            return start + 1, end, True, True
        last = start + 1
        for i in range(start + 1, len(lines)):
            if lines[i].startswith("- ") or is_note(lines[i]):
                last = i + 1
            elif lines[i].strip():
                break
        return start + 1, last, True, False
    bullets = [i for i, line in enumerate(lines) if line.startswith("- ")]
    if not bullets:
        return len(lines), len(lines), False, False
    last = bullets[0]
    while last < len(lines) and (lines[last].startswith("- ") or is_note(lines[last])):
        last += 1
    return bullets[0], last, False, False


def target_roles(root):
    """The roles listed in profile/roles.md, ignoring the placeholder line."""
    lines = read(root, "profile/roles.md").splitlines()
    first, last, _, _ = roles_block(lines)
    roles = [line[2:].strip() for line in lines[first:last] if line.startswith("- ")]
    return [role for role in roles if role and not role.startswith("[")]


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
    """Totals for the Progress tab, one count per application, over current and archived rows.

    A row counts as an interview or an offer by the furthest stage it reached, which a closed
    row keeps in its Furthest column. A company folder with interview notes adds one more when
    no row for that company is already counted, in case the column was never filled in.
    """
    rows = []
    for relative in ("applications/PIPELINE.md", "applications/_archive/PIPELINE-ARCHIVE.md"):
        try:
            rows += pipeline_rows(root, relative)
        except pipeline.PipelineError:
            pass

    def same_company(name, folder):  # "Acme Inc." matches the folder "acme"; "Scale" does not match "scale-ai"
        longer, shorter = sorted((name, folder), key=len, reverse=True)
        return longer == shorter or (longer.startswith(shorter + "-")
                                     and set(longer[len(shorter) + 1:].split("-")) <= LEGAL_SUFFIXES)

    interviewed = [r for r in rows if r["furthest"] in pipeline.INTERVIEW_STAGES]
    from_notes = 0
    for folder in company_folders(root):
        if (folder / "interview-notes.md").exists() and \
                not any(same_company(slug(r["company"]), slug(folder.name)) for r in interviewed):
            from_notes += 1
    return {"applied": sum(1 for r in rows if r["stage"] in pipeline.STAGES and r["stage"] != "Drafted"),
            "interviews": len(interviewed) + from_notes,
            "offers": sum(1 for r in rows if r["furthest"] == "Offer")}


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


def prep_docs(root):
    """Documents for the Prep tab. `ready` is False while a file is still the empty template."""
    profile = clean_markdown(read(root, "profile/profile.md"))
    master = read(root, "profile/resume.md")
    rubric = read(root, "applications/SCREENING-RUBRIC.md")
    gaps = read_table(clean_markdown(read(root, "progress/weak-spots.md")))[1]
    exercises = clean_markdown(read(root, "modes/practice.md")).split(EXERCISES_HEADING)[-1]
    linkedin = clean_markdown(read(root, "profile/linkedin-profile.md"))
    docs = [
        ("Profile", "profile/profile.md", UNFILLED not in profile.split("## Verified experience")[0],
         "Your verified experience and the claims you must not inflate. Filled in by setup and audit."),
        ("Master resume", "profile/resume.md", bool(master) and RESUME_PLACEHOLDER not in master,
         "Your full resume, the source for every other version. Built by setup."),
        ("Gap list", "progress/weak-spots.md", any(any(cells) for cells in gaps),
         "Skills that real postings and interviews showed you are missing, ranked. Filled in as you apply."),
        ("Practice exercises", "modes/practice.md", "###" in exercises,
         "One live exercise per target role. Written by the roles keyword."),
        ("Screening rubric", "applications/SCREENING-RUBRIC.md", "[amount]" not in rubric and UNFILLED not in rubric,
         "Your rules for deciding in two minutes whether to apply. Filled in during setup."),
        ("LinkedIn text", "profile/linkedin-profile.md", bool(section(linkedin, "Headline").strip()),
         "The text currently on your LinkedIn profile. Filled in by setup, updated by linkedin sync."),
    ]
    found = [{"title": title, "path": path, "ready": bool(ready), "about": about,
              "section": "Exercises" if path == "modes/practice.md" else ""}
             for title, path, ready, about in docs if (root / path).exists()]
    return found + [{"title": f"Resume: {name}", "path": f"profile/resumes/{name}.md", "ready": True,
                     "about": "", "section": ""} for name in resume.role_versions(root / "profile" / "resumes")]


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
    entries = sorted(archive.log_entries(read(root, "progress/daily-log.md")), key=lambda e: e[0], reverse=True)
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
        "prep": prep_docs(root),
        "questions": questions,
        "stories": stories_state(root),
        "practice": practice_log(root),
        "log": [{"date": d.isoformat(), "html": render_md(body)} for d, body in entries[:7]],
        "keywords": commands.keywords(),
        "scripts": [{"name": name, "summary": summary, "commands": usage}
                    for name, summary, usage in commands.script_commands()],
    }


# ---------- writing: always the user's own files, never the example ----------

def save_roles(roles, target=None):
    """Replace the role list in profile/roles.md and leave the rest of the file exactly as it is.

    Indented notes under a role that is kept stay with it, as does any text above the first role
    inside the markers. Returns the cleaned list, or raises ValueError.
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

    target = target or ROOT / "profile" / "roles.md"
    raw = target.read_bytes() if target.exists() else ROLES_TEMPLATE.encode("utf-8")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    lines = raw.decode("utf-8", errors="replace").splitlines()
    first, last, has_start, has_end = roles_block(lines)

    def key(role):
        return re.sub(r"\s+", " ", role).strip().lower()

    lead, notes, current = [], {}, None  # text above the first role, and notes under each role
    for line in lines[first:last]:
        if line.startswith("- "):
            current = key(line[2:])
        elif current is None:
            lead.append(line)
        elif line.strip():
            notes.setdefault(current, []).append(line)
    block = lead
    for role in cleaned:
        block = block + [f"- {role}"] + notes.get(key(role), [])
    if not cleaned:
        block = block + [NO_ROLE_YET]
    if not has_start:  # a file written by hand: put the markers around its list
        block = [ROLES_START] + block + [ROLES_END]
    elif not has_end:  # the end marker was lost: put it back
        block = block + [ROLES_END]
    target.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(lines[:first] + block + lines[last:]).rstrip() + "\n"
    target.write_bytes(text.replace("\n", newline).encode("utf-8"))
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
            days = int(body.get("days", 30))
        except (TypeError, ValueError, OverflowError):
            return 400, {"error": "Days must be a whole number."}
        return 200, archive.run(days, bool(body.get("apply")))
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

    def guarded(self, handle):
        """Run a request handler; report any failure to the page instead of dropping the connection."""
        try:
            handle()
        except Exception as error:  # the page shows this message, so the user is not told to restart
            try:
                self.send_json(500, {"error": f"{type(error).__name__}: {error}"})
            except OSError:
                pass

    def do_GET(self):
        self.guarded(self.handle_get)

    def do_POST(self):
        self.guarded(self.handle_post)

    def handle_get(self):
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
                text = clean_markdown(path.read_text(encoding="utf-8", errors="replace"))
                wanted = query.get("section", [""])[0]
                found = re.search(r"^## " + re.escape(wanted) + r"[ \t]*$", text, flags=re.M) if wanted else None
                if found:  # show the document from that section onward
                    text = text[found.end():]
                self.send_json(200, {"path": path.relative_to(root.resolve()).as_posix(), "html": render_md(text)})
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

    def handle_post(self):
        if not self.local_only():
            return
        if self.headers.get("X-Token") != TOKEN:
            return self.send_json(403, {"error": "Reload the page and try again"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except ValueError:
            return self.send_json(400, {"error": "Bad request"})
        self.send_json(*do_action(urlparse(self.path).path, body if isinstance(body, dict) else {}))


class Server(ThreadingHTTPServer):
    # Windows lets a second program bind a port that is already listening when address reuse is on,
    # which would hide a dashboard that is already running. Elsewhere reuse only skips a restart delay.
    allow_reuse_address = os.name != "nt"


def already_running(port):
    """True if a dashboard for this same folder is answering on the port."""
    direct = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never through a proxy
    try:
        with direct.open(f"http://127.0.0.1:{port}/api/ping", timeout=2) as response:
            return json.loads(response.read()).get("instance") == INSTANCE
    except (OSError, ValueError):
        return False


def main():
    parser = argparse.ArgumentParser(description="Open the local dashboard.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port to use (default: {DEFAULT_PORT})")
    parser.add_argument("--no-open", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    ports = [args.port] if args.port != DEFAULT_PORT else list(range(DEFAULT_PORT, DEFAULT_PORT + 10))
    server = None
    for port in ports:
        try:
            server = Server(("127.0.0.1", port), Handler)
            break
        except OSError:
            # The port is taken. If it is this folder's dashboard, open that one and stop here.
            if already_running(port):
                address = f"http://127.0.0.1:{port}/"
                print(f"The dashboard is already running at {address}")
                if not args.no_open:
                    webbrowser.open(address)
                return
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
