# Patterns and conventions

The conventions here are unusual because the repository's product *is* its evidentiary standard. A sloppy record is not a cosmetic problem — it is a defective artifact.

`AGENTS.md` is binding on every agent working in the repo, Factory Droid, Claude Code, Codex, or human. Read it before writing anything.

## Treat this repository as public

Assume anything committed here **will be read by outside parties**, including the vendors whose products it evaluates. There is no "it's private for now" state to rely on.

**Never write here:**

- Personal or confidential context of any kind
- Names of individuals at vendors or target companies, or anything traceable to a private conversation
- Competitive or negotiating strategy
- Secrets, credentials, tokens, internal customer names, or employer-confidential material

That material lives in a separate private repository, and the fence includes not referencing the private side by path.

**Do write here:** engineering rationale, trade-offs, what was tried and rejected, reproducible evidence, and **honest technical assessment including unflattering findings**. Recording that a platform capability is immature, undocumented, or broken is legitimate engineering work. The line is not "avoid criticism" — it is "keep it technical, sourced, and fair."

The distinction that matters: *"deterministic hook blocking is unreliable under condition X, here is the repro"* is good. Something sourced from a private conversation is not, even if true.

## History hygiene

A clean working tree is not enough, because git history travels with the repository. If anything sensitive is ever committed, **squash or rewrite before the first push** rather than adding a follow-up "scrub" commit that leaves the original in history.

In practice this means scrubbing local usernames and absolute home paths out of captured output *before* staging it. Probe records replace `/Users/<user>` with `~` in every raw capture.

## Evidence standards

From `phase-0/evidence/README.md`, every probe record carries:

- exact commands with exit codes
- raw stdout and stderr, secret-filtered
- the `droid --version` under test — a "no" recorded against no version cannot be rechecked later
- resolved model IDs wherever the probe touches model selection, not the requested IDs
- a `run.sh` that reproduces every measurement

> If a probe cannot be re-run from what is in its directory, it is a claim rather than evidence.

**Negative results get the same treatment as positive ones.** A probe that fails is the artifact, not a missing artifact.

### Controlled comparison is the default method

Every load-bearing claim in this repository comes from an A/B pair differing in **exactly one variable**:

| Claim | The pair |
|---|---|
| Hooks load from `settings.json`, not `hooks.json` | Same declaration, same canary, four config locations |
| The `tools:` allowlist is real | Same droid with and without the `tools:` key |
| A path guard fails open on shell writes | Same prompt, matcher with and without `Execute` |
| The family gate follows the resolved model | Same gate, `gpt-5.4-mini` versus `claude-opus-5` |

A single observation is a story; a pair with one variable is a finding.

### Force the bypass, or you are measuring manners

The sharpest recurring lesson. Twice, a control appeared to hold and did not:

- **Probe 4, test A3.** A locked file survived a run where the shell was unguarded — because the model *declined* to route around the guard on its own judgement. Test A4, differing only in the matcher, showed the file being overwritten by `sed -i`.
- **Probe 3, tests V3–V5.** A read-only validator refused three write instructions at `num_turns: 1` without attempting anything. That measured persuasion. Only after the persona was removed did the enforcement layer actually answer.

**Any test where the agent could have complied out of good manners measures the model's manners, not the control.** Design the run so refusal is not an option, or label the result behavioral.

### Never trust exit 0

The platform's default failure mode is reporting success for work that did not happen. See [Silent green](../findings/silent-green.md). Assert on the hook's own log, on per-tool `is_error`, and on observed effects such as file hashes — never on the process exit code or the agent's summary text.

### Record the limits

Every probe record ends with what was **not** measured, stated plainly rather than left implied. Examples that are load-bearing:

- Probe 2 induced no *real* fallback; `--model auto` and a cross-family ID are proxies.
- Probe 8 measures one model's calibration, not a platform property.
- Probe 6 never established whether hooks fire on a subagent's tool calls.

An unmeasured thing recorded as unmeasured is a finding. An unmeasured thing left ambiguous is a defect.

### Correct in place, do not rewrite

When a verdict is overturned, the original record is **kept unedited** under a banner pointing at the correction. Probe 4's superseded `README.md` is preserved alongside `reverify/README.md`, because how the wrong call was caught is part of the evidence. Probe 3's addendum lists four inline corrections to the main record rather than editing the claims away.

## Multi-agent handoff

Three agents work in this repository — Factory Droid, Codex, and Claude Code — sharing one working tree. **Commits are the baton.**

- **Branch by author:** `<agent>/<topic>` — `factory/`, `codex/`, `claude/`. Authorship stays obvious in history, a bad run is one `git branch -D`, and nobody reconstructs who wrote what from commit messages.
- Hand off via `git diff`. The reviewing agent reads the diff, not the other agent's reasoning.
- Push branches to the private remote as you go. The local machine is not a backup.
- Land on `main` only after review, and **keep convention and spec changes off feature branches** so they do not ride along with unreviewed work.

This mirrors the method the repository itself specifies — independent context, no transcript bleed. If it feels clumsy in practice, that is real signal about the design and belongs in `phase-0/README.md` under Notes.

**Role separation applies to the agents too.** The agent that authored a plan should not approve it, and the agent that wrote an implementation should not validate it. That is invariant #1 applied to the humans-and-agents layer, not just the runtime.

## Writing style in records

Probe records are technical documents that will be read adversarially, so:

- Lead with the verdict, then the evidence that supports it
- Quote raw output rather than paraphrasing it
- Distinguish observation from inference explicitly — Probe 8 states that causation is *inferred, not proven*, and flags it as a question for the vendor rather than an assertion
- Prefer a table over prose for anything with more than two dimensions
- Link claims to the specific raw capture that supports them

## Commit messages

Commits in this repository are unusually long, because they carry the reasoning that a diff cannot. A typical probe commit states the verdict, the controlled comparison that produced it, the caveat, and the scope limit. They also carry `Co-authored-by:` trailers for agent-authored work — 26 of 33 commits have one.
