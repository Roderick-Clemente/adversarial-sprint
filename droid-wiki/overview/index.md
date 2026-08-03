# Adversarial Sprint

A specification and feasibility-evidence repository for a Factory plugin that runs multi-model adversarial planning, execution, and validation for agentic coding.

There is no application code here yet, and that is deliberate. The repository is currently a **build gate**: a full product spec (`PRD.md`), the canonical sprint method it packages (`templates/SPRINT-PLANNING-TEMPLATE.md`), and a set of executed probes that test whether the platform can actually enforce what the spec assumes. Plugin directories (`droids/`, `skills/`, `schemas/`, `scripts/`) get created once the probes say the design is buildable, not before.

## The idea

Quality in agentic coding does not come from a smarter model. It comes from **structural separation of roles across different model families**, with expensive thinking front-loaded into planning, and executable evidence — not self-assessment — deciding whether work is done.

Four properties carry the method, and all four are meant to be enforced rather than suggested:

1. **Family separation.** The plan reviewer is not the planner's family; the validator is not the executor's family. Two passes from one model family are one opinion twice.
2. **Fresh review context.** The validator sees the approved spec, the diff, read-only repository state, and test evidence. It never sees the executor's reasoning.
3. **Independent test authorship.** The executor cannot write or modify the tests that judge it. Locked by content hash, enforced by a hook.
4. **Valid RED before GREEN.** Behavior-changing work cannot start until the intended assertion has run and failed *for the expected reason*. A syntax error is not a RED.

The full set of eight runtime invariants is in [Invariants](../method/invariants.md).

## Roadmap

The north star is a **replayable demo of the method on one bounded pilot change**, with the manual harness at Phase 0.5 as the honest comparison arm.

| Phase | What it delivers | Status |
|---|---|---|
| **0 — Feasibility spike** | Eight probes and a go/no-go on Factory capabilities | **Done, GO** |
| **0.5 — Manual baseline harness** | The smallest honest two-CLI harness; the §13 comparison arm and Act 1 of the demo | Not started |
| **1 — Test-evidence slice** | Valid-RED classification, test locking, RED → GREEN on the pilot | Not started |
| **2 — Adversarial planning slice** | Blind plan review, bounded reconciliation, human decision packets | Not started |
| **3 — Factory end-to-end** | The full loop on one pilot change, plus a replayable demo and the baseline comparison | Not started |
| **4 — Generalize** | A second stack and a portable Claude/Codex runtime | Not started |

**Only Phase 0 has been built.** Everything from 0.5 onward is specified in `PRD.md` §11 and has not been started. No code exists for any of it, and the repository contains no partial implementation of a later phase.

Each phase carries written exit criteria in `PRD.md` §11. A phase is finished when those are met, not when it looks finished, which is the same standard the probe records hold themselves to.

Phase 0.5 is the one most easily misread as optional. It is the baseline arm the §13 evaluation already requires, and the PRD is explicit that it must not be strawmanned: if a two-CLI shell harness turns out to be nearly as good as the plugin, that is a finding worth having before a demo rather than during one.

> Not to be confused with the sprint method's own three phases, GROK, CHUNK and EXECUTE, which are stages *within* a single sprint rather than stages of this project. Those are described in [Workflow](../method/workflow.md) and [Sprint template](../method/sprint-template.md).

## Current status

**Phase 0 is complete and the verdict is GO, with one mandatory design change:** build it command-orchestrated rather than Mission-native. See `phase-0/GO-NO-GO.md`, summarised in [Findings](../findings/index.md).

A probe is a **Phase-0-only device**: one feasibility question aimed at the platform, used solely to decide the build gate. Later phases deliver vertical slices measured against exit criteria, not probes. The project is not made of probes, and the eight below are scaffolding for the decision rather than the product.

| Probe | Question | Verdict |
|---|---|---|
| [1](../probes/probe-1-model-pinning.md) | Per-role model pinning | **BLOCKED** — `droid exec --mission` is a no-op that reports success |
| [2](../probes/probe-2-fallback-safety.md) | Fallback safety | **CONDITIONAL PASS** — family gate works; found a silent reasoning downgrade |
| [3](../probes/probe-3-context-isolation.md) | Custom Droid context isolation | **PASS / GAP** — tools genuinely restricted; transcript readable off disk |
| [4](../probes/probe-4-hook-blocking.md) | Deterministic hook blocking | **PASS** (conditional) — overturned an earlier BLOCKED verdict |
| 5 | Rejection routing | Unreached — blocked by Probe 1 |
| [6](../probes/probe-6-plugin-boundary.md) | Plugin distribution boundary | **PASS** — droid, skill and hook ship as one install |
| 7 | Usage attribution | Partially unblocked by Probe 2 |
| [8](../probes/probe-8-self-declared-risk.md) | Self-declared risk as a policy input | **PASS with caveat** — the tier gates on a self-report |

Every verdict is scoped to `droid` **0.186.0** on macOS. A version-less result cannot be rechecked later, so each probe record carries the CLI version, and a CLI upgrade invalidates the go/no-go until the probes are re-run.

## The single most important finding

**The platform cannot fail loudly.** Four independent probes hit the same shape:

- a mission that performs no work and exits 0 ([Probe 1](../probes/probe-1-model-pinning.md))
- a hook registered in the documented location that is never loaded ([Probe 4](../probes/probe-4-hook-blocking.md))
- a model silently downgraded from maximum reasoning to none ([Probe 2](../probes/probe-2-fallback-safety.md))
- a run whose every tool call was denied, still exiting 0 with a plausible answer ([Probe 2](../probes/probe-2-fallback-safety.md))

That failure mode is documented in [Silent green](../findings/silent-green.md), and it is the reason the design centres on [one reference guard](../findings/reference-guard.md) that inspects reality instead of trusting configuration.

## Where to start

| If you want to | Read |
|---|---|
| See where the project is going | [Roadmap](#roadmap), then `PRD.md` §11 for exit criteria |
| Understand the method being packaged | [Method](../method/index.md) → [Workflow](../method/workflow.md) |
| Know what the platform can actually enforce | [Findings](../findings/index.md) |
| Re-run a probe and check a claim yourself | [Getting started](./getting-started.md) |
| See how the pieces fit together | [Architecture](./architecture.md) |
| Look up a term | [Glossary](./glossary.md) |
| Contribute, as a human or an agent | [How to contribute](../how-to-contribute/index.md) |

## A note on scope and honesty

The repository makes no claim to be a correctness oracle. Different model families are an independence control, not proof. Tests are executable evidence, not truth. Two reviewers agreeing means no known dispute and nothing more.

The same standard applies to the probe records. Negative results get the same treatment as positive ones, an overturned verdict is kept alongside its correction rather than quietly edited, and unmeasured things are listed as unmeasured. See [Patterns and conventions](../how-to-contribute/patterns-and-conventions.md) for how that standard is applied in practice.
