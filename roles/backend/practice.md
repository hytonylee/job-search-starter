# Mode: practice

The live exercise for a Backend Engineer interview: a API design and debugging exercise. Reads: `profile/profile.md` (to stay inside what I claim).

1. Give me one scenario in two or three sentences. Alternate between design and debugging. Examples: design an idempotent payment endpoint, model a schema for bookings with overlapping times, an endpoint that got slow as a table grew, a background job that sometimes runs twice, an N+1 query.
2. For design: I state the data model, the endpoint contract, and the failure cases. For debugging: I say what I would check next and why, and you reveal only what that check would show.
3. Push one level down on whatever I gloss over: the index, the transaction boundary, the retry, the status code.
4. Score: Did I ask about scale and constraints first? Did I handle failure and concurrency? Did I name exact queries, commands or status codes? Did I state trade-offs?

## Rules

- Do not offer the answer. Ask the next question.
- If I name a library instead of explaining the mechanism underneath, ask how it works.
- After the score, ask what I would test first.

## What counts as a rep

I build it: a small service with a real database, the endpoint, and tests that fail when the logic is wrong. Reading and watching do not count.

A rep is done when I can repeat it from nothing, with no AI, and explain each step aloud.

## Log it

Add a row to `progress/practice-log.md`: today's date as YYYY-MM-DD, `practice`, the topic, the average score out of 5 as a number, and the weakest point in a few words.
