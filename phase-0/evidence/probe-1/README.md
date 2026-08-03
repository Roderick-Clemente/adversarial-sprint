# Probe 1 — Per-role model pinning

**Status:** BLOCKED. Probe 1 is not answered, and could not be reached.
**Date:** 2026-08-02
**CLI under test:** `droid` 0.186.0
**Recorded by:** Factory Droid, from an operator-reported reproduction. Raw stdout/stderr is not yet captured in this directory — see [Reproduction gaps](#reproduction-gaps).

## Finding

`droid exec --mission` performs no work and reports success at 0.186.0.

```
cd /tmp/mission-probe          # fresh git repo, README.md committed
droid exec --mission --auto high --model claude-opus-5 "Add a one-line comment to README.md"
```

| Signal | Observed |
|---|---|
| `numTurns` | 0 |
| `input_tokens` | 0 |
| `credits` | 0 |
| exit code | 0 |

A concrete, achievable task was supplied as a positional prompt, in a real git repository, at the autonomy level required to perform it. Zero turns followed, and the process exited successfully.

No worker or validator model flags were involved. This is the plainest mission invocation that could be expected to do something, which is what makes it a blocker rather than a misconfiguration on our side.

### The empty-invocation explanation is ruled out

`droid exec --help` declares the prompt as an *optional* positional (`droid exec [options] [prompt]`), so a prompt-less invocation is legal and would be an unremarkable reason to see zero turns. That is not what happened here: a prompt was present, the working directory was a git repo with a committed `README.md`, and `--auto high` cleared the permission tier needed to edit it. The benign reading does not survive the actual invocation.

### Two details from the CLI contract

- **`--model claude-opus-5` was a no-op.** `-m, --model` already defaults to `claude-opus-5` at 0.186.0. The requested model was the default, not an unusual or possibly-unavailable ID, which removes model resolution failure as an explanation for zero turns.
- **The per-role pinning flags exist.** `--worker-model`, `--validator-model`, and matching `--*-reasoning-effort` options are present and documented as "only valid with `--mission`". So Probe 1's surface *is* expressible on this version. What is untested is whether those flags resolve to the models named, because the mission that would exercise them does not run.

That distinction is the accurate summary of Probe 1 right now: **the surface exists; it could not be exercised.**

## Why this does not answer Probe 1

Probe 1 asks whether distinct models can be pinned to planner, reviewer, worker, and validator roles. The intended test routes through a Mission with distinct worker and validator model settings. If the mission surface does not execute, there is nothing to pin models *to*, and a pinning test run through it would return a meaningless pass: zero turns consume zero models, so any assertion about which model ran is vacuously satisfiable.

Recording this as "Probe 1: no" would be wrong. The accurate statement is that the execution substrate Probe 1 depends on did not run, so the capability question is still open.

## Blast radius

Three probes route through a working Mission, and all three are blocked by the same root cause:

| Probe | Dependency on Missions | Effect |
|---|---|---|
| 1 — per-role pinning | Mission worker/validator model settings | Flags exist, cannot be exercised |
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

The repo standard in [`../README.md`](../README.md) requires raw output, resolved model IDs, and a re-runnable record. This record does not yet meet it.

| Gap | Status |
|---|---|
| Prompt handling | **Closed.** Positional prompt supplied, quoted above |
| Working directory | **Closed.** `/tmp/mission-probe`, fresh git repo, `README.md` committed |
| Model availability | **Closed.** Requested ID is the version default |
| Raw stdout/stderr | **Open.** Four signals transcribed from operator observation, not captured here |
| Resolved model ID | **Open.** `claude-opus-5` is what was *requested*. What resolved is unrecorded, and unknown provenance cannot satisfy a family constraint (PRD §4) |

Neither open gap undermines the finding. Both are needed before it is cited externally.

## Next

1. **Re-run with raw output captured** to this directory, recording the resolved model ID rather than the requested one.
2. **Assert on the side effect, not the counter.** The strongest evidence here is that `README.md` was never modified. That is an observable outcome, which is the standard the PRD holds executors to; `numTurns: 0` is the system reporting on itself.
3. **Isolate mission mode.** Run the identical prompt, cwd, and autonomy level *without* `--mission`. If plain `droid exec` completes the edit and the mission variant does not, the defect is mission-specific and the finding hardens to its strongest form. If both no-op, the problem is broader than Missions and Probe 4 planning should account for it.
4. If it holds, treat PRD §8's Probe 5 contingency as triggered and decide the Mission-native vs command-orchestrated branch at the Phase 0 gate.
5. Continue with Probe 4, which this does not block.
