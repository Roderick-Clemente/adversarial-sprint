# How to contribute

Contributing here is not writing features. There is no application to extend. Work in this repository takes one of three shapes:

- **Record probe evidence** — run a controlled experiment against the `droid` CLI and commit the record under `phase-0/evidence/`, meeting the standard in `phase-0/evidence/README.md`.
- **Extend the spec** — change `PRD.md` or `templates/SPRINT-PLANNING-TEMPLATE.md`, with the reasoning for the change written down.
- **Re-verify a verdict** — re-run a probe against a newer CLI version and record whether its recorded verdict still holds. Probe verdicts are pinned to `droid` 0.186.0; a different version invalidates them until re-run.

## Read this first: treat this repository as public

`AGENTS.md` is binding on every agent and human working here. Its first rule is that anything committed **will be read by outside parties**, including the vendors whose products the probes evaluate. There is no "it's private for now" state to rely on.

**Never write here:**

- Personal or confidential context of any kind — private conversations, negotiations, process notes about people
- Names of individuals at vendors or target companies, or anything traceable to a private conversation with them
- Competitive or negotiating strategy
- Secrets, credentials, tokens, internal customer names, or employer-confidential material

That material lives in a separate private repository, and the fence includes not referencing the private side by path.

Honest technical criticism is *not* on the never-write list. Recording that a platform capability is immature, undocumented, or broken is legitimate engineering work and belongs in the record. The line is "keep it technical, sourced, and fair", not "avoid criticism".

Because git history travels with the repository, scrub before the first push rather than adding a follow-up commit. See [Development workflow](./development-workflow.md#history-hygiene).

## Pages in this section

| Page | What it covers |
|---|---|
| [Patterns and conventions](./patterns-and-conventions.md) | Evidence standards, controlled comparison, forcing the bypass, how records are corrected |
| [Development workflow](./development-workflow.md) | Branch-per-author, commits as the handoff baton, review gate, history hygiene |
| [Testing](./testing.md) | The probes are the tests: how to re-run one, what a `run.sh` must do, what to assert on |
| [Debugging](./debugging.md) | The traps this repository actually hit, and how to get out of them |
| [Tooling](./tooling.md) | The `droid` CLI, `python3` hooks, bash, `git`, `jq`, and where Factory config lives |

New to the repository? Start at [Getting started](../overview/getting-started.md), then [Architecture](../overview/architecture.md). Unfamiliar terms are in the [Glossary](../overview/glossary.md).
