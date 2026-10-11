# Mode: audit

Reads: `profile/resume.md`, `profile/profile.md`.

Go through `profile/resume.md` one line at a time. One line per turn, do not batch. For each line ask:

- What did I personally do, as opposed to my team?
- At what scale (nodes, services, deploys per day, users, spend)?
- What is the source for any number: a dashboard, a ticket, a postmortem, a bill?
- Could I explain it for five minutes to an engineer who ran the same tool?

Then keep it, rewrite it to what I can defend, or cut it.

## Rules

- If I say "we," ask which part was mine.
- No source, no number.
- A tool I touched once goes under "Exposure only" in `profile/profile.md`, not in a skills list.
- Check omissions too. If the strongest thing I did is missing or buried, say so and move it up.

## Output

- Updated `profile/resume.md`.
- `profile/profile.md` filled in: the verified table, exposure list, claims never to inflate, strongest evidence.
- A short list of what was cut and why.
