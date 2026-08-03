# Glossary

Terms as this repository uses them. Where a term has a common industry meaning that differs, the difference is called out.

## The method

**Adversarial Sprint** — the workflow this repository specifies: independent planning, cross-family plan review, separately authored tests, chunked execution, and independent validation. "Adversarial" refers to structural independence between roles, not conflict for its own sake. PRD §16 records the name itself as an open decision.

**GROK → CHUNK → EXECUTE** — the three phases of the sprint method. GROK produces problem analysis, acceptance criteria, risks and test strategy; CHUNK breaks work into independently executable units with locked tests; EXECUTE runs the TDD cycle per chunk. Defined in `templates/SPRINT-PLANNING-TEMPLATE.md`.

**Chunk** — one bounded outcome with observable success criteria, allowed implementation files, locked test files, exact commands, a risk level, and a rollback method. Chunks are sequential by default.

**Model family** — declared model provenance (Anthropic/Claude, OpenAI/GPT, Google/Gemini, DeepSeek, and so on), not a marketing label or cost tier. Open-weight derivatives must declare their upstream base family. **Unknown provenance is treated as unknown and cannot satisfy a hard separation constraint.** Maintained by hand in a curated `model-families.json`, because nothing in the runtime can verify a claim of provenance.

**Family separation** — invariant #1. Planner ≠ plan reviewer family; test designer ≠ executor family; executor ≠ validator family.

**Single-blind review** — the reviewer sees the plan document and repository evidence, but not the planner's private reasoning and not a competing review. Deliberately *not* double-blind: the reviewer still reads the plan, so it inherits the plan's framing and vocabulary. The PRD calls this out specifically to avoid over-trust in the independence claim.

**Finding** — a structured review output with severity, category, claim, evidence, recommended change, and disposition. Schema in PRD §5.3 and [Data models](../reference/data-models.md).

**Disposition** — the recorded decision on a finding (accepted, rejected, superseded) plus rationale. Explicitly **not machine-verifiable** — the PRD treats this as an irreducibly human judgment and keeps the schema light so the ledger actually gets filled in.

## Test evidence

**Valid RED** — a test that collected, executed the intended path, reached its assertion, and failed *because the required behavior is absent or wrong*. Invariant #4.

**Invalid RED** — a failure from syntax errors, import errors, missing fixtures, unavailable services, empty test selection, timeouts, or unrelated assertion failures. These do not count as evidence, and the distinction is the point of the gate.

**Test lock** — pinning a test file by SHA-256 so the executor cannot modify the tests that judge it. Invariant #3, enforced by a hook. See [Probe 4](../probes/probe-4-hook-blocking.md).

**`SPEC_OR_TEST_BLOCKED`** — the contract string an executor receives when it attempts to modify a locked test. The executor reports it rather than "fixing" the test. Proven deliverable in Probe 4.

**`TEST_REFACTOR_REQUESTED`** — what an executor emits when a test legitimately needs changing after GREEN. Post-GREEN test changes are a separate reviewed transition, not an exception to the lock; there is deliberately no "cosmetic test change" fast path.

**Hidden tests** — a held-out acceptance set kept out of every agent's context, including the validator's. They do **not** buy insulation from human bias, since humans author both. They buy **Goodhart protection**: detecting an implementation that satisfies the letter of a visible test without the behavior generalising.

## Platform terms

**`droid exec`** — the Factory CLI's non-interactive mode. Every probe in this repository uses it. Prints a JSON result envelope with `-o json`.

**Result envelope** — the JSON `droid exec -o json` returns: `type`, `subtype`, `is_error`, `duration_ms`, `num_turns`, `session_id`, `result`, `usage`. Notably it does **not** contain the model that ran.

**Session transcript** — the per-session JSONL under `~/.factory/sessions/<cwd-slug>/<session-id>.jsonl`. Carries `message.modelId` and `message.reasoningEffort`, the startup context block, and every tool call and result. It is the only runtime source for the resolved model, and it is readable by any later agent with `Grep` — which is [Probe 3](../probes/probe-3-context-isolation.md)'s gap.

**Startup context** — the environment block injected into a session before the first turn. Contains `pwd`, an `ls`, `git status`, and a `Model:` line. Two probes turn on this: it is where the family gate reads the resolved model from turn 0, and it is why a run whose every tool was denied could still answer correctly.

**Autonomy tier** (`--auto low|medium|high`) — the permission level for a run. At `--auto low`, `Execute` is effectively **read-only**: every mutating command the model produced was labelled `medium` or higher and refused. See [Probe 8](../probes/probe-8-self-declared-risk.md).

**`riskLevel`** — a field in the `Execute` tool input containing **the model's own classification of the command it is about to run**, alongside `riskLevelReason`. The autonomy tier appears to gate on it, which makes it a self-report. Subject of Probe 8.

**`PreToolUse` hook** — a command Factory runs before a tool call, receiving a JSON payload on stdin (including `tool_name`, `tool_input`, `cwd`, and `transcript_path`). Exit 2 with a message on stderr denies the call and delivers the message to the agent. The basis of [the reference guard](../findings/reference-guard.md).

**Fail closed** — denying when the guard cannot interpret what it is looking at. Probe 4's A4 test showed the opposite: a guard that exited 0 on an unrecognised payload shape let a `sed -i` overwrite a locked file.

**Canary hook** — a `matcher: "*"` hook that logs every invocation and never blocks. Used to answer "did *any* hook fire at all", which is what distinguished "the matcher did not match" from "no hook loaded". Its absence caused a wrong verdict in this repository.

**Schema omission** — the mechanism by which a custom Droid's `tools:` allowlist is enforced. Disallowed tools are absent from the tool schema entirely, so there is nothing to refuse with. Note the allowlist is a **floor**, not an exact manifest: the platform adds `TodoWrite` and `Skill`.

**Custom Droid** — a Factory subagent defined in markdown with frontmatter (`name`, `description`, `model`, `tools`), callable via the `Task` tool. The plugin plans three: plan reviewer, test designer, independent validator.

## Repository conventions

**Probe** — a bounded feasibility experiment against the installed Factory version, recorded with commands, exit codes, raw output, and a reproduction script. Eight exist; see [Probes](../probes/index.md).

**Silent green** — this repository's name for the platform's default failure mode: a failed or degraded operation reporting success at exit 0. Four independent instances found. See [Silent green](../findings/silent-green.md).

**Reference guard** — the single `PreToolUse` hook primitive that enforces three invariants. See [The reference guard](../findings/reference-guard.md).

**Controlled comparison** — the repository's primary evidentiary method: an A/B pair differing in exactly one variable. Used for the hook registration matrix, the `tools:` allowlist, fail-open versus fail-closed, and the family gate.

**Superseded record** — an overturned probe result kept unedited under a banner pointing at its correction, rather than being rewritten. How the wrong call was caught is treated as part of the evidence.

**`STEER.md`** — a gitignored async steering channel where the operator appends instructions between probes. Deliberately untracked: it is live control input, not part of the record. Anything in it that should survive belongs in a commit or a probe README.

**Oversight** — the setting controlling human review frequency (`high`, `medium`, `low`) without weakening hard safety gates. PRD §16 flags the name itself as unsettled.
