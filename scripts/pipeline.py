#!/usr/bin/env python3
"""Show the job pipeline from applications/PIPELINE.md.

Usage:
  python3 scripts/pipeline.py           print the pipeline in the terminal
  python3 scripts/pipeline.py --html    also write output/pipeline.html
  python3 scripts/pipeline.py --open    write the HTML and open it in a browser

Needs Python 3.8+ and nothing else. Dates in the table must be YYYY-MM-DD.
"""

import argparse
import html
import re
import sys
import webbrowser
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "applications" / "PIPELINE.md"
OUTPUT = ROOT / "output" / "pipeline.html"

STAGES = ["Drafted", "Applied", "Screen", "Technical", "Final", "Offer",
          "Rejected", "Withdrawn", "No reply"]
CLOSED = {"Rejected", "Withdrawn", "No reply"}
STALE_DAYS = 21  # an Applied row with no contact for this long is flagged


def parse_date(text):
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def split_cells(line):
    """Split a table row on | but not on an escaped \\| inside a cell."""
    return [c.strip().replace("\\|", "|")
            for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def read_rows(path):
    """Return the rows of the first table whose header starts with Company."""
    if not path.exists():
        sys.exit(f"Pipeline file not found: {path}")
    header, rows = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header:
                break
            continue
        cells = split_cells(line)
        if header is None:
            if cells[0].lower() == "company":
                header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):  # separator or blank row
            continue
        row = dict(zip(header, cells))
        row["issues"] = []
        if len(cells) != len(header):
            row["issues"].append(f"has {len(cells)} columns, expected {len(header)}")
        if row.get("company"):
            rows.append(row)
    if header is None:
        sys.exit(f"No pipeline table found in {path}")
    return rows


def enrich(rows, today):
    """Normalise the stage and work out which rows need attention."""
    known = {s.lower(): s for s in STAGES}
    for row in rows:
        row["stage"] = known.get(row.get("stage", "").lower(), row.get("stage", ""))
        if row["stage"] not in STAGES:
            row["issues"].append(f"unknown stage '{row['stage']}'")
        for field in ("applied", "last contact", "due"):
            if row.get(field) and not parse_date(row[field]):
                row["issues"].append(f"{field} '{row[field]}' is not YYYY-MM-DD")
        row["closed"] = row["stage"] in CLOSED
        due = parse_date(row.get("due", ""))
        last = parse_date(row.get("last contact", "")) or parse_date(row.get("applied", ""))
        row["flag"] = ""
        if not row["closed"]:
            if due and due < today:
                row["flag"] = f"overdue {(today - due).days}d"
            elif row["stage"] == "Applied" and last and (today - last).days >= STALE_DAYS:
                row["flag"] = f"no reply {(today - last).days}d"
        row["_sort"] = (
            STAGES.index(row["stage"]) if row["stage"] in STAGES else len(STAGES),
            due or date.max,
            row["company"].lower(),
        )
    return sorted(rows, key=lambda r: r["_sort"])


def stage_counts(rows):
    counts = {}
    for row in rows:
        counts[row["stage"] or "(no stage)"] = counts.get(row["stage"] or "(no stage)", 0) + 1
    ordered = [s for s in STAGES if s in counts] + [s for s in counts if s not in STAGES]
    return [(s, counts[s]) for s in ordered]


def problems(rows):
    return [f"{r['company']}: {issue}" for r in rows for issue in r["issues"]]


def clip(text, width):
    return text if len(text) <= width else text[: width - 1] + "…"


def print_terminal(rows):
    if not rows:
        print("No applications yet. Add one with:  apply: [company]")
        return
    active = [r for r in rows if not r["closed"]]
    flagged = [r for r in rows if r["flag"]]
    need = "needs" if len(flagged) == 1 else "need"
    print(f"{len(rows)} applications, {len(active)} active, {len(flagged)} {need} attention")
    print("  " + "  ".join(f"{stage}: {n}" for stage, n in stage_counts(rows)))
    print()

    columns = [("company", "Company", 24), ("role", "Role", 28), ("stage", "Stage", 10),
               ("applied", "Applied", 10), ("due", "Due", 10),
               ("next action", "Next action", 34), ("flag", "Attention", 14)]
    widths = [min(limit, max(len(title), *(len(r.get(key, "")) for r in rows)))
              for key, title, limit in columns]
    print("  ".join(title.ljust(w) for (_, title, _), w in zip(columns, widths)))
    print("  ".join("-" * w for w in widths))
    for row in rows:
        print("  ".join(clip(row.get(key, ""), w).ljust(w)
                        for (key, _, _), w in zip(columns, widths)).rstrip())
    if problems(rows):
        print("\nFix these rows in applications/PIPELINE.md (they may be miscounted):")
        for line in problems(rows):
            print(f"  - {line}")


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Job Pipeline</title>
<style>
  :root {{ --bg:#f7f7f5; --card:#fff; --text:#1c1c1a; --muted:#6b6b66; --line:#e3e3de;
          --warn:#b45309; --warn-bg:#fef3c7; --ok:#166534; --ok-bg:#dcfce7; --off:#6b6b66; --off-bg:#ecece8; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#161615; --card:#1f1f1d; --text:#ecece8; --muted:#a3a39c; --line:#33332f;
            --warn:#fcd34d; --warn-bg:#453208; --ok:#86efac; --ok-bg:#0f3d22; --off:#a3a39c; --off-bg:#2a2a27; }}
  }}
  body {{ margin:0; padding:24px 16px 48px; background:var(--bg); color:var(--text);
         font:15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }}
  main {{ max-width:1100px; margin:0 auto; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  h2 {{ font-size:15px; margin:28px 0 10px; }}
  .sub {{ color:var(--muted); margin:0 0 20px; }}
  .cards {{ display:flex; flex-wrap:wrap; gap:10px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:10px 16px; min-width:92px; }}
  .card b {{ display:block; font-size:24px; line-height:1.2; }}
  .card span {{ color:var(--muted); font-size:13px; }}
  .wrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--line); border-radius:10px; }}
  table {{ border-collapse:collapse; width:100%; min-width:760px; }}
  th, td {{ text-align:left; padding:9px 12px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }}
  tr:last-child td {{ border-bottom:0; }}
  tr.closed td {{ color:var(--muted); }}
  .pill {{ display:inline-block; padding:1px 9px; border-radius:99px; font-size:13px; white-space:nowrap;
          color:var(--ok); background:var(--ok-bg); }}
  .pill.closed {{ color:var(--off); background:var(--off-bg); }}
  .pill.warn {{ color:var(--warn); background:var(--warn-bg); }}
  .nowrap {{ white-space:nowrap; }}
  .empty {{ padding:28px; color:var(--muted); text-align:center; }}
</style>
</head>
<body>
<main>
<h1>Job Pipeline</h1>
<p class="sub">{summary} · generated {today} from applications/PIPELINE.md</p>
<div class="cards">{cards}</div>
{attention}
{problems}
<h2>All applications</h2>
<div class="wrap">{table}</div>
</main>
</body>
</html>
"""


def html_table(rows, with_flag=True):
    if not rows:
        return '<div class="empty">No applications yet. Add one with <code>apply: [company]</code>.</div>'
    esc = html.escape
    head = "<tr><th>Company</th><th>Role</th><th>Stage</th><th>Applied</th><th>Last contact</th>" \
           "<th>Next action</th><th>Due</th>" + ("<th>Attention</th>" if with_flag else "") + "</tr>"
    body = []
    for r in rows:
        pill = '<span class="pill warn">' + esc(r["flag"]) + "</span>" if r["flag"] else ""
        flag = "<td>" + pill + "</td>"
        body.append(
            f'<tr class="{"closed" if r["closed"] else ""}">'
            f'<td><b>{esc(r.get("company", ""))}</b></td><td>{esc(r.get("role", ""))}</td>'
            f'<td><span class="pill{" closed" if r["closed"] else ""}">{esc(r["stage"])}</span></td>'
            f'<td class="nowrap">{esc(r.get("applied", ""))}</td>'
            f'<td class="nowrap">{esc(r.get("last contact", ""))}</td>'
            f'<td>{esc(r.get("next action", ""))}</td>'
            f'<td class="nowrap">{esc(r.get("due", ""))}</td>{flag if with_flag else ""}</tr>'
        )
    return f"<table><thead>{head}</thead><tbody>{''.join(body)}</tbody></table>"


def write_html(rows, today):
    active = [r for r in rows if not r["closed"]]
    flagged = [r for r in rows if r["flag"]]
    cards = "".join(f'<div class="card"><b>{n}</b><span>{html.escape(stage)}</span></div>'
                    for stage, n in stage_counts(rows))
    attention = ""
    if flagged:
        attention = f'<h2>Needs attention ({len(flagged)})</h2><div class="wrap">{html_table(flagged)}</div>'
    fix = ""
    if problems(rows):
        items = "".join(f"<li>{html.escape(line)}</li>" for line in problems(rows))
        fix = f"<h2>Rows to fix in applications/PIPELINE.md</h2><ul>{items}</ul>"
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(PAGE.format(
        summary=f"{len(rows)} applications, {len(active)} active",
        today=today.isoformat(), cards=cards, attention=attention, problems=fix, table=html_table(rows),
    ), encoding="utf-8")
    return OUTPUT


def main():
    parser = argparse.ArgumentParser(description="Show the job pipeline.")
    parser.add_argument("--html", action="store_true", help="write output/pipeline.html")
    parser.add_argument("--open", action="store_true", help="write the HTML and open it")
    parser.add_argument("--file", type=Path, default=PIPELINE, help="pipeline file to read")
    args = parser.parse_args()

    today = date.today()
    rows = enrich(read_rows(args.file), today)
    print_terminal(rows)
    if args.html or args.open:
        path = write_html(rows, today)
        print(f"\nWrote {path.relative_to(ROOT)}")
        if args.open:
            webbrowser.open(path.as_uri())


if __name__ == "__main__":
    main()
