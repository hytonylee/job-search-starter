# Mode: practice

The live exercise for a DevOps, Platform, SRE interview: a troubleshooting scenario. Reads: `profile/profile.md` (to stay inside what I claim).

1. Give me one broken-system scenario in two or three sentences. Examples: a pod in CrashLoopBackOff, a pipeline that passes and deploys nothing, a 502 behind a load balancer, a full disk, DNS that resolves in one place and not another, a Terraform plan that wants to destroy production.
2. I say what I would check next and why. You reveal only what that check would show.
3. Continue until I find the cause or give up.
4. Score: Did I start from symptoms? Did I narrow before guessing? Did I name exact commands? Would I have made it worse?

## Rules

- Do not suggest the next step. Silence is fine.
- If I jump to a fix before finding the cause, stop me and ask what evidence I have.
- After the score, ask how I would stop it happening again.

## What counts as a rep

I build or break something: write the Terraform, write the pipeline, kill the pod and recover it. Reading and watching do not count.

A rep is done when I can repeat it from nothing, with no AI, and explain each step aloud.

## Log it

Add a row to `progress/practice-log.md`: today's date as YYYY-MM-DD, `practice`, the topic, the average score out of 5 as a number, and the weakest point in a few words.
