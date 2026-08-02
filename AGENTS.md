# Agent Conventions

Applies to every agent working in this repo — Factory Droid, Claude Code, Codex, or otherwise.

## Treat this repo as public

Assume anything committed here **will be read by outside parties**, including the vendors whose products it evaluates, and may become fully public. Write accordingly. There is no "it's private for now" state to rely on.

### Never write here

- Personal or confidential context of any kind — private conversations, negotiations, process notes about people
- Names of individuals at vendors or target companies, or anything traceable to a private conversation with them
- Competitive or negotiating strategy
- Secrets, credentials, tokens, internal customer names, or employer-confidential material

That material lives in a separate private repo. Keep the fence clean; do not reference the private side by path, either.

### Do write here

- Engineering rationale, design trade-offs, and what was tried and rejected
- **Honest technical assessment, including unflattering findings.** Recording that a platform capability is immature, undocumented, or broken is legitimate engineering work and belongs in the record. The line is not "avoid criticism" — it is "keep it technical, sourced, and fair."
- Reproducible evidence: commands, exit codes, observed output

The distinction that matters: *"deterministic hook blocking is unreliable under condition X, here's the repro"* is good. *"Their PM told me the roadmap is a mess"* is not — even though both are true, only one is engineering.

## History hygiene

The working tree being clean is not enough — git history travels with the repo. If anything sensitive is ever committed, squash or rewrite **before** the first push rather than adding a follow-up "scrub" commit that leaves the original in history.

## Multi-agent handoff

Agents share this working tree, so avoid simultaneous edits. Commits are the baton:

- Droid works on `factory/<topic>` branches so authorship stays obvious in history and a bad run is one `git branch -D`
- Hand off via `git diff`; the reviewing agent reads the diff, not the other agent's reasoning
- This mirrors the method the repo itself specifies — independent context, no transcript bleed. If it feels clumsy in practice, that is real signal about the design. Record it in `phase-0/README.md` under Notes.
