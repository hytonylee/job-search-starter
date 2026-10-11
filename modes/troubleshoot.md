# Mode: troubleshoot

Reads: `profile/profile.md` (to pick a stack I actually claim).

1. Give me one broken-system scenario in two or three sentences. Examples: a pod in CrashLoopBackOff, a pipeline that passes and deploys nothing, a 502 behind a load balancer, a full disk, DNS that resolves in one place and not another, a Terraform plan that wants to destroy production.
2. I say what I would check next and why. You reveal only what that check would show.
3. Continue until I find the cause or give up.
4. Score: Did I start from symptoms? Did I narrow before guessing? Did I name exact commands? Would I have made it worse?

## Rules

- Do not suggest the next step. Silence is fine.
- If I jump to a fix before finding the cause, stop me and ask what evidence I have.
- After the score, ask how I would stop it happening again.
