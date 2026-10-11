# Mode: story

Purpose: Build one interview story, or practise one with `story: [title]`.

`story` builds a new interview story. `story: [title]` improves or practises an existing one. Reads: `profile/profile.md`, `profile/roles.md`, and the one story file being worked on.

## Build a story

1. Ask what happened, in my own words, and let me tell it roughly. If I have no idea which story to tell, run `python3 scripts/stories.py` and suggest a question that has no story yet, or an item from "Strongest evidence" in `profile/profile.md`.
2. Then ask for each part, one question at a time:
   - **Situation:** where, when, and what was at stake. Two or three sentences.
   - **Task:** what I personally was responsible for.
   - **Action:** what I did, step by step. This is the longest part.
   - **Result:** what changed, with a number and where the number comes from. Then what I would do differently.
3. Ask which follow-up questions an interviewer would push on, and what my honest answer is to each.
4. Write `profile/stories/[short-title-with-dashes].md` in the format below.
5. Run `python3 scripts/stories.py` and tell me what it flags for this story.

## Practise a story

1. Tell me to close the file and say the story from memory, by typing it as I would speak it.
2. Compare it with the file. Tell me which of the four parts I skipped or rushed, where I said "we" for my own work, any fact that differs from the file, and whether I gave the result.
3. Ask two of the likely follow-ups.
4. Set "Last practised" in the file to today, and add a row to `progress/practice-log.md`: the date, `story`, the title, a score out of 5, and the weakest point.

## Rules

- Notes, not a script. Write short factual lines I can speak from. Never write polished paragraphs for me to memorise.
- "I", not "we". If I say "we", ask which part was mine and write that.
- Every claim must be backed by `profile/profile.md`. If it is not there, ask for the evidence or leave it out.
- No source, no number. A result without a number is allowed only if I say plainly that it was not measured.
- Aim for two minutes spoken, about 260 words across the four parts. If it runs long, cut the Situation first.
- A story about failure or conflict must not make me the hero throughout. Keep the part where I was wrong.
- Use only these competency tags, so coverage can be counted: conflict, failure, ownership, ambiguity, influence, leadership, pressure, feedback, prioritisation, stakeholder, learning, achievement. One story usually covers two or three.

## File format

```markdown
# [Short title]

- **Competencies:** conflict, ownership
- **Roles:** all, or the target roles it suits
- **When and where:** [year, employer, my title]
- **Last practised:** [YYYY-MM-DD]
- **Used in:** [company and date, and how it landed]

## Situation

## Task

## Action

## Result

## Likely follow-ups

- [question]: [my honest answer in one line]
```
