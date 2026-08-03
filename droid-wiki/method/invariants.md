# Invariants

PRD §4 draws a line between two kinds of claim. **Hypotheses must be measured**: they might turn out false, and the evaluation design in §13 exists to find out. **Invariants must be enforced**: if one cannot be guaranteed, the run stops rather than continuing in a weakened form.

There are eight, numbered as in PRD §4. The numbering is load-bearing: the Phase 0 scorecard, the reference guard's policy table, and the probe records all cite invariants by number.

> Hard invariants apply at every `oversight` level (PRD §6). Turning oversight down reduces how often a human is consulted; it does not relax any of the eight.

## The scorecard at a glance

From `phase-0/GO-NO-GO.md`, scoped to `droid` **0.186.0** on macOS. Nothing is red.

| # | Invariant | Phase 0 status | Tested by |
|---|---|---|---|
| 1 | Family separation | 🟢 green, via contingency | [Probe 1](../probes/probe-1-model-pinning.md), [Probe 2](../probes/probe-2-fallback-safety.md) |
| 2 | Fresh review context | 🟡 amber — enforceable, not default | [Probe 3](../probes/probe-3-context-isolation.md) |
| 3 | Independent test authorship | 🟢 green, conditional | [Probe 4](../probes/probe-4-hook-blocking.md) |
| 4 | Valid RED before GREEN | ⚪ unprobed, low risk | — |
| 5 | Immutable evidence | 🟢 green | [Probe 4](../probes/probe-4-hook-blocking.md) |
| 6 | Blocking validation | 🟡 amber — the wrapper owns it | Probe 5, unreached |
| 7 | Explicit degradation | 🟡 amber — only if we build it | [Probe 2](../probes/probe-2-fallback-safety.md) |
| 8 | Human merge | 🟢 green | — (git-level) |

Three green, three amber that turn green once the guard exists, one unprobed and low risk, one green with no platform dependency at all. The amber entries share a cause: the platform will not enforce these for us, so the enforcement is code this project has to write. The full argument is in [Findings](../findings/index.md).

A CLI upgrade invalidates every status in this table until the probes are re-run.

---

## 1. Family separation

> Planner ≠ plan reviewer family; test designer ≠ executor family; executor ≠ validator family.

**What it means.** Three pairwise constraints, not a blanket "all roles differ". The planner and the executor may share a family; the planner and its reviewer may not. Family is *declared provenance* (Anthropic/Claude, OpenAI/GPT, Google/Gemini, DeepSeek), not a marketing label and not a cost tier. See [Roles and models](./roles-and-models.md).

**Why it exists.** PRD §2 lists two failure modes this addresses: confidently wrong plans, where the author also grades the plan, and correlated blind spots, where repeated passes reuse the same priors and framing. A second pass from the same family is one opinion twice.

**How it is enforced.** Explicit `--model` pins, one `droid exec` invocation per role. Every run records resolved model ID, provider, family, role, and whether a fallback occurred. A resolution that violates a role constraint stops the run. At runtime the family gate policy of the reference guard reads the resolved model from the session transcript's startup context and denies before any tool acts.

**Phase 0 status: 🟢 green, via contingency.** The intended surface is gone. Mission-level `--worker-model` and `--validator-model` are unusable because they are only valid with `--mission`, and `droid exec --mission` performs no work while reporting success ([Probe 1](../probes/probe-1-model-pinning.md)). The replacement holds: explicit `--model` pins resolve exactly and an invalid model ID fails closed at exit 1 ([Probe 2](../probes/probe-2-fallback-safety.md)). One hard rule came out of it: **never use `--model auto`**, because it resolved to a concrete model the caller cannot predict, which is unusable for role-pinned work.

**Not yet closed.** No real fallback was induced. Probe 2 used `--model auto` and an explicit cross-family ID as proxies; quota exhaustion and server-side substitution are untested, and custom or BYOK endpoints are the most plausible real silent fallback and were not measured at all.

---

## 2. Fresh review context

> The validator receives the approved spec, resulting diff, read-only repository state, and test evidence. It never receives the executor's transcript, reasoning, or self-assessment.

**What it means.** An allowlist and a denylist in one sentence. The validator gets enough repository reality to catch integration failures, not only the diff, but none of the executor's narration about what it did or why.

**Why it exists.** PRD §2 calls the failure it prevents *self-review theater*: a reviewer that inherits the author's reasoning and framing agrees with it. The exclusion is deliberately narrow. PRD §14 phrases the trade-off as "exclude transcript, not codebase reality": a validator starved of repository access cannot find integration problems, so restricting it too far breaks the invariant it was meant to serve.

**How it is enforced.** A custom Droid definition gives the validator a fresh context and read-only tools, plus an isolation guard policy that denies commands touching the session store.

**Phase 0 status: 🟡 amber, enforceable but not default.** A custom Droid does get a fresh context, and its `tools:` allowlist is genuinely enforced by schema omission. But the executor's session is readable off disk from `~/.factory/sessions/` with `Grep` alone, and independently via `droid search` ([Probe 3](../probes/probe-3-context-isolation.md) and its addendum). Isolation holds only if a guard blocks those paths. The same `PreToolUse` primitive that enforces invariant 3 does it, so the cost is small, but a Droid definition alone does not satisfy this invariant.

---

## 3. Independent test authorship

> The executor may not create or modify locked acceptance tests. A required test change returns to the test-design stage.

**What it means.** The executor's write scope excludes every hash-locked test file. When the spec or the test is wrong, the executor reports `SPEC_OR_TEST_BLOCKED` and stops; it does not repair the test. Post-GREEN test changes are a separate reviewed transition, described under invariant 5.

**Why it exists.** PRD §2: when the same agent writes the tests and the code, the tests encode the implementation bug. The gate is only worth something if the thing being graded cannot edit the grader.

**How it is enforced.** A `PreToolUse` hook denies writes to hash-pinned test files, matching on `Edit`, `Create`, `ApplyPatch` **and** `Execute`. Denial exits 2 with the contract string on stderr, which is delivered to the agent so the run can act on it.

**Phase 0 status: 🟢 green, conditional.** [Probe 4](../probes/probe-4-hook-blocking.md) blocked the agent's own `Edit` to a hash-locked test, delivered `SPEC_OR_TEST_BLOCKED` verbatim, and the run continued and acted on it. This verdict **overturned an earlier BLOCKED** result that had been caused by a registration mistake rather than a platform limit.

The conditions are absolute, and each was earned from a counterexample:

1. **Register via `.factory/settings.json` or inside a plugin.** A standalone project `.factory/hooks.json` is silently never read, despite being documented as the primary location. That trap produced a wrong verdict in this repository.
2. **Fail closed.** A guard keying on `file_path` was handed `Execute`'s `command`, understood nothing, exited 0, and the locked file was overwritten.
3. **Match `Execute`.** Path matching alone is one `sed -i` away from bypass.
4. **Prove the hook fired.** Install a canary and assert it logged. Configuration being present is not evidence of enforcement.

**Not yet closed.** Whether hooks fire on a *subagent's* tool calls is unresolved ([Probe 6](../probes/probe-6-plugin-boundary.md)). If they do not, a subagent is a hole in this invariant. `phase-0/GO-NO-GO.md` flags it as cheap to close and worth closing early.

---

## 4. Valid RED before GREEN

> Behavior-changing work cannot begin until the intended assertion has run and failed for the expected reason.

This is the subtlest of the eight, and the distinction it rests on is what makes it useful rather than ceremonial.

### Valid versus invalid RED

A **valid RED** means all four of the following happened: the test **collected**, it **executed the intended code path**, it **reached its assertion**, and it **failed because the required behavior is absent or wrong**.

An **invalid RED** is any other failure. PRD §5.4 enumerates them:

| Invalid RED class | What actually failed |
|---|---|
| Syntax error | The file never parsed |
| Import error | The module never loaded |
| Missing fixture | Setup failed before the test body ran |
| Unavailable service | The environment, not the code |
| Empty test selection | Nothing ran at all; the selector matched no test |
| Timeout | Unknown — the assertion may never have been reached |
| Unrelated assertion failure | A different behavior, in the wrong place |

Every one of these produces a non-zero exit code, which is why "the test failed, so we have RED" is not a gate. It is a gate against nothing. A misspelled test path and a genuinely missing feature are indistinguishable at the exit code, and the first one lets an executor proceed to implement while believing it has evidence. Worse, the corresponding GREEN is equally hollow: fix the import and the "RED" becomes "GREEN" without a line of behavior changing.

So the required record is not a boolean. PRD §5.4 pins the shape:

```json
{
  "behavior": "observable outcome under test",
  "test_id": "path::test_name",
  "test_sha256": "hash of locked test content",
  "command": "exact test command",
  "expected_failure": "assertion and mismatch expected before implementation",
  "exit_code": 1,
  "observed_failure": "captured assertion output",
  "classification": "behavioral-red"
}
```

`expected_failure` is written *before* the run and `observed_failure` is captured *from* it. The gate compares them. That is what distinguishes "it failed" from "it failed for the reason we predicted", and it is the whole content of the invariant.

### Documented exceptions

Refactors, docs-only changes, test-only cleanups, and fixes where a failing test already exists may receive a documented exception. The exception is approved by the validator **before** execution, not claimed afterwards by the executor. The same carve-out exists in the hand-run template, which requires the reason to be written into the chunk notes.

**Phase 0 status: ⚪ unprobed, low risk.** No platform capability is in question. This is pure orchestration: run the test, capture the exit code and output, assert the failure matches the prediction. `phase-0/GO-NO-GO.md` still attaches the project's standing rule to it: *never trust `exit 0`*, and by extension never trust a non-zero one either without reading what produced it.

---

## 5. Immutable evidence

> The RED test content hash must match the GREEN test content hash. Any mutation invalidates the gate and requires review.

**What it means.** The SHA-256 of the locked test content is recorded at RED and re-checked at GREEN. If it changed, the RED evidence no longer describes the test that passed, and the gate is void.

**Why it exists.** Invariant 3 stops the executor from editing tests. Invariant 5 catches the case where a test changed anyway, whatever the route. It converts test tampering from something to detect by inspection into a hash comparison.

**The post-GREEN gap, and why it is not an exception.** The hash lock covers RED → GREEN and nothing after. But REFACTOR is the third beat of the cycle, so a legitimate test cleanup after a passing implementation is the first thing a real chunk hits. PRD §5.6 handles it as a **separate reviewed transition**:

1. The executor never makes the change. It reports `TEST_REFACTOR_REQUESTED` with a rationale.
2. The test designer authors the change.
3. The validator approves it and re-runs the **original locked assertion set** against the current implementation. If a previously-locked behavioral assertion no longer holds, this is a scope change and routes back to GROK.
4. The run records both hashes and the approving role.

There is deliberately **no "cosmetic test change" fast path**. Cosmetic is a judgment call, and removing the executor's judgment from test content is the entire point of the lock.

**Phase 0 status: 🟢 green.** Evidence persists in two independent places ([Probe 4](../probes/probe-4-hook-blocking.md), Test D): a hook-side log whose path the orchestrator chooses, and three times over in the session transcript. Two independent stores matter here, because a single store the run itself controls is not evidence of the run's own behavior. PRD §9 also notes that RED/GREEN records are the one artifact class that is fully **machine-verifiable**, so a human should never need to adjudicate one.

---

## 6. Blocking validation

> A rejected chunk cannot be marked complete.

**What it means.** Validation is a gate, not advice. The validator's verdict is one of `ACCEPT`, `REJECT_IMPLEMENTATION`, `REJECT_TEST`, `REPLAN`, or `HUMAN_DECISION`, and each non-accept verdict has a defined destination: a fresh executor attempt capped at two, a return to test design that invalidates downstream locks, a return to GROK/CHUNK, or a human decision packet.

**Why it exists.** PRD §2 names the failure as *rubber-stamp validation*: review that is advisory or has no blocking contract changes nothing about the outcome.

**How it is enforced.** The command wrapper's state machine. Chunk completion is a transition the wrapper refuses to take without an `ACCEPT`.

**Phase 0 status: 🟡 amber, the wrapper owns it.** Mission rejection routing was Probe 5's question and was never reachable, because Probe 5 was blocked by Probe 1's mission defect. In the command-orchestrated design this stops being a platform feature and becomes project code. `phase-0/GO-NO-GO.md` accepts the cost as real but bounded, and puts the rejection state machine last in the Phase 1 build order, after the guard it depends on. PRD §16 still lists the underlying question as open: whether mission validation could express all retry and re-plan transitions is unanswered rather than settled negative.

---

## 7. Explicit degradation

> If family identity, context isolation, test locking, or artifact capture cannot be guaranteed, the run stops rather than silently weakening the method.

**What it means.** A guarantee that cannot be verified is treated as absent. Four things are named, and they map onto invariants 1, 2, 3, and 5. This is also where `unknown` model provenance lands: unknown cannot satisfy a hard separation constraint, so it stops the run rather than being optimistically admitted.

**Why it exists.** A method whose entire value is a trustworthy gate is worse than useless if the gate can quietly stop working while still reporting success. Silent weakening is the failure mode that destroys the audit trail's meaning retroactively.

**How it is enforced.** Preflight checks before execution, per-stage checks during it, and the family gate at runtime. The guard fails closed on any payload it cannot interpret.

**Phase 0 status: 🟡 amber, only if we build it.** This is the invariant the platform actively works against. `-r xhigh` on a model that does not support that reasoning effort **silently resolves to `off`** at exit 0 ([Probe 2](../probes/probe-2-fallback-safety.md)): maximum to minimum, no warning. That is one of four silent-green instances Phase 0 recorded, alongside a mission that does no work, a hook that never loads, and a run whose every tool call was denied still exiting 0 with a plausible answer sourced from startup context.

It is recoverable: the family gate detects a wrong-model run before any tool acts. But the detection is entirely ours to write, and that is why `phase-0/GO-NO-GO.md` puts the guard first in the build order and closes with the instruction to treat every green check as unproven until something this project wrote has asserted it. See [Silent green](../findings/silent-green.md).

---

## 8. Human merge

> The system may create a branch, local commits, and a PR; a human approves the merge.

**What it means.** No auto-merge, and no deployment. PRD §3 puts CD, auto-merge, and autonomous production changes out of scope for v1 entirely. PRD §5.8 adds that the final report must distinguish evidence from inference and include unresolved risks, so the human approving the merge is reading a document that does not overstate its own confidence.

**Why it exists.** It is the outer boundary on autonomy. Everything else in the method is about making the run's claims checkable; this is the point at which someone checks them.

**How it is enforced.** Git-level. The run has no merge step to disable.

**Phase 0 status: 🟢 green.** No platform dependency, so nothing to probe.

---

## How the eight are enforced in practice

Phase 0's central architectural finding is that one primitive covers three of them. A ~30-line `PreToolUse` hook that reads `transcript_path`, inspects what actually happened, and fails closed carries three policies:

| Guard policy | Denies when | Invariants |
|---|---|---|
| Locked-test guard | The target path, or a shell command mentioning it, is a hash-pinned test | 3 |
| Isolation guard | The command touches `~/.factory/sessions` or invokes `droid search` | 2 |
| Family gate | `message.modelId` is outside the expected family | 1, 7 |

It ships inside a plugin and activates on install ([Probe 6](../probes/probe-6-plugin-boundary.md)). Details in [The reference guard](../findings/reference-guard.md).

The remaining five are elsewhere: invariants 4 and 6 are orchestration in the command wrapper, invariant 5 is a hash comparison plus two independent evidence stores, and invariant 8 is git.

One boundary is worth stating plainly, because it is easy to reach for the wrong control. The autonomy tier is **not** a substitute for any of these. It gates partly on the model's own `riskLevel` label for the command it is about to run ([Probe 8](../probes/probe-8-self-declared-risk.md)), which makes it a self-report. Use tiers for blast radius and hooks for enforcement.

## Related

- [Workflow](./workflow.md) — where each invariant's gate sits in the stage machine
- [Roles and models](./roles-and-models.md) — how family separation is declared and checked
- [Probes](../probes/index.md) — the full evidence set
- [The reference guard](../findings/reference-guard.md), [Silent green](../findings/silent-green.md)
