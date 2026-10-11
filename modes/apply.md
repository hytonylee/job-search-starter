# Mode: apply: [company]

Reads: `applications/SCREENING-RUBRIC.md`, `profile.md`, `resume.md`. I paste the posting.

1. Save the posting to `applications/[company]/posting.md`.
2. Score it against the rubric. Tell me **apply or skip** before writing anything else. If skip, log the unmet required items in `progress/weak-spots.md` and stop.
3. Write `applications/[company]/fit.md`: each required item, whether I meet it, and the evidence from `profile.md`.
4. Draft `applications/[company]/resume.md`, tailored by reordering and rewording verified items only. Never add a skill that is not in `profile.md`.
5. Draft `cover-note.md` only if the posting asks for one. Under 150 words.
6. Add a row to `applications/PIPELINE.md` as **Drafted**. Change it to **Applied** only when I say I submitted.
7. Add each unmet required item to `progress/weak-spots.md`, or raise its count if it is already there.

Company folder layout is described in `applications/_example-company/README.md`.
