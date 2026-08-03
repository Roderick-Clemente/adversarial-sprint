# Phase 0 — Feasibility Spike

**This is a build gate.** Nothing in Phase 1+ starts until these are answered with working probes rather than documentation reading or product assumptions.

Each probe below can kill or reshape the design. Answer honestly — a "no" here saves weeks.

> **Worth doing even if the project dies.** These probes double as a real evaluation of the platform's enterprise controls: can models be pinned per role, do agents get genuinely isolated context, can policy block an action deterministically, can spend be attributed at useful granularity. Those answers are worth having on their own, whether or not this plugin ever ships.

## Environment under test

Every answer below is scoped to this environment. A probe result recorded without it cannot be rechecked or contested later, and "Factory can't do X" is not a usable finding without a version attached.

| | |
|---|---|
| Factory CLI (`droid --version`) | **0.186.0** |
| Host | macOS (darwin 24.6.0), case-sensitive filesystem |
| Pilot repo | `~/Work/QuantumBank` |
| First probed | 2026-08-02 |

**Re-verify after any CLI upgrade.** A capability that appears or disappears between versions is itself a finding worth recording rather than a silent correction.

## Evidence

Committed probe evidence lives in [`evidence/`](./evidence/), one directory per probe. `.factory/` is gitignored as local tool state, so nothing written there survives — see [`evidence/README.md`](./evidence/README.md) for why and what a probe record needs.

Each **Result** below should end with a link to its evidence directory. A result without one is an opinion.

---

## Probe 1 — Per-role model pinning

**Question:** Can the installed Factory version pin distinct models to planner, reviewer, worker, and validator roles?

**Why it matters:** Family separation is invariant #1. Without per-role pinning there is no adversarial separation, and the whole thesis collapses to "one model, more steps."

**How to test:** Configure a Mission with distinct worker and validator model settings. Confirm via `droid exec --mission` flags and mission model settings that each role resolves to the model you specified.

**Result:** **BLOCKED — not reached.** `droid exec --mission` performs no work and reports success at 0.186.0: zero turns, zero tokens, zero credits, exit 0, with a real prompt in a real git repo at `--auto high`. A control run of plain `droid exec` on the same machine took a turn and consumed tokens, so the defect is scoped to mission mode: `input_tokens: 0` means it short-circuits before any model call. The `--worker-model` / `--validator-model` flags do exist on this version, so the surface is expressible — it just cannot be exercised, and a pinning assertion over zero turns would pass vacuously. Also blocks Probes 5 and 7. **Triggers the §8 Probe 5 contingency.** Raw capture and resolved model ID still outstanding — see [`evidence/probe-1/`](./evidence/probe-1/).

---

## Probe 2 — Fallback safety

**Question:** Can the plugin resolve *effective* model IDs at runtime and abort before a family-violating fallback occurs?

**Why it matters:** Invariant #7 — explicit degradation. A silent fallback that puts the validator on the executor's family turns the gate into theater without anyone noticing. Silent degradation is worse than no gate, because it still produces a green check.

**How to test:** Force a fallback (unavailable model, quota exhaustion, router override). Observe whether the resolved model ID is exposed to the caller *before* execution begins, and whether the run can be stopped on that signal.

**Result:** _(unanswered)_

---

## Probe 3 — Custom Droid context isolation

**Question:** Do custom Droids give genuinely fresh context and enforceable tool restrictions?

**Why it matters:** Invariant #2. If the validator can see the executor's transcript or reasoning, it is anchored and the independent review is worthless.

**How to test:** Define a read-only validator Droid. Run it after an executor Droid in the same Mission. Verify it cannot read the executor's transcript, and that write tools are genuinely unavailable rather than merely discouraged by prompt.

**Result:** _(unanswered)_

---

## Probe 4 — Deterministic hook blocking

**Question:** Can hooks reliably block edits to locked test files and persist command evidence?

**Why it matters:** Invariant #3 and #5. "The executor shouldn't edit tests" as a prompt instruction is a suggestion. As a hook it's a guarantee. The difference decides whether test locking is real.

**How to test:** Lock a test file by content hash. Instruct an executor Droid to modify it. Confirm the write is blocked, the executor receives `SPEC_OR_TEST_BLOCKED`, and the attempt is captured in run evidence.

**Result:** **PASS, with one condition.** A `PreToolUse` hook blocks the agent's own `Edit` to a SHA-256-locked test, the file is unchanged, the executor receives `SPEC_OR_TEST_BLOCKED` verbatim and quotes it back, and **the run continues** (5 turns, exit 0) rather than dying — so the block is actionable, not just fatal. Both the exit-2 and `permissionDecision: "deny"` channels work, and the attempt is captured twice over: in a hook-side log the orchestrator owns, and 3× in the session transcript. Invariant #3 and #5 are satisfiable.

The condition, and the most important implementation rule from Phase 0: **the guard must match `Execute` and must fail closed.** A path-matching hook sees `tool_input.command` for `Execute`, not `file_path`; with the matcher extended to `Execute` but the guard still keying on paths, it fired 5× and let a `sed -i` through — **lock bypassed** — because it exited 0 on a payload shape it did not understand. A guard that inspects command strings and denies on unparseable input held. Related negative: `--disabled-tools Edit` did **not** protect the file (the agent used a shell instead), so tool-level restriction is not path-level protection.

This **overturns the earlier BLOCKED verdict**, which was caused by a config-location trap rather than a runtime limit: hooks are read from the `hooks` key in **`.factory/settings.json`** and are **not read from `.factory/hooks.json`**, the location the docs list as the project-scope primary. Canary hooks at four locations: `hooks.json` 0, user-scope `hooks.json` 0, legacy `hooks/hooks.json` 0, `settings.json` **1**. A misregistered hook produces no warning and `exit 0` — the third silent-green failure in Phase 0 after the mission no-op and the Probe 3 storage leak. See [`evidence/probe-4/reverify/`](./evidence/probe-4/reverify/); the superseded record is kept alongside it.

---

## Probe 5 — Rejection routing

**Question:** Can Mission validation route a rejection to retry or re-plan, or must the command wrapper own that state machine?

**Why it matters:** Determines whether this is a Factory-native Mission or a command-level orchestrator that merely calls Factory. Materially changes the build, and changes the demo story.

**How to test:** Construct a Mission where the validator stage rejects. Observe whether the Mission can loop back to a prior stage, or whether it terminates and requires external re-invocation.

**Result:** _(unanswered)_ — likely blocked by the Probe 1 finding, since the scenario requires a Mission that executes. Pending confirmation of that finding. If it holds, §8's command-orchestrated contingency is triggered.

---

## Probe 6 — Plugin distribution boundary

**Question:** Which settings, hooks, and Mission artifacts are safely distributable inside a plugin?

**Why it matters:** Decides whether this ships as one installable thing or as a plugin plus a pile of manual repo-local setup. Directly affects whether it's demoable as a product.

**How to test:** Build a minimal plugin containing a Droid, a skill, and a hook. Install it clean and confirm which components activate without manual intervention.

**Result:** _(unanswered)_

---

## Probe 7 — Usage attribution

**Question:** Can credit/token usage be associated with a run at per-role granularity?

**Why it matters:** Hypothesis H3 (role-tiered models cut cost without cutting task success) is unmeasurable without it. The §13 evaluation needs real numbers, and "roughly 50% cheaper" is not a claim worth making in a demo without evidence.

**How to test:** Run one Mission with mixed models. Check whether usage data and OpenTelemetry traces can be correlated back to individual role invocations.

**Result:** _(unanswered)_ — likely blocked by the Probe 1 finding; a zero-credit run attributes nothing. Pending confirmation. Recall that a "no" here removes H3 from the §13 evaluation entirely.

---

## Exit Criteria

- [ ] Minimal plugin scaffold that installs cleanly
- [ ] Two cross-family read-only Droids
- [ ] One hook that provably blocks a locked-test edit
- [ ] One captured run artifact, committed under `evidence/`
- [ ] **Written go/no-go on Factory-native orchestration** — if Probe 5 says no, the design changes from Mission-native to command-orchestrated, and that decision belongs here rather than halfway through Phase 3

## Notes / Findings

_(running log — record surprises, doc gaps, and anything worth raising with Factory)_
