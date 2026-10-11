# Mode: mock interview

Reads: `applications/[company]/posting.md`, `fit.md` and `research.md` (if it exists) for the company I name, `profile/profile.md`, the output of `python3 scripts/stories.py`.

Run a full round as that company's interviewer:

1. Two behavioural questions, phrased the way a real interviewer would. Pick one I have a story for and one I do not.
2. Three questions on the skills of the role, drawn from the posting's required items and weighted toward the ones `fit.md` marks unmet.
3. One practice exercise for the role this company is hiring (see `modes/practice.md`).
4. "Walk me through the hardest problem you handled in your last role."
5. "Why do you want to work here?" and "What questions do you have for us?" If there is no `research.md`, tell me afterwards to run `research: [company]`.

Stay in character until I say **stop**. Do not coach mid-round.

## After stop

- Score each answer 1 to 5 with one line on what was missing.
- Flag any answer over two minutes and any answer that did not address the question asked.
- Flag any claim that goes beyond `profile/profile.md`.
- For each behavioural answer, open the matching file in `profile/stories/` and say which of Situation, Task, Action and Result I skipped, and any fact that differed from the file. If I had no story for the question, say so and suggest `story`.
- Add repeated weak points to `progress/weak-spots.md`.

## Log it

Add a row to `progress/practice-log.md`: today's date as YYYY-MM-DD, `mock interview`, the topic, the average score out of 5 as a number, and the weakest point in a few words.
