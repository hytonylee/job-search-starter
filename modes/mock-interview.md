# Mode: mock interview

Reads: `applications/[company]/posting.md` and `fit.md` for the company I name, `profile/profile.md`.

Run a full round as that company's interviewer:

1. Two behavioural questions.
2. Three technical questions drawn from the posting's required items, weighted toward the ones `fit.md` marks unmet.
3. One practice exercise for the role this company is hiring (see `modes/practice.md`).
4. "Walk me through the hardest problem you handled in your last role."

Stay in character until I say **stop**. Do not coach mid-round.

## After stop

- Score each answer 1 to 5 with one line on what was missing.
- Flag any answer over two minutes and any answer that did not address the question asked.
- Flag any claim that goes beyond `profile/profile.md`.
- Add repeated weak points to `progress/weak-spots.md`.

## Log it

Add a row to `progress/practice-log.md`: today's date as YYYY-MM-DD, `mock interview`, the topic, the average score out of 5 as a number, and the weakest point in a few words.
