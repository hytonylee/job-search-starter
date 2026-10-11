#!/usr/bin/env python3
"""List interview stories and show which common questions have no story yet.

Usage:
  python3 scripts/stories.py    list stories, coverage gaps and things to fix

Stories live in profile/stories/, one STAR story per file. Create them with the
`story` keyword in your AI tool. Needs Python 3.8+ and nothing else.
"""

import re

from common import ROOT

STORIES = ROOT / "profile" / "stories"

# The tags a story can carry, each with the kind of question it answers.
COMPETENCIES = [
    ("conflict", "Tell me about a disagreement with a colleague."),
    ("failure", "Tell me about a time you failed or made a mistake."),
    ("ownership", "Tell me about something you took on that was not your job."),
    ("ambiguity", "Tell me about a time the requirements were unclear."),
    ("influence", "Tell me about persuading someone you had no authority over."),
    ("leadership", "Tell me about a time you led a project or other people."),
    ("pressure", "Tell me about a tight deadline or a crisis."),
    ("feedback", "Tell me about hard feedback you received."),
    ("prioritisation", "Tell me about a trade-off, or a time you said no."),
    ("stakeholder", "Tell me about a difficult customer or stakeholder."),
    ("learning", "Tell me about something you had to learn quickly."),
    ("achievement", "What are you most proud of?"),
]
SECTIONS = ["situation", "task", "action", "result"]
META = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
WORDS_PER_MINUTE = 130
LONG_WORDS = 320  # about two and a half minutes spoken


def filled_value(text):
    """A metadata value, or "" if it is still a [placeholder]."""
    text = text.strip()
    return "" if text.startswith("[") else text


def parse_story(path):
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8"), flags=re.S)
    title = re.search(r"^#\s+(.+)$", text, flags=re.M)
    meta, sections, current = {}, {}, None
    for line in text.splitlines():
        heading = re.match(r"^##\s+(.+)$", line)
        field = META.match(line)
        if heading:
            current = heading.group(1).strip().lower()
            sections[current] = []
        elif current:
            sections[current].append(line)
        elif field:
            meta[field.group(1).strip().lower()] = filled_value(field.group(2))
    body = {name: "\n".join(lines).strip() for name, lines in sections.items()}
    body = {name: "" if content.startswith("[") else content for name, content in body.items()}

    tags = [t.strip().lower() for t in re.split(r"[,;]", meta.get("competencies", "")) if t.strip()]
    words = sum(len(body.get(name, "").split()) for name in SECTIONS)
    flags = []
    missing = [name.capitalize() for name in SECTIONS if not body.get(name)]
    if missing:
        flags.append("missing " + ", ".join(missing))
    if not tags:
        flags.append("no competencies tagged")
    if words > LONG_WORDS:
        flags.append(f"long: about {words / WORDS_PER_MINUTE:.1f} min spoken")
    if body.get("result") and not re.search(r"\d", body["result"]):
        flags.append("result has no number")
    action = body.get("action", "")
    if len(re.findall(r"\bwe\b", action, flags=re.I)) > len(re.findall(r"\bI\b", action)):
        flags.append('action says "we" more than "I"')
    if not meta.get("last practised"):
        flags.append("never practised aloud")
    return {
        "file": path.name,
        "title": title.group(1).strip() if title else path.stem,
        "competencies": tags,
        "roles": meta.get("roles", ""),
        "practised": meta.get("last practised", ""),
        "used": meta.get("used in", ""),
        "minutes": round(words / WORDS_PER_MINUTE, 1),
        "flags": flags,
    }


def load_stories(folder=None):
    folder = folder or STORIES
    if not folder.exists():
        return []
    return [parse_story(p) for p in sorted(folder.glob("*.md")) if p.name != "README.md"]


def coverage(stories):
    """For each competency: (tag, example question, [titles of stories that cover it])."""
    return [(tag, question, [s["title"] for s in stories if tag in s["competencies"]])
            for tag, question in COMPETENCIES]


def main():
    stories = load_stories()
    if not stories:
        print("No stories yet. Build one with:  story")
        print("\nQuestions to prepare for:")
        for tag, question in COMPETENCIES:
            print(f"  {tag.ljust(15)} {question}")
        return

    print(f"{len(stories)} stories\n")
    for story in stories:
        tags = ", ".join(story["competencies"]) or "untagged"
        print(f"  {story['title']}  ({story['minutes']} min)  [{tags}]")
        for flag in story["flags"]:
            print(f"      fix: {flag}")

    covered = coverage(stories)
    gaps = [(tag, question) for tag, question, titles in covered if not titles]
    print(f"\nCoverage: {len(covered) - len(gaps)} of {len(covered)} common questions have a story")
    for tag, question in gaps:
        print(f"  no story for {tag.ljust(15)} {question}")
    sole_cover = {}  # story title -> the questions it alone answers
    for tag, _, titles in covered:
        if len(titles) == 1:
            sole_cover.setdefault(titles[0], []).append(tag)
    for title, tags in sole_cover.items():
        if len(tags) >= 4:
            print(f"  '{title}' is the only story for {len(tags)} questions: {', '.join(tags)}")
    known = {tag for tag, _ in COMPETENCIES}
    other = sorted({t for s in stories for t in s["competencies"]} - known)
    if other:
        print(f"\nTags not in the standard list (still fine to use): {', '.join(other)}")


if __name__ == "__main__":
    main()
