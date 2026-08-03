# Probe 1 — Per-role model pinning

**Status:** BLOCKED. Probe 1 is not answered, and could not be reached.
**Date:** 2026-08-02
**CLI under test:** `droid` 0.186.0
**Recorded by:** Factory Droid, from an operator-reported reproduction. See [Reproduction gaps](#reproduction-gaps) — raw output is not yet captured in this directory.

## Finding

`droid exec --mission` appears to be a no-op at 0.186.0. Invoked without worker or validator flags, it returns success having done nothing.

```
droid exec --mission --auto high --model claude-opus-5
```

| Signal | Observed |
|---|---|
| `numTurns` | 0 |
| `input_tokens` | 0 |
| `credits` | 0 |
| exit code | 0 |

No worker or validator model flags were involved. This is the plainest possible mission invocation, which is what makes it a blocker rather than a configuration error on our side.

## Why this does not answer Probe 1

Probe 1 asks whether distinct models can be pinned to planner, reviewer, worker, and validator roles. The intended test routes through a Mission with distinct worker and validator model settings. If the mission surface does not execute, there is nothing to pin models *to*, and a pinning test run through it would return a meaningless pass: zero turns consume zero models, so any assertion about which model ran is vacuously satisfiable.

Recording this as "Probe 1: no" would be wrong. The accurate statement is that the execution substrate Probe 1 depends on did not run, so the capability question is still open.

## Blast radius

Three probes route through a working Mission, and all three are blocked by the same root cause:

| Probe | Dependency on Missions | Effect |
|---|---|---|
| 1 — per-role pinning | Mission worker/validator model settings | Cannot test through this surface |
| 5 — rejection routing | A Mission with a validator stage that rejects | Cannot construct the scenario |
| 7 — usage attribution | One Mission run with mixed models | Zero-credit run attributes nothing |

Probe 5 is the one that matters most. PRD §8 already carries a contingency: if Missions cannot route a rejection back to retry or re-plan, Phase 3 is redesigned around a command-orchestrated state machine with Factory as the execution substrate, and **that redesign lands before Phase 2 starts**. A mission surface that does not execute at all is a stronger trigger for that branch than the one §8 anticipated.

Probes 2, 3, 4, and 6 do not require a Mission and remain reachable. Probe 4 in particular is unaffected.

## The exit code is the interesting part

Zero turns is a bug. **Exit 0 on zero turns is the finding.**

A run that performs no work and reports success is the exact failure mode PRD invariant #7 exists to prevent, and the same one Probe 2 was written to catch in the model-fallback path:

> Silent degradation is worse than no gate, because it still produces a green check.

Any gate built on "the mission completed" is vacuous against this behavior. An orchestrator that trusts the exit code would mark a chunk complete having executed nothing, and the zero-credit reading means a cost-based sanity check would not catch it either. Whatever consumes mission results must assert on turns and token usage, not on exit status alone.

This is worth raising with Factory independently of whether this project continues.

## Reproduction gaps

The repo standard in [`../README.md`](../README.md) requires raw output, resolved model IDs, and a re-runnable record. This record does not yet meet it. Outstanding:

- **No raw stdout/stderr.** The four signals above are transcribed from an operator observation, not captured here. Attach the raw JSON result.
- **No resolved model ID.** `claude-opus-5` is the *requested* model. What actually resolved is unknown, and unknown provenance cannot satisfy a family constraint (PRD §4).
- **Working directory not recorded.** Mission behavior may depend on repo context; unknown whether this was run inside a repo.
- **Prompt handling unclear.** The command as recorded carries no prompt argument. Whether one was supplied by stdin, by a mission config file, or not at all is undetermined, and "no prompt" would be an ordinary explanation for zero turns rather than a bug.

That last gap is the one that could overturn the finding. Resolve it before this is cited anywhere.

## Next

1. Re-run with output captured to this directory, working directory and prompt handling recorded explicitly.
2. Settle the no-prompt question. If a prompt was supplied and turns were still zero, the finding stands and hardens.
3. If it stands, treat PRD §8's Probe 5 contingency as triggered and decide the Mission-native vs command-orchestrated branch at the Phase 0 gate.
4. Continue with Probe 4, which this does not block.
